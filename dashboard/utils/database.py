"""Common methods for connection to the database"""
import os
import psycopg2
from psycopg2.extensions import connection
from dotenv import load_dotenv


def get_connection_to_db() -> connection:
    """Gets a psycopg2 connection to the energy database"""
    load_dotenv()
    return psycopg2.connect(host=os.getenv("DB_HOST"),
                            database=os.getenv("DB_NAME"),
                            user=os.getenv("DB_USER"),
                            password=os.getenv("DB_PASSWORD"),
                            port=os.getenv("DB_PORT")
                            )
