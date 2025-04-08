"""Pipeline file to perform ETL for pricing, generation and demand data"""
import logging
from extract import get_pricing_data, get_generation_data, get_demand_data
from transform import transform_market_price, transform_energy_generation, transform_energy_demand
from load import load_market_price_data, load_energy_generation_data, load_energy_demand_data
import pandas as pd

logger = logging.getLogger()


def enable_logger() -> None:
    """Enable basic logger"""
    logger.basicConfig(
        level=logging.INFO,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )


def main():
    """Main method - Perform ETL pipeline"""
    enable_logger()

    logger.info("Getting data")
    pricing_data = get_pricing_data().get('data')
    demand_data = get_demand_data()
    generation_data = get_generation_data().get('data')

    logger.info("Creating dataframes")
    pricing_data_df = pd.DataFrame(pricing_data)
    demand_data_df = pd.DataFrame(demand_data)
    generation_data_df = pd.DataFrame(generation_data)\

    logger.info("Cleaning data")
    cleaned_pricing_data = transform_market_price(pricing_data_df)
    cleaned_demand_data_df = transform_energy_demand(demand_data_df)
    cleaned_generation_data_df = transform_energy_generation(
        generation_data_df)

    logger.info("Converting...")
    db_pricing = cleaned_pricing_data.to_dict('records')
    db_demand = cleaned_demand_data_df.to_dict('records')
    db_generation = cleaned_generation_data_df.to_dict('records')

    logger.info("Uploading data")
    load_market_price_data(db_pricing)
    load_energy_demand_data(db_demand)
    load_energy_generation_data(db_generation)
    logger.info("ETL Complete")


if __name__ == '__main__':
    main()
