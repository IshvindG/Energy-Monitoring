# Power Generation Data

ETL Script for retrieving data related to energy generation.
Includes:
- Generation by type
- Imported / Exported power
- Market price per MW/h from ATX
- Overall demand over 24h

Each ETL script can be run standalone via `python3` and will save/read/upload data from a CSV instead. 

`extract.py` - Extract data from publicly available APIs
`transform.py` - Clean data, remove unnecessary bits, adjust into the format we need
`load.py` - Upload data to the database, in correct tables
`pipeline.py` - Combines all three stages to perform ETL. This is in the form of a lambda function, with the main method as `handler()`
`requirements.txt` - Requirements for the pipeline to run

`data/` - Folder for storing CSV files when running files individually
`terraform/` - Infrastructure details stored in here. Defines ECS task
`tests/` - Defines tests for the pipeline

Environment variables needed
```
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_USER=
DB_NAME=
```
