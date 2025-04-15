import os
import logging
from typing import Tuple, Optional, Any
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import connection as Connection, cursor as Cursor
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')


def connect_to_db() -> Tuple[Connection, Cursor]:
    """
    Establish a connection to the PostgreSQL database.
    """
    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = connection.cursor()
    return connection, cursor


def check_if_outage_exists(cursor: Cursor, reference_id: str) -> bool:
    """
    Check if an outage_id already exists in the database.
    """
    query = sql.SQL(
        "SELECT EXISTS(SELECT 1 FROM outages WHERE reference_id = %s);")
    cursor.execute(query, (reference_id,))
    result = cursor.fetchone()
    return result[0]


def get_provider_id(cursor: Cursor, provider_name: str) -> None:
    """
    Get the provider_id based on the provider_name from the providers table.
    """
    query = sql.SQL(
        "SELECT provider_id FROM providers WHERE provider_name = %s;")
    cursor.execute(query, (provider_name,))
    result = cursor.fetchone()

    if result:
        return result[0]
    return None


def insert_outage_data(cursor: Cursor,
                       connection: Connection,
                       reference_id: str,
                       outage_start: Optional[Any],
                       outage_end: Optional[Any],
                       provider_id: Any,
                       planned: Optional[bool]
                       ) -> None:
    """
    Insert a new outage record into the database.
    """
    query = sql.SQL("""
        INSERT INTO outages (reference_id, outage_start, outage_end, provider_id, planned)
        VALUES (%s, %s, %s, %s, %s);
    """)
    cursor.execute(query, (reference_id, outage_start,
                           outage_end, provider_id, planned))
    connection.commit()


def convert_planned_to_bool(planned: Any) -> Optional[bool]:
    """
    Convert the 'planned' column to a boolean value.
    """
    if isinstance(planned, bool):
        return planned
    elif pd.isnull(planned) or planned.lower() == 'na':
        return None
    elif planned.lower() == 'true':
        return True
    elif planned.lower() == 'false':
        return False
    else:
        return None


def upload_data_from_csv(csv_file: str) -> None:
    """
    Upload the cleaned data from the CSV file to the RDS Postgres database.
    """
    logging.info(
        "Starting the upload process from CSV file: %s", csv_file)

    try:
        df = pd.read_csv(csv_file)
        logging.info(
            "CSV file %s read successfully, %s rows found.", csv_file, len(df))
    except Exception as e:
        logging.error(
            "Error reading the CSV file %s: %s", csv_file, e)
        return

    connection, cursor = connect_to_db()

    logging.info("Connected to the database.")

    for _, row in df.iterrows():
        reference_id = row['reference_id']

        outage_start = row['outage_start'] if pd.notnull(
            row['outage_start']) else None
        outage_end = row['outage_end'] if pd.notnull(
            row['outage_end']) else None
        provider_name = row['Provider_name'] if pd.notnull(
            row['Provider_name']) else 'NA'
        planned = convert_planned_to_bool(row['planned'])

        provider_id = get_provider_id(cursor, provider_name)

        if provider_id is None:
            logging.warning(
                "Provider '%s' not found in the database.", provider_name)
            provider_id = 'NA'

        if not check_if_outage_exists(cursor, reference_id):
            logging.info(
                "Inserting outage data for reference_id: %s", reference_id)
            insert_outage_data(cursor, connection, reference_id,
                               outage_start, outage_end, provider_id, planned)
        else:
            logging.info(
                "Outage with reference_id %s already exists, skipping insertion.", reference_id)

    cursor.close()
    connection.close()
    logging.info("Database connection closed. Data upload process completed.")


if __name__ == "__main__":
    upload_data_from_csv('clean_power_outage_data.csv')
