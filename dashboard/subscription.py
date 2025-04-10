"""File for signing up to the alert system"""
import os
import streamlit as st
import psycopg2
from psycopg2.extensions import connection
from dotenv import load_dotenv
from utils.api import submit_form


def get_connection_to_db() -> connection:
    """Gets a psycopg2 connection to the energy database"""
    load_dotenv()
    return psycopg2.connect(host=os.getenv("DB_HOST"),
                            database=os.getenv("DB_NAME"),
                            user=os.getenv("DB_USER"),
                            password=os.getenv("DB_PASSWORD"),
                            port=os.getenv("DB_PORT"))


def execute_query(conn: connection, query: str) -> list[str]:
    """Execute a query on the database"""
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def get_region_data(conn: connection) -> list[str]:
    """Get Region data from the database"""
    cursor = conn.cursor()

    query = """SELECT region_name FROM regions;"""
    cursor.execute(query)
    result = cursor.fetchall()
    region_data = []

    for region in result:
        region_data.append(region[0])

    return region_data


def get_provider_data(conn: connection) -> list[str]:
    """Get Provider data from the database"""
    cursor = conn.cursor()

    query = """SELECT provider_name FROM providers;"""
    cursor.execute(query)
    result = cursor.fetchall()
    provider_data = []
    for provider in result:
        provider_data.append(provider[0])
    return provider_data


def newsletter_form(regions: list[str], providers: list[str]):
    """Display Newsletter subscription form"""

    st.header("Subscribe to Newsletter")
    with st.form("newsletter_form"):
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        region = st.selectbox("Region", regions)
        postcode = st.text_input("Postcode")
        provider = st.selectbox("Provider", providers)
        submitted = st.form_submit_button("Submit")

        if submitted:
            result = submit_form({
                "type": "newsletter",
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "region": region,
                "postcode": postcode,
                "provider": provider
            })
            if result:
                st.success("You're subscribed! 🎉")


def alert_form(regions: list[str], providers: list[str]):
    """Display Alert subscription form"""

    st.header("Subscribe to Outage Alerts")
    with st.form("outage_form"):
        first_name = st.text_input("First Name", key="f2")
        last_name = st.text_input("Last Name", key="l2")
        phone = st.text_input("Phone Number", key="p2")
        region = st.selectbox("Region", regions, key="r2")
        postcode = st.text_input("Postcode", key="pc2")
        provider = st.selectbox("Provider", providers, key="pr2")
        submitted = st.form_submit_button("Submit")

        if submitted:
            result = submit_form({
                "type": "alert",
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "region": region,
                "postcode": postcode,
                "provider": provider
            })
            if result:
                st.success("Alert subscription saved!")


def main(conn: connection):
    """Start Dashboard"""

    st.title("Subscribe")

    tab1, tab2 = st.tabs(["Newsletter", "Outage Alerts"])

    regions = get_region_data(conn)
    providers = get_provider_data(conn)

    with tab1:
        newsletter_form(regions, providers)

    with tab2:
        alert_form(regions, providers)


if __name__ == "__main__":
    db_connection = get_connection_to_db()
    main(db_connection)
