# Overview
The newsletter folder contains scripts to connect to the database, gather information for a monthly overview, generate a pdf with an overview, and send it to users subscribed to the newsletter

# Scripts
- newsletter.py: Connects to the RDS instance and gathers information added to the database over the past month
- newsletter_pdf.py: Adds data overview to template html and converts this to a pdf report
- send_email.py: Generates an email body and attached the created pdf to the email
- monthly_email_report.py: Connect to database and find users subscribed to newsletter, sending an email to each.

# Requirements
- A .env file containing the following variables:
```
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_USER=
DB_NAME=
SENDER_EMAIL=
```

- To install the required dependencies run:

```pip install -r requirements.txt```
