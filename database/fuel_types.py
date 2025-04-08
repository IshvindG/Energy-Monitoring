import requests
import psycopg2
import os
from dotenv import load_dotenv


URL = "https://data.elexon.co.uk/bmrs/api/v1/reference/fueltypes/all"


def get_connection_to_db():
    """Gets a pymssql connection to the short term MS SQL short-term DB"""
    load_dotenv()
    return psycopg2.connect(host=os.getenv("DB_HOST"),
                            database=os.getenv("DB_NAME"),
                            user=os.getenv("DB_USER"),
                            password=os.getenv("DB_PASSWORD"),
                            port=os.getenv("DB_PORT"))


def get_fuel_types_from_api(url: str) -> list[str]:

    response = requests.get(url)
    data = response.json()

    return data


def insert_fuel_types_into_db(fuel_types: list[str], conn: 'Connection'):

    query = """INSERT INTO fuel_types (fuel_type) VALUES (%s)"""
    curr = conn.cursor()

    for fuel_type in fuel_types:
        curr.execute(query, (fuel_type, ))
        conn.commit()
    conn.close()
    print(f"{len(fuel_types)} fuel types inserted into the fuel_type table")


if __name__ == "__main__":
    connection = get_connection_to_db()
    fuels = get_fuel_types_from_api(URL)
    insert_fuel_types_into_db(fuels, connection)
