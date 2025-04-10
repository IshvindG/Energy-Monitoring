import os
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


def create_empty_clean_csv():
    '''Creates csv file to add cleaned data'''

    if not os.path.exists('clean_power_outage_data.csv'):
        logging.info("Creating empty clean CSV as it doesn't exist.")
        empty_df = pd.DataFrame(
            columns=['reference_id', 'outage_start', 'outage_end', 'Provider_name', 'planned'])
        empty_df.to_csv('clean_power_outage_data.csv', index=False)
        logging.info("Empty clean CSV created.")
    else:
        logging.info("Clean CSV already exists.")


def clean_electric_nw():
    '''Cleans electric north west csv'''

    logging.info("Cleaning process started.")

    df = pd.read_csv('electric_nw_outage_data.csv')

    cleaned_df = pd.DataFrame({
        'reference_id': df['Reference'],
        'outage_start': pd.to_datetime(df['First reported at'], errors='coerce'),
        'outage_end': pd.to_datetime(df['Estimated time of restoration'], errors='coerce'),
        'Provider_name': 'Electricity North West',
        'planned': np.nan
    })

    cleaned_df = cleaned_df.applymap(
        lambda x: np.nan if pd.isna(x) or x == '' else x)

    existing_df = pd.read_csv('clean_power_outage_data.csv')
    new_data = cleaned_df[~cleaned_df['reference_id'].isin(
        existing_df['reference_id'])]

    if not new_data.empty:
        new_data.to_csv('clean_power_outage_data.csv',
                        mode='a', header=False, index=False)
        logging.info("Uploaded %s full rows.", len(new_data))

    logging.info("Cleaning process completed.")


def clean_national_grid():
    '''Cleans national grid csv'''

    logging.info("Cleaning process started.")

    df = pd.read_csv('national_grid_power_outages.csv')

    cleaned_df = pd.DataFrame({
        'reference_id': df['incident_id'],
        'outage_start': pd.to_datetime(df['outage_start'], errors='coerce'),
        'outage_end': pd.to_datetime(df['outage_end'], errors='coerce'),
        'Provider_name': 'National Grid',
        'planned': df['planned'].apply(lambda x: True if x == 'true' else False)
    })

    cleaned_df = cleaned_df.applymap(
        lambda x: np.nan if pd.isna(x) or x == '' else x)

    existing_df = pd.read_csv('clean_power_outage_data.csv')
    new_data = cleaned_df[~cleaned_df['reference_id'].isin(
        existing_df['reference_id'])]

    if not new_data.empty:
        new_data.to_csv('clean_power_outage_data.csv',
                        mode='a', header=False, index=False)
        logging.info("Uploaded %s full rows.", len(new_data))

    logging.info("Cleaning process completed.")


def clean_northern_power():
    '''Cleans Northern Power csv'''

    logging.info("Cleaning Northern Power Grid data.")

    if not os.path.exists('northern_power_outage_data.csv') or os.path.getsize('northern_power_outage_data.csv') == 0:
        logging.warning(
            "northern_power_outage_data.csv is empty or doesn't exist. Skipping processing.")
        return

    try:
        df = pd.read_csv('northern_power_outage_data.csv')

        if df.empty:
            logging.warning(
                "northern_power_outage_data.csv exists but contains no data. Skipping processing.")
            return

        def infer_planned(category):
            if isinstance(category, str) and ('planned power cut' in category.lower() or 'scheduled power cut' in category.lower()):
                return True
            return False

        cleaned_df = pd.DataFrame({
            'reference_id': df['Power Cut ID'],
            'outage_start': pd.to_datetime(df['Start Time'], errors='coerce'),
            'outage_end': pd.to_datetime(df['End Time'], errors='coerce'),
            'Provider_name': 'Northern Powergrid',
            'planned': df['Category'].apply(infer_planned)
        })

        cleaned_df = cleaned_df.applymap(
            lambda x: np.nan if pd.isna(x) or x == '' else x)

        if not os.path.exists('clean_power_outage_data.csv'):
            logging.info("Creating clean_power_outage_data.csv with headers")
            cleaned_df.to_csv('clean_power_outage_data.csv', index=False)
            logging.info("Created file with %s rows.", len(cleaned_df))
            return

        existing_df = pd.read_csv('clean_power_outage_data.csv')
        new_data = cleaned_df[~cleaned_df['reference_id'].isin(
            existing_df['reference_id'])]

        if not new_data.empty:
            new_data.to_csv('clean_power_outage_data.csv',
                            mode='a', header=False, index=False)
            logging.info("Uploaded %s new rows.", len(new_data))
        else:
            logging.info("No new data to append.")

    except pd.errors.EmptyDataError:
        logging.warning(
            "northern_power_outage_data.csv is empty. Skipping processing.")
    except OSError as e:
        logging.error("Error processing Northern Power Grid data: %s", e)

    logging.info("Northern Power Grid cleaning process completed.")


