"""Homepage for Streamlit dashboard"""
import streamlit as st
import altair as alt
import pandas as pd
from utils.database import get_connection_to_db
from psycopg2.extras import RealDictCursor


def generate_demand_graph(db_cursor):
    """Generate demand"""
    db_cursor.execute("SELECT * FROM demands")
    demand = db_cursor.fetchall()
    demand_df = pd.DataFrame(demand)
    demand_df.drop(columns=['demand_id'], inplace=True)
    demand_df['demand_at'] = pd.to_datetime(
        demand_df['demand_at'], utc=True)

    st.title("Energy Monitor Dashboard")
    st.write("Welcome! Use the sidebar to navigate between dashboards.")
    st.area_chart(demand_df, x='demand_at', y='total_demand')


def generate_price_graph(db_cursor):
    """Generate price"""
    db_cursor.execute("SELECT * FROM prices")
    price = db_cursor.fetchall()
    price_df = pd.DataFrame(price)
    price_df.drop(columns=['price_id'], inplace=True)
    price_df['price_at'] = pd.to_datetime(
        price_df['price_at'], utc=True)

    price_df['price_per_mwh'] = pd.to_numeric(
        price_df['price_per_mwh'])

    print(price_df)
    st.line_chart(price_df, x='price_at', y='price_per_mwh')


def generate_energy_generation_graph(db_cursor):
    """Generate price"""
    db_cursor.execute(
        """
        WITH Latest_gen_data AS (
            SELECT gd.fuel_type_id, gd.mw_generated, gd.generation_at
            FROM generations gd
            INNER JOIN(
                SELECT fuel_type_id, MAX(generation_at) AS latest_time
                FROM generations
                GROUP BY fuel_type_id
            ) latest ON gd.fuel_type_id = latest.fuel_type_id AND gd.generation_at = latest.latest_time
            WHERE gd.mw_generated > 0
        )
        SELECT * FROM Latest_gen_data JOIN fuel_types USING(fuel_type_id);
        """)
    price = db_cursor.fetchall()
    price_df = pd.DataFrame(price)
    price_df['generation_at'] = pd.to_datetime(
        price_df['generation_at'], utc=True)

    print(price_df)
    st.write(
        alt.Chart(price_df).mark_arc().encode(
            theta="mw_generated",
            color="fuel_type_name"
        )
    )


def main():
    """Main method for running dashboard"""
    db_conn = get_connection_to_db()
    db_cursor = db_conn.cursor(cursor_factory=RealDictCursor)

    generate_demand_graph(db_cursor)
    generate_price_graph(db_cursor)
    generate_energy_generation_graph(db_cursor)


if __name__ == '__main__':
    print("Hi")
    main()

"""
WITH Latest_gen_data AS (
    SELECT gd.fuel_type_id, gd.mw_generated, gd.generation_at
    FROM generations gd
    INNER JOIN(
        SELECT fuel_type_id, MAX(generation_at) AS latest_time
        FROM generations
        GROUP BY fuel_type_id
    ) latest ON gd.fuel_type_id = latest.fuel_type_id AND gd.generation_at = latest.latest_time
)
SELECT * FROM Latest_gen_data JOIN fuel_types USING(fuel_type_id);
"""
