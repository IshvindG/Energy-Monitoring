# Overview

## Carbon Dioxide Emission ETL
This folder covers an ETL script which extracts information about forecasted carbon dioxide emissions from the NESO Data Portal API and uploads the data to a Postgres Database on RDS every 30 minutes.

The ETL script is containerized in a Dockerfile and uploaded to a Lambda function on AWS.

## Files Included

1. `co2_extract_clean.py`
    - Extracts data from the last 30 minutes from 'https://api.neso.energy/api/3/action/datastore_search_sql'
    - Cleans the extracted data
    - Categorises co2 emissions as low, medium or high 
    - Uploads cleaned data to a CSV

2. `co2_load.py`
    - Connects to Postgres RDS
    - Inserts cleaned data from CSV into database


3. `main.py`
    - Script containing lambda handler function to be able to run ETL on a lambda function

4. `Dockerfile`
    - Defines the Docker image for running the ETL pipeline. It installs the dependencies from requirements.txt and copies the necessary Python files to the container.


5. `requirements.txt`
    - `pandas`
    - `requests`
    - `psycopg2-binary`
    - `python-dotenv`

6. `terraform`
    1. `main.tf`
    - Contains terraform code to provision IAM Role, Lambda Function and existing ECR
    2. `variables.tf`
    - Defines variables required to run `main.tf`
    3. `terraform.tfvars`
    - Contains enviornment variables. See below

## Requirements 
- Postgres RDS Database credentials

```
DB_PASSWORD= db_password
DB_HOST= db_host
DB_PORT= db_port
DB_USER= db_use
DB_NAME= db_name
```

