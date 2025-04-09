import pandas as pd
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')


def connect_to_db():
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


def check_if_outage_exists(cursor, reference_id):
    """
    Check if an outage_id already exists in the database.
    """
    query = sql.SQL(
        "SELECT EXISTS(SELECT 1 FROM outages WHERE reference_id = %s);")
    cursor.execute(query, (reference_id,))
    result = cursor.fetchone()
    return result[0]


def get_provider_id(cursor, provider_name):
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


def insert_outage_data(cursor, connection, reference_id, outage_start, outage_end, provider_id, planned):
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


def convert_planned_to_bool(planned):
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


def upload_data_from_csv(csv_file):
    """
    Upload the cleaned data from the CSV file to the RDS Postgres database.
    """
    df = pd.read_csv(csv_file)

    connection, cursor = connect_to_db()

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
            print(
                f"Warning: Provider '{provider_name}' not found in the database.")
            provider_id = 'NA'

        if not check_if_outage_exists(cursor, reference_id):
            insert_outage_data(cursor, connection, reference_id,
                               outage_start, outage_end, provider_id, planned)

    cursor.close()
    connection.close()


if __name__ == "__main__":
    upload_data_from_csv('clean_power_outage_data.csv')
