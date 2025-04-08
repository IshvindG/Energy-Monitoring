"""Load script to add data to the database"""
import os
import logging
import csv
import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection, cursor
from dotenv import load_dotenv

load_dotenv()
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
logger = logging.getLogger()


def get_connection() -> connection:
    """Return a connection to the databse"""
    db_conn = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    return db_conn


def get_cursor(db_conn: connection) -> cursor:
    """Get cursor for database"""
    db_cursor = db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return db_cursor


def load_energy_generation_data(data: list[dict]) -> None:
    """Load energy generation data into the database"""

    logger.info("Loading energy data into database")
    db_conn = get_connection()
    db_cursor = get_cursor(db_conn)

    rows = [(row.get('generation'), row.get('fuelType'),
             row.get('publishTime')) for row in data]
    statement = """
    INSERT INTO generations (mw_generated, fuel_type_id, generation_at)
    VALUES (%s, (SELECT fuel_type_id FROM fuel_types WHERE fuel_type = %s), %s)"""
    try:
        db_cursor.executemany(statement, (rows))
        db_conn.commit()
    except (psycopg2.Error) as db_error:
        logging.error('Load failed - %s', db_error)
    finally:
        db_cursor.close()
        db_conn.close()


def load_market_price_data(data: list[dict]) -> None:
    """Load market data into database"""

    logger.info("Loading market data into database")
    db_conn = get_connection()
    db_cursor = get_cursor(db_conn)

    row = (data[0].get('startTime'), data[0].get(
        'price'))
    statement = """
    INSERT INTO prices (price_at, price_per_mwh)
    VALUES (%s, %s)"""
    try:
        db_cursor.execute(statement, row)
        db_conn.commit()
    except (psycopg2.Error) as db_error:
        logging.error('Load failed - %s', db_error)
    finally:
        db_cursor.close()
        db_conn.close()


def load_energy_demand_data(data: list[dict]) -> None:
    """Load demand data into database"""
    logger.info("Loading demand data into database")
    db_conn = get_connection()
    db_cursor = get_cursor(db_conn)

    row = (data[0].get('startTime'), data[0].get(
        'demand'))
    statement = """
    INSERT INTO demands (demand_at, total_demand)
    VALUES (%s, %s)"""
    try:
        db_cursor.execute(statement, row)
        db_conn.commit()
    except (psycopg2.Error) as db_error:
        logging.error('Load failed - %s', db_error)
    finally:
        db_cursor.close()
        db_conn.close()


def load_csv(filename: str) -> list:
    """Take a file and load a list of rows from it"""

    with open(filename, encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = list(reader)
    return data


if __name__ == '__main__':
    db_connection = get_connection()
    db_cur = get_cursor(db_connection)

    energy_generation_data = load_csv('data/energy_generation_cleaned.csv')
    load_energy_generation_data(energy_generation_data)

    market_price_data = load_csv('data/market_price_cleaned.csv')
    print(market_price_data)
    load_market_price_data(market_price_data)

    demand_data = load_csv('data/energy_demand_cleaned.csv')
    print(demand_data)
    load_energy_demand_data(demand_data)

    db_cur.close()
    db_connection.close()