def clean_sp():
    '''Cleans SP Energy csv'''

    logging.info("Cleaning process started.")

    df = pd.read_csv('sp_outage_data.csv')

    def interpret_planned(status):
        if isinstance(status, str):
            status = status.strip().lower()
            if status == 'live':
                return 'false'
            elif status == 'restored':
                return 'false'
        return 'NA'

    cleaned_df = pd.DataFrame({
        'reference_id': df['incident_id'],
        'outage_start': pd.to_datetime(df['outage_start'], errors='coerce'),
        'outage_end': pd.to_datetime(df['outage_end'], errors='coerce'),
        'Provider_name': 'SP Energy Networks',
        'planned': df['status'].apply(interpret_planned)
    })

    cleaned_df.loc[cleaned_df['planned'] == 'false', 'outage_end'] = np.nan
    cleaned_df.loc[cleaned_df['planned'] == 'false', 'planned'] = np.nan

    cleaned_df = cleaned_df.applymap(
        lambda x: np.nan if pd.isna(x) or x == '' else x)

    existing_df = pd.read_csv('clean_power_outage_data.csv')
    new_data = cleaned_df[~cleaned_df['reference_id'].isin(
        existing_df['reference_id'])]

    if not new_data.empty:
        new_data.to_csv('clean_power_outage_data.csv',
                        mode='a', header=False, index=False)
        logging.info("Uploaded %s full rows.", len(new_data))

    logging.info("Cleaning process completed.")


def clean_ssen():
    '''Cleans SSEN csv'''

    logging.info("Cleaning process for SSEN started.")

    df = pd.read_csv('ssen_outage_data.csv')

    def infer_planned(val):
        if isinstance(val, str):
            if 'LV' in val:
                return False
            elif 'PSI' in val or 'HV' in val:
                return True
        return 'NA'

    cleaned_df = pd.DataFrame({
        'reference_id': df['incident_id'],
        'outage_start': pd.to_datetime(df['outage_start'], errors='coerce'),
        'outage_end': pd.to_datetime(df['outage_end'], errors='coerce'),
        'Provider_name': 'Scottish and Southern Energy (SSE)',
        'planned': df['planned'].apply(infer_planned)
    })

    cleaned_df = cleaned_df.applymap(
        lambda x: np.nan if pd.isna(x) or x == '' else x)

    existing_df = pd.read_csv('clean_power_outage_data.csv')
    new_data = cleaned_df[~cleaned_df['reference_id'].isin(
        existing_df['reference_id'])]

    if not new_data.empty:
        new_data.to_csv('clean_power_outage_data.csv',
                        mode='a', header=False, index=False)
        logging.info("Uploaded %s full rows.", len(new_data))

    logging.info("Cleaning process for SSE completed.")


def clean_uk_power():
    '''Cleans Uk Power csv'''

    logging.info("Cleaning process for UK Power Networks started.")

    df = pd.read_csv('ukpowernetworks_outage.csv')

    cleaned_df = pd.DataFrame({
        'reference_id': df['incident_id'],
        'outage_start': pd.to_datetime(df['outage_start'], errors='coerce'),
        'outage_end': pd.to_datetime(df['outage_end'], errors='coerce'),
        'Provider_name': 'UK Power Networks',
        'planned': df['planned'].apply(lambda x: True if x == 'Planned' else False)
    })

    cleaned_df = cleaned_df.applymap(
        lambda x: np.nan if pd.isna(x) or x == '' else x)

    existing_df = pd.read_csv('clean_power_outage_data.csv')
    new_data = cleaned_df[~cleaned_df['reference_id'].isin(
        existing_df['reference_id'])]

    if not new_data.empty:
        new_data.to_csv('clean_power_outage_data.csv',
                        mode='a', header=False, index=False)
        logging.info("Uploaded %s full rows.", len(new_data))

    logging.info("Cleaning process for UK Power Networks completed.")


if __name__ == "__main__":
    create_empty_clean_csv()
    clean_electric_nw()
    clean_national_grid()
    clean_northern_power()
    clean_sp()
    clean_ssen()
    clean_uk_power()
