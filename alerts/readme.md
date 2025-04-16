# Overview
This folder contains scripts to find a region based on a postcode input and send alerts to subscribed users

# Scripts
- postcode_lookup.py: utilises the https://api.postcodes.io/postcodes/{postcode} api to find the region associated with a specific postcode to find the provider for a postcode
- send_alerts.py: Connects to the database and finds users subscribed to alerts, sending them an alert on outages based on their registered region.postcode

# Requirements
- A .env file with the following variables:
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
