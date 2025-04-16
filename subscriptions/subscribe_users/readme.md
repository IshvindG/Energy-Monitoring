# Overview
This folder contains a script to subscribe users to a newsletter or alert and update the database with their information

# Scripts
- lambda.py: checks if a user exists, if not adds them to the database and subscribes them to the newsletter/alert. The pipeline is added to a lambda handler to work on an AWS lambda

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