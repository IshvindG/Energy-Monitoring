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
                WHERE updated_at BETWEEN %s AND %s
            """

    cursor.execute(query, (last_month, today))
    result = cursor.fetchone()[0]

    return round(result, 2)


def get_highest_price_over_past_month(cursor: 'Cursor', today: str, last_month: str):
    """Retrieving highest price of energy over the past month and corresponding date
    from database"""
    query = """SELECT price_per_mwh, price_at
                FROM prices
                WHERE updated_at BETWEEN %s AND %s
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
                WHERE updated_at BETWEEN %s AND %s
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
                WHERE updated_at BETWEEN %s AND %s"""

    cursor.execute(query, (last_month, today))
    result = cursor.fetchone()[0]

    return result


def get_average_demand_per_day_over_past_month(cursor: 'Cursor',
                                               today: str, last_month: str) -> float:
    """Retrieving average demand per day for energy over the past month from database"""
    query = """SELECT AVG(total_demand)
                FROM demands
                WHERE updated_at BETWEEN %s AND %s"""

    cursor.execute(query, (last_month, today))
    result = cursor.fetchone()[0]

    return round(result, 2)


def get_highest_demand(cursor: 'Cursor', today: str, last_month: str):
    """Retrieving highest demand recorded for energy in a day over the past 
    month from database"""
    query = """SELECT total_demand, demand_at
                FROM demands
                WHERE updated_at BETWEEN %s AND %s
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
                WHERE updated_at BETWEEN %s AND %s
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


def get_total_generation(cursor: 'Cursor', today: str, last_month: str) -> int:
    """Retrieving total energy generated"""

    query = """SELECT SUM(mw_generated)
                FROM generations
                WHERE updated_at BETWEEN %s AND %s"""

    cursor.execute(query, (last_month, today))
    result = cursor.fetchone()[0]

    return result


def get_total_renewable(cursor: 'Cursor', today: str, last_month: str) -> int:
    """Retrieving total renewable energy generated"""

    query = """SELECT SUM(mw_generated)
                FROM generations g
                JOIN fuel_types ft ON ft.fuel_type_id = g.fuel_type_id
                JOIN fuel_categories fc ON fc.fuel_category_id = ft.fuel_category_id
                WHERE g.updated_at BETWEEN %s AND %s
                AND fc.fuel_category = 'Renewables'"""

    cursor.execute(query, (last_month, today))
    result = cursor.fetchone()[0]

    return result


def get_average_carbon_intensity(cursor: 'Cursor', today: str, last_month: str) -> float:
    """Retrieving average carbon emissions over the past month"""

    query = """SELECT AVG(forecast_measure)
                FROM carbon_intensities
                WHERE measure_at BETWEEN %s AND %s"""

    cursor.execute(query, (last_month, today))
    result = cursor.fetchone()[0]

    return round(result, 2)


def get_region_with_best_avg_carbon_intensity(cursor: 'Cursor', today: str, last_month: str) -> str:
    """Retrieving region with the least carbon emissions"""

    query = """SELECT region_name, AVG(forecast_measure) AS avg_measure
                FROM carbon_intensities c
                JOIN regions r ON r.region_id = c.region_id
                WHERE measure_at BETWEEN %s AND %s
                GROUP BY region_name
                ORDER BY avg_measure ASC
                LIMIT 1"""

    cursor.execute(query, (last_month, today))

    result = cursor.fetchone()[0]

    return result


def get_region_with_worst_avg_carbon_intensity(cursor: 'Cursor', today: str, last_month: str) -> str:
    """Retrieving region with the most carbon emissions"""

    query = """SELECT region_name, AVG(forecast_measure) AS avg_measure
                FROM carbon_intensities c
                JOIN regions r ON r.region_id = c.region_id
                WHERE measure_at BETWEEN %s AND %s
                GROUP BY region_name
                ORDER BY avg_measure DESC
                LIMIT 1"""

    cursor.execute(query, (last_month, today))

    result = cursor.fetchone()[0]

    return result


def get_hour_with_best_avg_carbon_intensity(cursor: 'Cursor', today: str, last_month: str) -> datetime:
    """Retrieving the hour with the least carbon emissions"""

    query = """SELECT EXTRACT(HOUR FROM measure_at) AS hour_of_day, AVG(forecast_measure) AS avg_measure
                FROM carbon_intensities
                WHERE measure_at BETWEEN %s AND %s
                GROUP BY hour_of_day
                ORDER BY avg_measure ASC
                LIMIT 1"""

    cursor.execute(query, (last_month, today))
    result = cursor.fetchone()[0]

    return result


def get_hour_with_worst_avg_carbon_intensity(cursor: 'Cursor', today: str, last_month: str) -> datetime:
    """Retrieving the hour with the most carbon emissions"""

    query = """SELECT EXTRACT(HOUR FROM measure_at) AS hour_of_day, AVG(forecast_measure) AS avg_measure
                FROM carbon_intensities
                WHERE measure_at BETWEEN %s AND %s
                GROUP BY hour_of_day
                ORDER BY avg_measure DESC
                LIMIT 1"""

    cursor.execute(query, (last_month, today))
    result = cursor.fetchone()[0]

    return result


if __name__ == "__main__":

    db_connection = get_connection_to_db()
    curr = db_connection.cursor()
    date_today, date_last_month = get_dates()
    date_today = format_dates(date_today)
    date_last_month = format_dates(date_last_month)
    print(get_hour_with_worst_avg_carbon_intensity(
        curr, date_today, date_last_month))
