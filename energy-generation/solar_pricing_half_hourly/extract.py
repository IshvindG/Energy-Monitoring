"""Extract energy generation data from online source"""
from datetime import datetime, timedelta
import csv
import logging
import os
import requests

TODAY = datetime.now()
YESTERDAY = TODAY - timedelta(hours=24)

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"
MARKET_PRICE_URL = f"{BASE_URL}/balancing/pricing/market-index"\
    f"?from={YESTERDAY.isoformat()}&to={TODAY.isoformat()}&dataProviders=APXMIDP"
SOLAR_DETAILS = "https://api.solar.sheffield.ac.uk/pvlive/api/v4/gsp/0"

logger = logging.getLogger(__name__)


def perform_http_get(url: str) -> list[dict]:
    """Perform HTTP get request and retrieve JSON"""
    logger.info('Performing HTTP request to %s', url)
    data = requests.get(
        url, timeout=10)
    if data.status_code != 200:
        logger.error('No data recieved!')
        return None
    return data.json()


def get_pricing_data() -> list[dict]:
    """Retrieve market index data from Elexon Insights"""
    logger.info("Getting Pricing data...")
    return perform_http_get(MARKET_PRICE_URL)


def get_solar_estimate_data() -> list[dict]:
    """Retrieve market index data from Elexon Insights"""
    logger.info("Getting solar_estimate data...")
    return perform_http_get(SOLAR_DETAILS)


def save_data(filename: str, data: list[dict], is_solar=False) -> None:
    """Save data to a CSV file"""
    if data is None:
        logger.error('No info available, skipping %s', filename)
        return

    if not os.path.exists('data'):
        os.makedirs('data')

    logger.info('Writing data to %s', filename,)

    with open(filename, 'w', encoding='utf-8') as csvfile:
        if is_solar:
            writer = csv.writer(csvfile)
            writer.writerow(data['meta'])
            writer.writerow(data['data'][0])
        else:
            writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    logger.info('File complete')


if __name__ == "__main__":
    # When run alone this script will take data and write to CSV files

    market_price_data = get_pricing_data()
    save_data('data/market_price.csv', market_price_data.get('data'))

    solar_estimate_data = get_solar_estimate_data()

    print(solar_estimate_data)
    save_data('data/solar_estimate.csv', solar_estimate_data, is_solar=True)
