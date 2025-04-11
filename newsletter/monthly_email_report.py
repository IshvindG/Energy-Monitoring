"""Script to get users and send them the monthly report"""
import logging
from dotenv import load_dotenv
from send_email import send_email_with_attachment
from newsletter_pdf import create_report_data, create_pdf_report
from newsletter import get_connection_to_db, enable_logging


def get_subscribed_users(cursor: 'Cursor') -> list[tuple]:
    """Retrieving all subscriber names and emails from database"""
    query = """SELECT u.first_name, u.email
                FROM users AS u
                JOIN subscriptions AS s ON s.user_id = u.user_id;"""

    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()

    return result


def send_emails_to_users(users: list[tuple], file_name: str):
    """extracting name and email from database results"""
    for user in users:
        name, email = user
        send_email_with_attachment(file_name, email, name)


def lambda_handler(event, context):
    """Combining all functions into a single lambda handler to be run on AWS"""
    try:
        load_dotenv()
        enable_logging()
        logging.info('Event: %s, Context %s', event, context)
        pdf_filename = "/tmp/monthly_report.pdf"
        logging.info("Getting connection")
        db_connection = get_connection_to_db()
        logging.info("Connected to database")
        curr = db_connection.cursor()
        logging.info("Finding subscribed users")
        subscribed_users = get_subscribed_users(curr)
        logging.info("Found users")
        logging.info("Creating newsletter")
        report_data = create_report_data()
        create_pdf_report(report_data, pdf_filename)
        logging.info("Report created")
        logging.info("Sending emails to subscribers")
        send_emails_to_users(subscribed_users, pdf_filename)
        logging.info("Emails sent")
        db_connection.close()
        return {
            "statusCode": 200,
            "body": "Emails sent successfully."
        }
    except Exception as e:
        logging.error("Error in monthly_email_report Lambda: %s", e)
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }


if __name__ == "__main__":

    lambda_handler({}, {})
