"""Script that sends an email with the report as an attachment"""
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import boto3
from dotenv import load_dotenv


def generate_email_body(user_name: str) -> str:
    """Generate a well-formatted email body."""
    return f"""Dear {user_name},

It's that exciting time of the month again! Check out the attached newsletter for an exclusive
insight into recent energy prices, demands and more!

Your favourite energy team,
WattWatch"""


def send_email_with_attachment(filename: str, recipient_email: str, user_name: str):
    """Send email with the attached PDF report."""
    client = boto3.client(
        "ses",
        region_name="eu-west-2"
    )

    message = MIMEMultipart()
    message["Subject"] = "Monthly Energy Report"
    message["From"] = os.getenv("SENDER_EMAIL")
    message["To"] = recipient_email

    email_body = generate_email_body(user_name)
    message.attach(MIMEText(email_body, "plain"))

    with open(filename, 'rb') as attachment_file:
        attachment = MIMEApplication(attachment_file.read())
        attachment.add_header('Content-Disposition',
                              'attachment', filename=filename)
        message.attach(attachment)

    try:
        response = client.send_raw_email(
            Source=os.getenv("SENDER_EMAIL"),
            Destinations=[recipient_email],
            RawMessage={
                'Data': message.as_string()
            }
        )
        print(f"Email sent! Message ID: {response['MessageId']}")
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    load_dotenv()
    send_email_with_attachment(
        "monthly_report.pdf", "example@email.com", "User")
