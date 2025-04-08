"""Script to find different fuel types from API and insert into fuel_types table in database"""
import os
import logging
import requests
import psycopg2
from dotenv import load_dotenv


FUEL_TYPES_URL = "https://data.elexon.co.uk/bmrs/api/v1/reference/fueltypes/all"
INTERCONNECTOR_URL = "https://data.elexon.co.uk/bmrs/api/v1/reference/interconnectors/all"


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


def fuel_type_name_mapping() -> dict:
    """Mapping fuel type abbreviations to their fuel type names"""
    fuel_type_names = {
        "CCGT": "Combined Cycle Gas Turbine",
        "OCGT": "Open Cycle Gas Turbine",
        "PS": "Pumped Storage",
        "NPSHYD": "Hydro (Non-Pumped Storage)"
    }

    return fuel_type_names


def get_interconnector_data_from_api(url: str) -> list[dict]:
    """Retrieving interconnector name data from api"""
    response = requests.get(url, timeout=10)
    data = response.json()
    interconnector_data = []
    for interconnector in data:

        interconnector_info = {
            'ID': interconnector.get('interconnectorId'),
            'Name': interconnector.get('interconnectorName')
        }

        interconnector_data.append(interconnector_info)

    return interconnector_data


def interconnector_map(interconnector_data: list[dict]) -> dict:
    """Mapping interconnector names to their ids"""
    interconnector_mapping = {
        item["ID"]: item["Name"] for item in interconnector_data
    }

    return interconnector_mapping


def merge_fuel_type_and_name_data(fuel_types: list[str],
                                  interconnector_mapping: dict, fuel_names: dict) -> list[tuple]:
    """Generate fuel data with fuel_type_name by checking interconnector or manual mappings"""
    fuel_data = []
    for fuel_type in fuel_types:
        if fuel_type in interconnector_mapping:
            fuel_type_name = interconnector_mapping[fuel_type]
        elif fuel_type in fuel_names:
            fuel_type_name = fuel_names[fuel_type]
        else:
            fuel_type_name = fuel_type.title()
        fuel_data.append((fuel_type, fuel_type_name))

    return fuel_data


def insert_fuel_type_and_name_data_into_db(fuel_types: list[str], interconnector_mapping: dict,
                                           fuel_names: dict, conn: 'Connection'):
    """Inserting both fuel types and interconnector names into fuel_types table in one go"""
    query = """INSERT INTO fuel_types (fuel_type, fuel_type_name) VALUES (%s, %s)"""
    curr = conn.cursor()

    fuel_data = merge_fuel_type_and_name_data(
        fuel_types, interconnector_mapping, fuel_names)

    try:
        curr.executemany(query, fuel_data)
        conn.commit()
        logging.info(
            'Inserted %s fuel types and their names into the fuel_type table', len(fuel_data))
    except psycopg2.Error as error:
        logging.error(
            'Error inserting fuel types into the database: %s', error)
        conn.rollback()
    finally:
        curr.close()
        logging.info("Cursor closed")


if __name__ == "__main__":
    enable_logging()
    connection = get_connection_to_db()
    try:
        fuels = get_fuel_types_from_api(FUEL_TYPES_URL)
        interconnectors = get_interconnector_data_from_api(INTERCONNECTOR_URL)
        int_mapping = interconnector_map(interconnectors)
        fuel_names_map = fuel_type_name_mapping()
        insert_fuel_type_and_name_data_into_db(
            fuels, int_mapping, fuel_names_map, connection)
    finally:
        connection.close()
        logging.info("Main: DB connection closed.")
