# Overview

## Carbon Dioxide Emission ETL
This folder covers an ETL script which extracts information about power outqges across the United Kingdom and its different energy providers:

- Scottish and Southern Energy (SSE)
- SP Energy Networks
- Electricity North West
- Northern Powergrid
- National Grid
- UK Power Networks

The ETL script gets data from various API endpoints aswell as by web scraping power outage websites to get the most up to date/ live data.

## Files Included

1. `extract_power_outage1.py`
    - Contains separate functions to extract data about power outages for each energy provider within the United Kingdom and uploads it to a CSV.
    - Retrieves data from API's.
    - Retrieves data by web scraping various websites.


2. `clean_power_outage1.py`
    - Function per provider to clean extracted data.
    - Uploads all the cleaned data to a single CSV file.

3. `load_power_outage.py`
    - Establishes connection to Postgres RDS.
    - Inserts unique entries into the database


4. `Dockerfile`
    - Defines the Docker image for running the ETL pipeline. It installs the dependencies from requirements.txt and other neccassary dependancies required for web scraping and copies the necessary Python files to the container.


5. `requirements.txt`
    - `pandas`
    - `numpy`
    - `psycopg2-binary`
    - `python-dotenv`
    - `requests`
    - `beautifulsoup4`
    - `urllib3`
    - `selenium`
    - `webdriver-manager`

6. `terraform`
    1. `main.tf`
    - Contains terraform code to provision CloudWatch, ECS, Security Group, ECS Task Definition.
    2. `variables.tf`
    - Defines variables required to run `main.tf`.
    3. `terraform.tfvars`
    - Contains enviornment variables. See below.

## Requirements 
- Postgres RDS Database credentials:

```
DB_PASSWORD= db_password
DB_HOST= db_host
DB_PORT= db_port
DB_USER= db_use
DB_NAME= db_name
```
