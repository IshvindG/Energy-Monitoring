"""Script to send email alerts to subscribed users about recent outages"""
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from dotenv import load_dotenv
import boto3
import pytz

from alerts.postcode_lookup import (get_connection_to_db, enable_logging,
                                    get_region_from_postcode, find_provider_from_region,
                                    find_provider_from_region_id)


def find_subscribers_from_db(cursor: 'Cursor') -> list[tuple]:
    """Finding all subscribers in the db"""
    query = """SELECT  first_name, phone_number, email, last_alert_sent, region_id, postcode
                FROM alert_users;"""

    cursor.execute(query)

    users = cursor.fetchall()

    return users


def create_subscriber_dict(cursor: 'Cursor') -> list[dict]:
    """Creating a dict for each subscriber"""
    users = find_subscribers_from_db(cursor)
    users_mapped = []
    for user in users:
        user_dict = {
            "name": user[0],
            "phone": user[1],
            "email": user[2],
            "last_alert": user[3],
            "region_id": user[4],
            "postcode": user[5]
        }

        users_mapped.append(user_dict)

    return users_mapped


def find_provider_for_user(cursor: 'Cursor', user: dict) -> dict:
    """Finding the relevant provider for each user"""
    region = user.get("region_id")
    postcode = user.get("postcode")

    if region:
        provider_id, region_name = find_provider_from_region_id(cursor, region)
        user['provider_id'] = provider_id
        user['region_name'] = region_name

    elif postcode:
        region = get_region_from_postcode(postcode)
        provider_id = find_provider_from_region(cursor, region)
        user['provider_id'] = provider_id
        user['region_name'] = region

    else:
        raise ValueError

    return user


def get_current_time_range(minutes: int) -> tuple[str, str]:
    """getting time range"""
    now = datetime.now(pytz.utc)
    past = now - timedelta(minutes=minutes)
    return past.strftime("%Y-%d-%m %H:%M:%S"), now.strftime("%Y-%d-%m %H:%M:%S")


def query_recent_outages(cursor: 'Cursor', provider_id: int,
                         start_time: str, end_time: str) -> list[dict]:
    """Finding recent outages"""
    query = """SELECT outage_start, outage_end, planned
               FROM outages o
               JOIN providers p ON p.provider_id = o.provider_id
               WHERE o.provider_id = %s
               AND outage_start BETWEEN %s AND %s
               ORDER BY outage_start DESC"""

    cursor.execute(query, (provider_id, start_time, end_time))
    results = cursor.fetchall()
    return [
        {
            "outage_start": row[0].strftime("%Y-%m-%d %H:%M:%S") if row[0] else "Unknown",
            "outage_end": row[1].strftime("%Y-%m-%d %H:%M:%S") if row[1] else "Unknown",
            "planned": row[2]
        }
        for row in results
    ]


def find_outage_info_for_user(cursor: 'Cursor', user: dict) -> dict:
    """Finding outages for the user"""
    provider_id = user.get("provider_id")

    if provider_id:
        start_time, end_time = get_current_time_range(1)
        outages = query_recent_outages(
            cursor, provider_id, start_time, end_time)
        user["outages"] = outages
    else:
        user["outages"] = []

    return user


def alert_message_format(user: dict) -> str:
    """Creating personalized alert message"""

    alert_message = (
        f"Hi {user['name']}, there's planned outages "
        f"in the region {user['region_name']}:")

    if user['outages']:
        for outage in user['outages']:
            alert_message += f"""\nFrom {outage['outage_start']} to {outage['outage_end']}"""
    else:
        return None
    return alert_message


def send_alert(user: dict):
    """Send an email using AWS SES."""
    load_dotenv()
    sender_email = os.getenv("SENDER_EMAIL")
    client = boto3.client("ses", region_name="eu-west-2")
    alert = alert_message_format(user)
    message = MIMEMultipart()
    message["Subject"] = "Outage Alert"
    message["From"] = sender_email
    message["To"] = user['email']

    body = MIMEText(alert, "plain")
    message.attach(body)

    try:
        client.send_raw_email(
            Source=message["From"],
            Destinations=[message["To"]],
            RawMessage={"Data": message.as_string()}
        )
        logging.info(f"Email sent to {user['email']} successfully")
    except Exception as e:
        logging.info(f"Failed to send email to {user['email']}: {e}")


def send_alert_pipeline():
    """Pipeline to combine all functions and send alert to users"""
    db_connection = get_connection_to_db()
    curr = db_connection.cursor()
    users = create_subscriber_dict(curr)
    for user in users:
        try:
            user_info = find_provider_for_user(curr, user)
            user_info_full = find_outage_info_for_user(curr, user_info)

            if alert_message_format(user_info_full):
                logging.info("Sending")
                send_alert(user_info_full)
                logging.info("sent")
            else:
                logging.info("failed to send")
        except ValueError as e:
            logging.info(
                f"Failed to process user {user.get('email', 'unknown')}: {e}")
    db_connection.close()


def lambda_handler(event, context):
    """Lambda handler to run pipeline in lambda"""
    enable_logging()
    logging.info("Event: %s, Context: %s", event, context)
    send_alert_pipeline()
    logging.info("Success!")


if __name__ == "__main__":

    send_alert_pipeline()
