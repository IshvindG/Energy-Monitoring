import requests
import pandas as pd
from urllib import parse
from datetime import datetime, timedelta
from typing import List, Dict


def get_time_range(hours_back: int = 0.5) -> tuple[str, str]:
    """
    Returns the current UTC time and a past time offset by `hours_back` hours, both in ISO format.
    """
    now = datetime.utcnow()
    past = now - timedelta(hours=hours_back)
    return past.strftime('%Y-%m-%dT%H:%M:%S.000Z'), now.strftime('%Y-%m-%dT%H:%M:%S.000Z')


def build_sql_query(start: str, end: str) -> str:
    """
    Builds a SQL query string for the given time range.
    """
    return f'''
        SELECT COUNT(*) OVER () AS _count, *
        FROM "c16b0e19-c02a-44a8-ba05-4db2c0545a2a"
        WHERE "datetime" >= '{start}'
        AND "datetime" <= '{end}'
        ORDER BY "_id" ASC
        LIMIT 100
    '''


def fetch_data(sql: str) -> List[Dict]:
    """
    Fetches data from the NESO API using a SQL query.
    """
    params = {'sql': sql}
    try:
        response = requests.get(
            'https://api.neso.energy/api/3/action/datastore_search_sql',
            params=parse.urlencode(params)
        )
        response.raise_for_status()
        return response.json()["result"]["records"]
    except (requests.RequestException, ValueError, KeyError) as e:
        print("Error fetching data:", e)
        return []


def classify_intensity(value: float) -> str:
    """
    Classifies a CO2 intensity value.
    """
    if pd.isna(value):
        return 'unknown'
    elif value <= 150:
        return 'Low'
    elif 150 < value <= 300:
        return 'Medium'
    else:
        return 'High'


def clean_data(records: List[Dict]) -> pd.DataFrame:
    """
    Cleans and reshapes raw records into a tidy dataframe.
    """
    df = pd.DataFrame(records)

    df = df.drop(columns=['_full_text', '_count'], errors='ignore')

    id_vars = ['datetime', '_id']
    value_vars = [col for col in df.columns if col not in id_vars]
    melted = df.melt(id_vars='datetime', value_vars=value_vars,
                     var_name='region_name', value_name='measure')

    melted['measure'] = pd.to_numeric(melted['measure'], errors='coerce')
    melted = melted.rename(columns={'datetime': 'time_of_measure'})

    melted['index'] = melted['measure'].apply(classify_intensity)

    return melted


def save_to_csv(df: pd.DataFrame, filename: str = '/tmp/clean_live_co2.csv') -> None:
    """
    Saves the dataframe to a CSV file. The file is overwritten each time.
    """
    df.to_csv(filename, index=False)
    print(f"Saved cleaned data with carbon index to {filename}")


def main() -> None:
    """
    Main entry point for data extraction, transformation, and CSV saving.
    """
    start, end = get_time_range(hours_back=0.5)
    sql = build_sql_query(start, end)
    records = fetch_data(sql)

    if records:
        cleaned_df = clean_data(records)
        save_to_csv(cleaned_df)
    else:
        print("No data retrieved to process.")


if __name__ == '__main__':
    main()
