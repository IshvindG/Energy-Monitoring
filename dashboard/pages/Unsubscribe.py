"""Script to create a subscription page in the dashboard"""
import os
import streamlit as st
from utils.unsub_api import submit_form
import psycopg2
from dotenv import load_dotenv


def get_connection_to_db():
    """Gets a psycopg2 connection to the energy database"""
    load_dotenv()
    return psycopg2.connect(host=os.getenv("DB_HOST"),
                            database=os.getenv("DB_NAME"),
                            user=os.getenv("DB_USER"),
                            password=os.getenv("DB_PASSWORD"),
                            port=os.getenv("DB_PORT"))


def execute_query(conn: 'Connection', query: str) -> list[str]:
    """"""
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def get_region_data(conn: 'Connection') -> list[str]:

    cursor = conn.cursor()

    query = """SELECT region_name FROM regions;"""
    cursor.execute(query)
    result = cursor.fetchall()
    region_data = []

    for region in result:
        region_data.append(region[0])

    return region_data


def newsletter_form(regions: list[str]):
    regions.append('All')
    st.header("Unsubscribe from Newsletter")
    with st.form("newsletter_form"):
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
        # region = st.selectbox("Region", regions)
        # postcode = st.text_input("Postcode")
        submitted = st.form_submit_button("Submit")

        if submitted:
            result = submit_form({
                "type": "newsletter",
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "email": email
                # "region": region,
                # "postcode": postcode
            })
            if result:
                st.success("You've successfully unsubscribed! ")


def alert_form(regions: list[str]):
    regions.append('All')
    st.header("Unsubscribe from Outage Alerts")
    with st.form("outage_form"):
        first_name = st.text_input("First Name", key="f2")
        last_name = st.text_input("Last Name", key="l2")
        phone = st.text_input("Phone Number", key="p2")
        email = st.text_input("Email")
        region = st.selectbox("Region", regions, key="r2")
        postcode = st.text_input("Postcode", key="pc2")
        submitted = st.form_submit_button("Submit")

        if submitted:
            result = submit_form({
                "type": "alert",
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "email": email,
                "region": region,
                "postcode": postcode,

            })
            if result:
                st.success("Unsubscribed from alert!")


def main(conn: 'Connection'):

    st.title("Unsubscribe :(")

    tab1, tab2 = st.tabs(["Newsletter", "Outage Alerts"])

    regions = get_region_data(conn)

    with tab1:
        newsletter_form(regions)

    with tab2:
        alert_form(regions)


if __name__ == "__main__":
    connection = get_connection_to_db()
    main(connection)
