"""File for signing up to the alert system"""
import os
import streamlit as st
import psycopg2
from psycopg2.extensions import connection
from dotenv import load_dotenv
from utils.api import submit_form
from validate_email_address import validate_email
import phonenumbers


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


def verify_email_address(email: str) -> bool:
    """Function to validate a given email"""
    return validate_email(email)


def validate_phone_number(phone: str) -> bool:
    """Function to validate a given phone number"""
    phone_number = phonenumbers.parse(phone, "GB")
    return phonenumbers.is_valid_number(phone_number)


def newsletter_form():
    """Display Newsletter subscription form"""

    st.header("Subscribe to Newsletter")
    with st.form("newsletter_form"):
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
        submitted = st.form_submit_button("Submit")

        valid_email = True
        valid_number = True

        if email:
            valid_email = verify_email_address(email)
        if phone:
            valid_number = validate_phone_number(phone)

        if submitted:
            if valid_email and valid_number:
                result = submit_form({
                    "type": "newsletter",
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone": phone,
                    "email": email
                })
                if result:
                    st.success("You're subscribed! 🎉")
            else:
                st.error("Invalid email address or phone number")


def alert_form(regions: list[str]):
    """Display Alert subscription form"""

    st.header("Subscribe to Outage Alerts")
    with st.form("outage_form"):
        first_name = st.text_input("First Name", key="f2")
        last_name = st.text_input("Last Name", key="l2")
        phone = st.text_input("Phone Number", key="p2")
        email = st.text_input("Email")
        region = st.selectbox("Region", regions, key="r2")
        postcode = st.text_input("Postcode", key="pc2")
        submitted = st.form_submit_button("Submit")

        valid_email = True
        valid_number = True

        if email:
            valid_email = verify_email_address(email)
        if phone:
            valid_number = validate_phone_number(phone)

        if submitted:
            if valid_email and valid_number:
                result = submit_form({
                    "type": "alert",
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone": phone,
                    "email": email,
                    "region": region,
                    "postcode": postcode
                })
                if result:
                    st.success("Alert subscription saved!")

            else:
                st.error("Invalid email address or phone number")


def main(conn: connection):
    """Start Dashboard"""
    st.logo("assets/icon.png", size="large")
    st.set_page_config(page_icon="assets/icon.png")
    st.title("Subscribe")

    tab1, tab2 = st.tabs(["Newsletter", "Outage Alerts"])
    regions = ['--']
    db_regions = get_region_data(conn)
    regions += db_regions

    with tab1:
        newsletter_form()

    with tab2:
        alert_form(regions)


if __name__ == "__main__":
    db_connection = get_connection_to_db()
    main(db_connection)
