"""Script to create users if they don't already exist, and subscribe them to 
newsletter/alerts within a lambda"""
import re
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
        "first_name": body.get("first_name"),
        "last_name": body.get("last_name"),
        "phone": body.get("phone"),
        "postcode": body.get("postcode"),
        "region": body.get("region"),
        "provider": body.get("provider"),
        "email": body.get("email"),
        "type": body.get("type")
    }
    return user_info


def user_details(user_info: dict) -> str:
    """Extracting user details from the user_info dict to reduce redundancy"""
    first_name = user_info["first_name"]
    last_name = user_info["last_name"]
    phone = user_info["phone"]
    email = user_info["email"]
    postcode = user_info["postcode"]
    return first_name, last_name, phone, email, postcode


def check_user_exists(cursor: 'Cursor', user: dict):
    """Querying database to check if the user submitted already exists, if so returning
    their user_id"""
    first_name, last_name, phone, email, postcode = user_details(user)
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


# def validate_user_info(user: dict) -> bool:
#     """Validates email, phone, and name fields."""

#     email = user.get("email")
#     phone = user.get("phone")
#     first_name = user.get("first_name")
#     last_name = user.get("last_name")

#     email_regex = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
#     phone_regex = r"^\+\d{7,15}$"
#     name_regex = r"^[A-Za-zÀ-ÿ'`’\- ]{1,50}$"

#     if not re.match(email_regex, email or ""):
#         logging.error("Invalid email format: %s", email)
#         return False

#     if not re.match(phone_regex, phone or ""):
#         logging.error("Invalid phone number format: %s", phone)
#         return False

#     if not re.match(name_regex, first_name or ""):
#         logging.error("Invalid first name: %s", first_name)
#         return False

#     if not re.match(name_regex, last_name or ""):
#         logging.error("Invalid last name: %s", last_name)
#         return False

#     return True


def upload_user_to_db(cursor: 'Cursor', user: dict) -> int:
    """Uploading user to database if user doesn't exist, returning user_id"""
    logging.info("Uploading user to database...")
    first_name, last_name, phone, email, postcode = user_details(user)
    query = """INSERT INTO users (first_name, last_name, phone_number, email, postcode)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING user_id"""
    cursor.execute(query, (first_name, last_name, phone, email, postcode))
    user_id = cursor.fetchone()[0]
    logging.info("User successfully added to database")
    return int(user_id)


def check_if_user_is_subscribed(cursor: 'Cursor', user: dict, user_id: int) -> bool:
    """Checking is a user is already subscribed to the newsletter, returning true/false"""
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


def subscribe_user_to_newsletter(cursor: 'Cursor', user: dict, user_id: int):
    """Subscribing user to newsletter and adding details to subscriptions table"""
    logging.info("Subscribing user to newsletter...")
    region = user.get("region")
    query = """INSERT INTO subscriptions (user_id, region_id)
                VALUES (%s,
                        (SELECT region_id FROM regions WHERE region_name = %s))"""
    cursor.execute(query, (user_id, region))
    logging.info("User subscribed to newsletter successfully!")


def handle_newsletter(cursor: 'Cursor', user_id: int, user: dict):
    """Combining newsletter check and subscription"""
    if not check_if_user_is_subscribed(cursor, user, user_id):
        subscribe_user_to_newsletter(cursor, user, user_id)


def check_if_user_has_alert(cursor: 'Cursor', user: dict, user_id: int) -> bool:
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
        logging.info("User already subscribed to this alert")
        return True
    logging.info("User not subscribed to this alert")
    return False


def subscribe_user_to_alert(cursor: 'Cursor', region: str, user_id: int):
    """Subscribing user to alert based on chosen region, updating alerts table"""
    logging.info("Subscribing user to alert...")
    query = """INSERT INTO alerts (user_id, region_id)
                    VALUES (
                        %s,
                        (SELECT region_id FROM regions WHERE region_name = %s)
                    )"""
    cursor.execute(query, (user_id, region))
    # send_phone_verification(phone)
    logging.info("User subscribed to alert and verification sent!")


def handle_alerts(cursor: 'Cursor', user_id: int, user: dict):
    """Combining alert checks and subscription"""
    region = user["region"]
    phone = user["phone"]
    if not check_if_user_has_alert(cursor, user, user_id):
        subscribe_user_to_alert(cursor, region, user_id)
        logging.info("User subscribed to alert successfully")


# def send_phone_verification(phone: str):
#     """Sending a phone verification text when a new user subscribes"""
#     logging.info("Sending phone verification to: %s", phone)
#     sns = boto3.client('sns', region_name='eu-west-2')
#     sns.publish(
#         PhoneNumber=phone,
#         Message="You've been subscribed to Energy Monitor alerts.",
#     )


def send_phone_verification(phone: str):
    """Send a phone verification text via SNS."""
    sns = boto3.client(
        'sns', region_name='eu-west-2')
    try:
        response = sns.verify_phone_number(
            PhoneNumber=phone
        )
        logging.info(
            f"Phone verification initiated for {phone}. Response: {response}")
    except ClientError as e:
        logging.error(f"Error sending verification SMS: {e}")
        raise


def send_email_verification(email: str, first_name: str):
    """Sending an email verification when a new user subscribes"""
    logging.info("Sending email verification to: %s", email)
    ses = boto3.client('ses', region_name='eu-west-2')
    ses.send_email(
        Source=os.getenv("SENDER_EMAIL"),
        Destination={"ToAddresses": [email]},
        Message={
            "Subject": {"Data": "Welcome to Energy Monitor"},
            "Body": {
                "Text": {
                    "Data": f"Hello {first_name}, thanks for subscribing!"
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
                user_response["email"], user_response["first_name"])
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

        # if not validate_user_info(user_response):
        #     return {
        #         "statusCode": 400,
        #         "body": json.dumps({"error": "Invalid input format"})
        #     }

        user_id = check_user_exists(cursor, user_response)
        new_user = False
        if not user_id:
            user_id = upload_user_to_db(cursor, user_response)
            connection.commit()
            send_verifications(user_response)
            new_user = True

        if user_response["type"] == "newsletter":
            handle_newsletter(cursor, user_id, user_response)

        elif user_response["type"] == "alert":
            handle_alerts(cursor, user_id, user_response)

        connection.commit()
        connection.close()

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "User created and subscribed" if new_user else "User subscribed"})
        }

    except Exception as e:
        logging.info("Error in lambda_handler: %s", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }
