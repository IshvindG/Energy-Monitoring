import os
import logging
import pandas as pd
import psycopg2
from typing import Dict, Tuple
from dotenv import load_dotenv
from psycopg2.extensions import connection as Connection, cursor as Cursor

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

REGION_NAME_MAP = {
    "North Wales and Merseyside": "North Wales & Merseyside",
}


def connect_to_db() -> Tuple[Connection, Cursor]:
    """
    Establish connection to database
    """

    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()
        logging.info("Successfully connected to the database.")
        return connection, cursor
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        raise


def load_csv(file_path: str) -> pd.DataFrame:
    """
    Load the cleaned csv for upload
    """
    logging.info(f"Loading data from {file_path}.")
    return pd.read_csv(file_path)


def insert_carbon_intensities(df: pd.DataFrame, conn: Connection, cur: Cursor):
    """
    Inserts carbon intensity records into the database, mapping region_name to region_id
    and renaming columns as required.
    """
    for _, row in df.iterrows():
        try:

            region_name = REGION_NAME_MAP.get(
                row['region_name'], row['region_name'])

            cur.execute(
                "SELECT region_id FROM regions WHERE region_name = %s", (region_name,))

            result = cur.fetchone()

            if result is None:
                logging.warning(
                    f"Region not found in database: {row['region_name']}")
                continue

            region_id = result[0]

            cur.execute("""
                INSERT INTO carbon_intensities (index, forecast_measure, measure_at, region_id)
                VALUES (%s, %s, %s, %s)
            """, (
                row['index'],
                row['measure'],
                row['time_of_measure'],
                region_id
            ))

        except Exception as e:
            logging.error(f"Error inserting row: {row.to_dict()}, Error: {e}")

    conn.commit()
    logging.info("All data inserted into carbon_intensities table.")


if __name__ == "__main__":
    file_path = "/tmp/clean_live_co2.csv"
    df = load_csv(file_path)
    conn, cur = connect_to_db()
    insert_carbon_intensities(df, conn, cur)
    cur.close()
    conn.close()
