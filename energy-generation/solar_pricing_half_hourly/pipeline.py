"""Pipeline file to perform ETL for pricing, generation and demand data"""
import logging
from extract import get_pricing_data, get_solar_estimate_data
from transform import transform_market_price, transform_solar_generation
from load import load_market_price_data, load_energy_solar_data
import pandas as pd
from psycopg2 import Error as psycopg2Error

logger = logging.getLogger(__name__)


def enable_logger() -> None:
    """Enable basic logger"""
    logging.basicConfig(
        level=logging.INFO,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )


def handler(event: dict, context: dict):
    """Main method - Perform ETL pipeline"""
    enable_logger()

    logger.info("Event: %s", event)
    logger.info("Context: %s", context)
    try:
        logger.info("Getting data")
        pricing_data = get_pricing_data().get('data')
        solar_estimate_data = get_solar_estimate_data()

        logger.info("Creating dataframes")
        pricing_data_df = pd.DataFrame(pricing_data)
        print(solar_estimate_data)
        solar_estimate_data_df = pd.DataFrame(
            solar_estimate_data['data'], columns=solar_estimate_data['meta'])

        logger.info("Cleaning data")
        cleaned_pricing_data = transform_market_price(pricing_data_df)
        cleaned_solar_estimate_data_df = transform_solar_generation(
            solar_estimate_data_df)

        logger.info("Converting...")
        db_pricing = cleaned_pricing_data.to_dict('records')
        db_solar_estimate = cleaned_solar_estimate_data_df.to_dict('records')

        logger.info("Uploading data")
        load_market_price_data(db_pricing)
        load_energy_solar_data(db_solar_estimate)
        logger.info("ETL Complete")
    except (ValueError, TypeError, psycopg2Error) as pipeline_error:
        logger.error('Pipeline error! - %s', pipeline_error)
        return {'status': 500, 'reason': pipeline_error}

    return {'status': 200}


if __name__ == '__main__':
    handler(None, None)
