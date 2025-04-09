import pandas as pd
import os
import numpy as np


def create_empty_clean_csv():
    if not os.path.exists('clean_power_outage_data.csv'):
        empty_df = pd.DataFrame(
            columns=['outage_start', 'outage_end', 'Provider_name', 'planned'])
        empty_df.to_csv('clean_power_outage_data.csv', index=False)
        print("Empty 'clean_power_outage_data.csv' created.")
    else:
        print("'clean_power_outage_data.csv' already exists.")


def clean_electric_nw():
    df = pd.read_csv('electric_nw_outage_data.csv')

    print("Column names in the CSV file:", df.columns)

    print("Sample data from 'First reported at' column:",
          df['First reported at'].head())
    print("Sample data from 'Estimated time of restoration' column:",
          df['Estimated time of restoration'].head())

    cleaned_df = pd.DataFrame({
        'outage_start': pd.to_datetime(df['First reported at'], errors='coerce'),
        'outage_end': pd.to_datetime(df['Estimated time of restoration'], errors='coerce'),
        'Provider_name': 'Electricity North West',
        'planned': 'NA'
    })

    cleaned_df = cleaned_df.applymap(
        lambda x: np.nan if pd.isna(x) or x == '' else x)

    print("Cleaned DataFrame preview:\n", cleaned_df.head())

    cleaned_df.to_csv('clean_power_outage_data.csv',
                      mode='a', header=False, index=False)


def clean_national_grid():
    df = pd.read_csv('national_grid_power_outages.csv')

    print("Column names in the National Grid CSV file:", df.columns)

    print("Sample data from 'outage_start' column:", df['outage_start'].head())
    print("Sample data from 'outage_end' column:", df['outage_end'].head())

    cleaned_df = pd.DataFrame({
        'outage_start': pd.to_datetime(df['outage_start'], errors='coerce'),
        'outage_end': pd.to_datetime(df['outage_end'], errors='coerce'),
        'Provider_name': 'National Grid',
        'planned': df['planned'].apply(lambda x: 'true' if x == 'true' else 'false')
    })

    cleaned_df = cleaned_df.applymap(
        lambda x: np.nan if pd.isna(x) or x == '' else x)

    print("Cleaned DataFrame preview for National Grid:\n", cleaned_df.head())

    cleaned_df.to_csv('clean_power_outage_data.csv',
                      mode='a', header=False, index=False)


def clean_northern_power():
    df = pd.read_csv('northern_power_outage_data.csv')

    print("Column names in Northern Powergrid CSV:", df.columns)

    print("Sample 'Start Time':", df['Start Time'].head())
    print("Sample 'End Time':", df['End Time'].head())

    def infer_planned(category):
        if isinstance(category, str) and 'planned' in category.lower():
            return 'true'
        return 'false'

    cleaned_df = pd.DataFrame({
        'outage_start': pd.to_datetime(df['Start Time'], errors='coerce'),
        'outage_end': pd.to_datetime(df['End Time'], errors='coerce'),
        'Provider_name': 'Northern Powergrid',
        'planned': df['Category'].apply(infer_planned)
    })

    cleaned_df = cleaned_df.applymap(
        lambda x: np.nan if pd.isna(x) or x == '' else x)

    print("Cleaned Northern Powergrid Data:\n", cleaned_df.head())

    cleaned_df.to_csv('clean_power_outage_data.csv',
                      mode='a', header=False, index=False)


def clean_sp():
    df = pd.read_csv('sp_outage_data.csv')

    print("Columns in Scottish Power CSV:", df.columns)
    print("Sample 'outage_start':", df['outage_start'].head())
    print("Sample 'outage_end':", df['outage_end'].head())
    print("Sample 'planned':", df['planned'].head())

    def interpret_planned(val):
        if isinstance(val, str) and val.strip().lower() == 'live':
            return 'false'
        elif isinstance(val, str) and val.strip().lower() == 'restored':
            return 'false'
        else:
            return 'NA'

    cleaned_df = pd.DataFrame({
        'outage_start': pd.to_datetime(df['outage_start'], errors='coerce'),
        'outage_end': pd.to_datetime(df['outage_end'], errors='coerce'),
        'Provider_name': 'SP Energy Networks',
        'planned': df['planned'].apply(interpret_planned)
    })

    cleaned_df = cleaned_df.applymap(
        lambda x: np.nan if pd.isna(x) or x == '' else x)

    print("Cleaned Scottish Power Data:\n", cleaned_df.head())

    cleaned_df.to_csv('clean_power_outage_data.csv',
                      mode='a', header=False, index=False)


def clean_ssen():
    df = pd.read_csv('ssen_outage_data.csv')

    df['outage_end'] = df['outage_end'].replace(['N/A', '', ' '], np.nan)

    outage_start = pd.to_datetime(df['outage_start'], errors='coerce')
    outage_end = pd.to_datetime(df['outage_end'], errors='coerce')

    planned = 'NA'

    cleaned_df = pd.DataFrame({
        'outage_start': outage_start,
        'outage_end': outage_end,
        'Provider_name': 'Scottish and Southern Energy (SSE)',
        'planned': planned
    })

    cleaned_df.replace(r'^\s*$', np.nan, regex=True, inplace=True)

    cleaned_df.to_csv('clean_power_outage_data.csv',
                      mode='a', header=False, index=False)


def clean_uk_power():
    df = pd.read_csv('ukpowernetworks_outage.csv')

    outage_start = pd.to_datetime(df['outage_start'], errors='coerce')
    outage_end = pd.to_datetime(df['outage_end'], errors='coerce')

    def parse_planned(val):
        if isinstance(val, str) and val.strip().lower() == 'planned':
            return True
        elif isinstance(val, str) and val.strip().lower() == 'unplanned':
            return False
        else:
            return 'NA'

    planned_status = df['planned'].apply(parse_planned)

    cleaned_df = pd.DataFrame({
        'outage_start': outage_start,
        'outage_end': outage_end,
        'Provider_name': 'UK Power Networks',
        'planned': planned_status
    })

    cleaned_df.replace(r'^\s*$', np.nan, regex=True, inplace=True)

    cleaned_df.to_csv('clean_power_outage_data.csv',
                      mode='a', header=False, index=False)


if __name__ == "__main__":
    create_empty_clean_csv()
    clean_electric_nw()
    clean_national_grid()
    clean_northern_power()
    clean_sp()
    clean_ssen()
    clean_uk_power()
