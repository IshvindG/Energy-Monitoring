"""Script to unsubscribe users if they exist, and remove them from the database"""
import json
import os
import logging
from dotenv import load_dotenv
import psycopg2
import boto3
from botocore.exceptions import ClientError


def enable_logging() -> None:
    """Enables logging at INFO level"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )


def connect_to_db():
    """Gets a psycopg2 connection to the energy database"""
    load_dotenv()
    logging.info("Connecting to the database...")
    return psycopg2.connect(host=os.getenv("DB_HOST"),
                            database=os.getenv("DB_NAME"),
                            user=os.getenv("DB_USER"),
                            password=os.getenv("DB_PASSWORD"),
                            port=os.getenv("DB_PORT"))


def define_user_info(response: dict) -> dict:
    """Creating user information based on POST data from API gateway"""
    body = json.loads(response['body'])
    user_info = {
        "phone": body.get("phone"),
        "email": body.get("email"),
        "type": body.get("type"),
        "region": body.get("region")
    }
    return user_info


def user_details(user_info: dict) -> str:
    """Extracting user details from the user_info dict to reduce redundancy"""
    phone = user_info["phone"]
    email = user_info["email"]
    return phone, email


def check_user_exists(cursor: 'Cursor', user: dict):
    """Querying database to check if the user submitted already exists, if so returning
    their user_id"""
    phone, email = user_details(user)
    query = """SELECT user_id FROM users
                WHERE phone_number = %s
                OR email = %s"""

    logging.info("Checking if user exists...")

    cursor.execute(query, (phone, email))
    result = cursor.fetchall()

    if not result:
        logging.info("No user found with the given details.")
        return None

    user_id = result[0][0]
    return user_id


def check_if_user_is_subscribed_one_region(cursor: 'Cursor', user: dict, user_id: int) -> bool:
    """Checking is a user is already subscribed to the newsletter for a region, returning true/false"""
    logging.info("Checking if user is subscribed to newsletter...")
    region = user.get('region')

    query = """SELECT * FROM subscriptions WHERE user_id = %s AND region_id = (
                    SELECT region_id FROM regions WHERE region_name = %s
                )"""
    cursor.execute(query, (user_id, region))
    result = cursor.fetchall()
    if result:
        logging.info("User already subscribed to newsletter")
        return True

    logging.info("User not subscribed to newsletter")
    return False


def check_if_user_is_subscribed(cursor: 'Cursor', user: dict, user_id: int) -> bool:
    """Checking is a user is already subscribed to the newsletter, returning true/false"""
    logging.info("Checking if user is subscribed to newsletter...")

    query = """SELECT * FROM subscriptions WHERE user_id = %s"""
    cursor.execute(query, (user_id, ))
    result = cursor.fetchall()
    if result:
        logging.info("User is subscribed to newsletter")
        return True

    logging.info("User not subscribed to newsletter")
    return False


def unsubscribe_user_to_newsletter_one_region(cursor: 'Cursor', user: dict, user_id: int):
    """Unsubscribing user from newsletter and removing details from subscriptions table"""
    logging.info("Unsubscribing user from newsletter...")
    region = user.get("region")
    query = """DELETE FROM subscriptions
                WHERE user_id = %s
                AND region_id = (SELECT region_id FROM regions WHERE region_name = %s)"""
    cursor.execute(query, (user_id, region))
    logging.info("User unsubscribed from newsletter successfully!")


def unsubscribe_user_to_newsletter_all(cursor: 'Cursor', user_id: int):
    """Unsubscribing user from all newsletters and removing all details from subscriptions table"""
    logging.info("Unsubscribing user from all newsletters...")
    query = """DELETE FROM subscriptions
                WHERE user_id = %s"""
    cursor.execute(query, (user_id, ))
    logging.info("User unsubscribed from all newsletters successfully!")


def handle_newsletter_unsubscribe(cursor: 'Cursor', user_id: int, user: dict):
    """Combining newsletter check and unsubscribe"""
    region = user['region']
    if check_if_user_is_subscribed(cursor, user, user_id):
        if region == 'All':
            unsubscribe_user_to_newsletter_all(cursor, user_id)
        unsubscribe_user_to_newsletter_one_region(cursor, user, user_id)


def check_if_user_has_alert_one_region(cursor: 'Cursor', user: dict, user_id: int) -> bool:
    """Checking is a user already has an alert for the specified region, returning
    true/false"""

    logging.info("Checking if user has alert for region...")
    region = user.get("region")
    query = """SELECT * FROM alerts WHERE user_id = %s AND region_id = (
                    SELECT region_id FROM regions WHERE region_name = %s
                )"""
    cursor.execute(query, (user_id, region))
    result = cursor.fetchone()
    if result:
        logging.info("User subscribed to this alert")
        return True
    logging.info("User not subscribed to this alert")
    return False


def check_if_user_has_alert_any(cursor: 'Cursor', user_id: int) -> bool:
    """Checking is a user already has an alert for the specified region, returning
    true/false"""

    logging.info("Checking if user has alert for region...")
    query = """SELECT * FROM alerts WHERE user_id = %s"""
    cursor.execute(query, (user_id, ))
    result = cursor.fetchone()
    if result:
        logging.info("User subscribed to alerts")
        return True
    logging.info("User not subscribed to any alerts")
    return False


def unsubscribe_user_from_alerts_all(cursor: 'Cursor', user_id: int):
    """Unsubscribing user from all alerts, updating alerts table"""
    logging.info("Unsubscribing user from all alerts...")
    query = """DELETE FROM alerts WHERE user_id = %s"""
    cursor.execute(query, (user_id, ))


def unsubscribe_user_from_alerts_one_region(cursor: 'Cursor', region: str, user_id: int):
    """Unsubscribing user from alert based on chosen region, updating alerts table"""
    logging.info("Unsubscribing user from all alerts...")
    query = """DELETE FROM alerts WHERE user_id = %s
                AND region_id = (SELECT region_id FROM regions WHERE region_name = %s
                ))"""
    cursor.execute(query, (user_id, region))


def handle_alerts(cursor: 'Cursor', user_id: int, user: dict):
    """Combining alert checks and unsubscribing"""
    region = user['region']
    if check_if_user_has_alert_any(cursor, user_id):
        if region == 'All':
            unsubscribe_user_from_alerts_all(cursor, user_id)
        unsubscribe_user_from_alerts_one_region(cursor, user, user_id)


def unsubscribe_user(cursor: 'Cursor', user_id: int, user_info: dict):
    """Handles unsubscribing the user from newsletters and alerts."""

    if user_info["type"] == "newsletter":
        logging.info("User opted to unsubscribe from the newsletter")
        handle_newsletter_unsubscribe(cursor, user_id, user_info)

    if user_info["type"] == "alert":
        logging.info("User opted to unsubscribe from alerts")
        handle_alerts(cursor, user_id, user_info)


def send_phone_verification(phone: str):
    """Sending a phone verification text when a user unsubscribes"""
    logging.info("Sending phone verification to: %s", phone)
    sns = boto3.client('sns', region_name='eu-west-2')
    sns.publish(
        PhoneNumber=phone,
        Message="You've been unsubscribed from Energy Monitor alerts.",
    )


def send_email_verification(email: str):
    """Sending an email verification when a user unsubscribes"""
    logging.info("Sending email verification to: %s", email)
    ses = boto3.client('ses', region_name='eu-west-2')
    ses.send_email(
        Source=os.getenv("SENDER_EMAIL"),
        Destination={"ToAddresses": [email]},
        Message={
            "Subject": {"Data": "Successfully Unsubscribed"},
            "Body": {
                "Text": {
                    "Data": f"Hello, you have successfully unsubscribed from\
                    the chosen newsleter!"
                }
            },
        }
    )


def send_verifications(user_response: dict):
    """Handles sending phone and email verification."""
    if user_response.get("phone"):
        try:
            send_phone_verification(user_response["phone"])
        except ClientError as e:
            logging.error("SNS error: %s", str(e))

    if user_response.get("email"):
        try:
            send_email_verification(
                user_response["email"])
        except ClientError as e:
            logging.error("SES error: %s", str(e))


def lambda_handler(event, context):
    """Combining all functions into a single lambda handler"""
    enable_logging()
    try:
        logging.info("Starting lambda_handler...")
        connection = connect_to_db()
        cursor = connection.cursor()
        user_response = define_user_info(event)

        user_id = check_user_exists(cursor, user_response)

        if not user_id:
            logging.info("User not found in the database.")
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "User not found"})
            }

        unsubscribe_user(cursor, user_id, user_response)

        connection.commit()

        send_verifications(user_response)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "User unsubscribed successfully"})
        }

    except Exception as e:
        logging.error("Error in lambda_handler: %s", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }
