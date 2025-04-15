"""Script that retrieves all the necessary data for the newsletter from the database"""
import os
import logging
from datetime import datetime, timedelta
import psycopg2
from dotenv import load_dotenv


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


def get_dates() -> datetime:
    """Returns dates for today and a month ago"""
    date_today = datetime.now()
    last_month_date = date_today - timedelta(days=30)

    return date_today, last_month_date


def format_dates(date: datetime) -> str:
    """Formatting any date to desired string"""
    date_formatted = date.strftime("%Y-%m-%d %H:%M:%S")

    return date_formatted


def get_average_price_over_past_month(cursor: 'Cursor', today: str, last_month: str):
    """Retrieving average price of energy over the past month from database"""
    query = """SELECT AVG(price_per_mwh) AS price_average
                FROM prices
                WHERE price_at BETWEEN %s AND %s
            """

    cursor.execute(query, (last_month, today))
    result = cursor.fetchone()[0]

    return round(result, 2)


def get_highest_price_over_past_month(cursor: 'Cursor', today: str, last_month: str):
    """Retrieving highest price of energy over the past month and corresponding date
    from database"""
    query = """SELECT price_per_mwh, price_at
                FROM prices
                WHERE price_at BETWEEN %s AND %s
                ORDER BY price_per_mwh DESC
                LIMIT 1"""

    cursor.execute(query, (last_month, today))
    result = cursor.fetchone()
    highest_price, date_of_highest_price = result

    return round(float(highest_price), 2), format_dates(date_of_highest_price)


def get_lowest_price_over_past_month(cursor: 'Cursor', today: str, last_month: str) -> str:
    """Retrieving lowest price of energy over the past month with corresponding date
    from database"""

    query = """SELECT price_per_mwh, price_at
                FROM prices
                WHERE price_at BETWEEN %s AND %s
                ORDER BY price_per_mwh ASC
                LIMIT 1"""

    cursor.execute(query, (last_month, today))
    result = cursor.fetchone()
    lowest_price, date_of_lowest_price = result

    return str(lowest_price), format_dates(date_of_lowest_price)


def get_total_demand_over_past_month(cursor: 'Cursor', today: str, last_month: str) -> int:
    """Retrieving total demand for energy over the past month from database"""
    query = """SELECT SUM(total_demand)
                FROM demands
                WHERE demand_at BETWEEN %s AND %s"""

    cursor.execute(query, (last_month, today))
    result = cursor.fetchone()[0]

    return result


def get_average_demand_per_day_over_past_month(cursor: 'Cursor',
                                               today: str, last_month: str) -> float:
    """Retrieving average demand per day for energy over the past month from database"""
    query = """SELECT AVG(total_demand)
                FROM demands
                WHERE demand_at BETWEEN %s AND %s"""

    cursor.execute(query, (last_month, today))
    result = cursor.fetchone()[0]

    return round(result, 2)


def get_highest_demand(cursor: 'Cursor', today: str, last_month: str):
    """Retrieving highest demand recorded for energy in a day over the past 
    month from database"""
    query = """SELECT total_demand, demand_at
                FROM demands
                WHERE demand_at BETWEEN %s AND %s
                ORDER BY total_demand DESC
                LIMIT 1"""

    cursor.execute(query, (last_month, today))
    result = cursor.fetchone()

    highest_demand, highest_demand_date = result

    return highest_demand, format_dates(highest_demand_date)


def get_lowest_demand(cursor: 'Cursor', today: str, last_month: str):
    """Retrieving highest demand for energy in a day over the past month 
    from database"""
    query = """SELECT total_demand, demand_at
                FROM demands
                WHERE demand_at BETWEEN %s AND %s
                ORDER BY total_demand ASC
                LIMIT 1"""

    cursor.execute(query, (last_month, today))
    result = cursor.fetchone()

    lowest_demand, lowest_demand_date = result

    return lowest_demand, format_dates(lowest_demand_date)


def get_average_demand_historical(cursor: 'Cursor'):
    """Retrieving average demand for energy per day over the past month from database"""
    query = """SELECT AVG(total_demand)
                FROM demands"""

    cursor.execute(query)
    result = cursor.fetchone()[0]

    return round(result, 2)
