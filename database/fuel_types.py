"""Script to find different fuel types from API and insert into fuel_types table in database"""
import os
import logging
import requests
import psycopg2
from dotenv import load_dotenv


URL = "https://data.elexon.co.uk/bmrs/api/v1/reference/fueltypes/all"


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


def get_fuel_types_from_api(url: str) -> list[str]:
    """Retrieving all fuel types from API"""
    response = requests.get(url, timeout=10)
    data = response.json()

    return data


def insert_fuel_types_into_db(fuel_types: list[str], conn: 'Connection'):
    """Inserting fuel types into fuel_type table in energy database"""
    query = """INSERT INTO fuel_types (fuel_type) VALUES (%s)"""
    curr = conn.cursor()

    fuel_types_tuple = [(fuel_type, ) for fuel_type in fuel_types]
    try:
        curr.executemany(query, fuel_types_tuple)
        conn.commit()
        logging.info(
            'Inserted %s fuel types into the fuel_type table', len(fuel_types_tuple))
    except psycopg2.Error as error:
        logging.info('Error: %s', error)
        conn.rollback()
    finally:
        curr.close()
        conn.close()
    logging.info('Connection closed')


if __name__ == "__main__":
    connection = get_connection_to_db()
    fuels = get_fuel_types_from_api(URL)
    insert_fuel_types_into_db(fuels, connection)
