# Overview
This folder covers everything regarding the database. It contains the schema, and multiple shell scripts for easy interactions with the database.

## Files Included

1. `fuel_types.py`
    - Script to find different fuel types from API and insert into fuel_types table in database

2. `connect.sh`
    - Shell script to quickly connect to the database.
3. `reset_db.sh`
    - Shell script to quickly reset the tables within the database.
4. `seed_db.sh`
    - Shell script to seed the database with data about fuel types.
5. `schema.sql`
    - SQL script to define tables and constraints within the database.
6. `seeding.sql`
    - SQL script to seed the database with data for providers and regions.
7. `requirements.txt`
    - `psycopg2-binary`
    - `requests`
    - `python-dotenv`

8. `terraform`

    - `main.tf`
    - `variables.tf`
    - `terraform.tfvars`

# Requirements

```
DB_PASSWORD= db_password
DB_HOST= db_host
DB_PORT= db_port
DB_USER= db_use
DB_NAME= db_name
```

- To install required dependencies run:

    `pip3 install -r requirements.txt`