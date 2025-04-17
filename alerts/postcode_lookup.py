"""Script that maps a postcode to a specific region, and finds the related provider in the db"""
import os
import logging
import requests
import psycopg2
from dotenv import load_dotenv


REGION_MAPPINGS = {
    "Scotland": "Scotland",
    "North East": "North East England",
    "North West": "North West England",
    "Yorkshire and The Humber": "Yorkshire",
    "West Midlands": "West Midlands",
    "East Midlands": "East Midlands",
    "Eastern": "East England",
    "London": "London",
    "South East": "South East England",
    "South West": "South West England",
    "South Wales": "Wales",
    "North Wales": "Wales",
    "Wales": "Wales"
}


def enable_logging() -> None:
    """Enables logging at INFO level"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )


def get_connection_to_db():
    """Gets a psycopg2 connection to the energy database"""
    load_dotenv()
    return psycopg2.connect(host=os.getenv("DB_HOST"),
                            database=os.getenv("DB_NAME"),
                            user=os.getenv("DB_USER"),
                            password=os.getenv("DB_PASSWORD"),
                            port=os.getenv("DB_PORT"))


def get_region_from_postcode(postcode: str) -> str:
    """Finding associated region from a given postcode"""
    url = f"https://api.postcodes.io/postcodes/{postcode}"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise ValueError("Invalid postcode or API failure")

    data = response.json()
    electoral_region = data['result']['european_electoral_region']
    region = REGION_MAPPINGS.get(electoral_region)

    if not region:
        raise ValueError(
            f"No matching region for electoral region: {electoral_region}")

    return region


def find_provider_from_region(cursor: 'Cursor', region: str) -> int:
    """Finding a provider from a region name"""
    query = """SELECT provider_id
                FROM region_provider
                WHERE region_name = %s"""
    try:
        cursor.execute(query, (region, ))
        result = cursor.fetchall()

        provider_id = result[0][0]

        return provider_id
    except Exception as e:
        raise ValueError('Provider not found') from e


def find_provider_from_region_id(cursor: 'Cursor', region_id: int) -> int:
    """Finding a provider from region id"""
    query = """SELECT provider_id, region_name
                FROM region_provider
                WHERE region_id = %s"""
    try:
        cursor.execute(query, (region_id, ))
        result = cursor.fetchall()

        provider_id = result[0][0]
        region_name = result[0][1]

        return provider_id, region_name
    except Exception as e:
        raise ValueError('Provider not found') from e


if __name__ == "__main__":
    db_connection = get_connection_to_db()
    curr = db_connection.cursor()
    user_provider, user_region = find_provider_from_region_id(curr, 18)
    print(user_provider)
    print(user_region)
