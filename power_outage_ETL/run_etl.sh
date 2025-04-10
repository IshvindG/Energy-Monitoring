#!/bin/bash

echo "Starting ETL process..."

python3 extract_power_outage1.py
python3 clean_power_outage1.py
python3 load_power_outage.py

echo "ETL process completed."
