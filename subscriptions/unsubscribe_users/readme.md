# Overview
This folder contains a script to unsubscribe users from a newsletter or alert and remove their information from the database

# Scripts
- lambda.py: checks if a user subscription exists. If so, removes the subscription from the database

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