"""File for signing up to the alert system"""
import os
import logging
import streamlit as st
import psycopg2
from psycopg2.extensions import connection
from dotenv import load_dotenv
import pandas as pd


def get_connection_to_db() -> connection:
    """Gets a psycopg2 connection to the energy database"""
    load_dotenv()
    return psycopg2.connect(host=os.getenv("DB_HOST"),
                            database=os.getenv("DB_NAME"),
                            user=os.getenv("DB_USER"),
                            password=os.getenv("DB_PASSWORD"),
                            port=os.getenv("DB_PORT"))


def main() -> None:
    """Main method for dashboard"""
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )

    db_conn = get_connection_to_db()
    db_cursor = db_conn.cursor()

    db_cursor.execute("SELECT * FROM demands")
    demands = db_cursor.fetchall()

    st.write(demands)


if __name__ == '__main__':
    logging.info("Running Streamlit")
    main()
