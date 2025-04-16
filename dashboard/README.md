# Overview
This folder contains all files related to the dashboard - Dashboard pages, Utilities for connecting to the database, assets used in the dashboard and 

## Files Included
1. `Home.py` - Main file to run streamlit using `streamlit run Home.py`
2. `Utils/` - Contains files with commonly used functions 
3. `terraform/` - Files defining infrastructure
4. `pages/` - Other pages for the dashboard, including the 'Emissions' page, and 'Submissions' pages
5.  `assets/` - Images and other files used on the dashboard

## Requirements 
To run locally these are needed in a `.env` and to run on the cloud these are needed in `terraform/tfvars.terraform`

```
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_USER=
DB_NAME=
SUB_LINK=
UNSUB_LINK
```