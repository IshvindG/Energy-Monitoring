# This script extracts data about forecast and actual carbon intensity data
import json
from urllib import parse
import requests
import csv
import os
from datetime import datetime


def extract_national_co2_data_today(national_csv_filename="national_carbon_intensity.csv"):
    """
    Extracts the latest UK national carbon intensity data and saves it to a CSV file.
    """
    url = "https://api.carbonintensity.org.uk/intensity"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        intensity_data = data["data"][0]
        from_time = intensity_data["from"]
        to_time = intensity_data["to"]
        forecast = intensity_data["intensity"]["forecast"]
        actual = intensity_data["intensity"]["actual"]
        index = intensity_data["intensity"]["index"]

        file_exists = os.path.isfile(national_csv_filename)

        with open(national_csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["from", "to", "forecast", "actual", "index"])
            writer.writerow([from_time, to_time, forecast, actual, index])

        print(f"Appended data to {national_csv_filename}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except KeyError:
        print("Unexpected data format received from the API.")


def extract_regional_co2_data_today():
    url = "https://api.carbonintensity.org.uk/regional"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        with open('regional_co2_data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)

            if file.tell() == 0:
                writer.writerow(['Timestamp', 'Region', 'Intensity Forecast', 'Intensity Index',
                                 'Fuel', 'Fuel Percentage'])

            for item in data['data']:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                for region in item['regions']:
                    region_name = region['shortname']
                    intensity_forecast = region['intensity']['forecast']
                    intensity_index = region['intensity']['index']

                    for fuel in region['generationmix']:
                        fuel_name = fuel['fuel']
                        fuel_percentage = fuel['perc']

                        writer.writerow(
                            [timestamp, region_name, intensity_forecast, intensity_index, fuel_name, fuel_percentage])

        print("Data successfully extracted and appended to regional_co2_data.csv.")

    else:
        print(f"Failed to retrieve data: {response.status_code}")


def extract_co2_intensity_factors_today():
    url = "https://api.carbonintensity.org.uk/intensity/factors"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        with open('co2_intensity_factors.csv', mode='a', newline='') as file:
            writer = csv.writer(file)

            if file.tell() == 0:
                writer.writerow(['Timestamp', 'Fuel Type',
                                'CO2 Intensity Factor (gCO2/kWh)'])

            for item in data['data']:
                timestamp = datetime.utcnow().strftime(
                    '%Y-%m-%d %H:%M:%S')

                for fuel, intensity in item.items():
                    writer.writerow([timestamp, fuel, intensity])

        print("Data successfully extracted and appended to co2_intensity_factors.csv.")

    else:
        print(f"Failed to retrieve data: {response.status_code}")


def extract_regional_intensity_forecast():
    sql_query = '''SELECT * FROM "c16b0e19-c02a-44a8-ba05-4db2c0545a2a" ORDER BY "_id" ASC LIMIT 100'''

    params = {
        'sql': sql_query
    }

    try:
        response = requests.get(
            'https://api.neso.energy/api/3/action/datastore_search_sql',
            params=parse.urlencode(params)
        )

        data = response.json()["result"]["records"]

        for record in data:
            if '_full_text' in record:
                del record['_full_text']
            if '_id' in record:
                record['region_id'] = record.pop('_id')

        with open('regional_intensity_forecast.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        print("Data saved to regional_intensity_forecast.csv")

    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e.response.text}")


if __name__ == "__main__":
    extract_national_co2_data_today()
    extract_regional_co2_data_today()
    extract_co2_intensity_factors_today()
    extract_regional_intensity_forecast()
