"""Transform step for extracted data"""
import logging
import pandas as pd
DATA_FOLDER = "data/"
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

logger = logging.getLogger(__name__)


def filter_by_largest(filter_column_name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Filter by largest value in a column"""
    logger.info("Filtering...")
    latest_time = df[filter_column_name].max()
    df = df[df[filter_column_name] == latest_time]
    return df


def transform_energy_generation(df: pd.DataFrame) -> pd.DataFrame:
    """Read and transform energy generation"""
    logger.info("Working on energy generation dataframe")
    df.drop(
        columns=['settlementDate', 'settlementPeriod', 'dataset', 'startTime'], inplace=True)
    df['publishTime'] = pd.to_datetime(df['publishTime'], utc=True)
    df = filter_by_largest('publishTime', df)
    return df


def transform_energy_demand(df: pd.DataFrame) -> pd.DataFrame:
    """Read and transform energy demand"""
    logger.info("Working on energy demand dataframe")
    df.drop(columns=['recordType'], inplace=True)
    df['startTime'] = pd.to_datetime(
        df['startTime'], utc=True, format='ISO8601')
    df = filter_by_largest('startTime', df)
    return df


def transform_interconnect_data(df: pd.DataFrame) -> pd.DataFrame:
    """Read and transform interconnect data"""
    logger.info("Working on energy interconnection dataframe")
    df.drop(columns=['dataset', 'startTime', 'settlementDate',
            'settlementDateTimezone', 'settlementPeriod'], inplace=True)

    df['publishTime'] = pd.to_datetime(
        df['publishTime'], utc=True, format='ISO8601')
    df = filter_by_largest('publishTime', df)
    return df


def transform_market_price(df: pd.DataFrame) -> pd.DataFrame:
    """Read and transform latest market data"""
    # Data provider will always be APXMIDP
    logger.info("Working on energy market pricing dataframe")
    df.drop(columns=['dataProvider', 'settlementDate',
            'settlementPeriod'], inplace=True)
    df['startTime'] = pd.to_datetime(
        df['startTime'], utc=True, format='ISO8601')
    df = filter_by_largest('startTime', df)
    return df


def transform_solar_generation(df: pd.DataFrame) -> pd.DataFrame:
    """Read and transform energy generation"""
    logger.info("Working on energy generation dataframe")
    df.drop(columns=['gsp_id'], inplace=True)
    df.rename(columns={"datetime_gmt": "publishTime"}, inplace=True)
    df['fuelType'] = 'SOLAR'
    return df


if __name__ == '__main__':
    # When run standalone will attempt to read data and transform, saving to csv files
    energy_gen_df = pd.read_csv('data/energy_generation.csv')
    cleaned = transform_energy_generation(energy_gen_df)
    cleaned.to_csv('data/energy_generation_cleaned.csv', index=False)

    energy_demand_df = pd.read_csv('data/energy_demand.csv')
    cleaned = transform_energy_demand(energy_demand_df)
    cleaned.to_csv('data/energy_demand_cleaned.csv', index=False)

    interconnect_df = pd.read_csv('data/interconnect.csv')
    cleaned = transform_interconnect_data(interconnect_df)
    cleaned.to_csv('data/interconnect_cleaned.csv', index=False)

    market_df = pd.read_csv('data/market_price.csv')
    cleaned = transform_market_price(market_df)
    cleaned.to_csv('data/market_price_cleaned.csv', index=False)
