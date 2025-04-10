import csv
import logging
import os
import time
from datetime import datetime
from os.path import exists
import pandas as pd
import requests
import urllib3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NATIONAL_GRID_URL = "https://connecteddata.nationalgrid.co.uk/dataset/d6672e1e-c684-4cea-bb78-c7e5248b62a2/resource/292f788f-4339-455b-8cc0-153e14509d4d/download/power_outage_ext.csv"
UK_POWER_NETWORKS_URL = "https://ukpowernetworks.opendatasoft.com/api/explore/v2.1/catalog/datasets/ukpn-live-faults/records"
SSEN_URL = "http://api.sse.com/powerdistribution/network/v3/api/faults"
SP_URL = "https://www.spenergynetworks.co.uk/pages/power_cuts_list.aspx"
NORTHERN_POWER_URL = "https://power.northernpowergrid.com/Powercuts/map"
ELECTRIC_NW_URL = "https://www.enwl.co.uk/power-cuts/power-cuts-power-cuts-live-power-cut-information-fault-list/fault-list/?postcodeOrReferenceNumber="


def setup_chrome_driver():
    """Setup Chrome WebDriver with appropriate options for Docker environment"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')

    try:
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        logging.error("Failed to initialize Chrome driver: %s", e)
        raise


def national_gird_outage_data():
    '''Fetch and append unique power outage records for Midlands (National Grid).'''
    logging.info("Fetching data from National Grid.")
    url = NATIONAL_GRID_URL
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(current_dir, "national_grid_power_outages.csv")

    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.content.decode('utf-8').splitlines()
        reader = csv.DictReader(content)
    except requests.exceptions.RequestException as e:
        logging.error("Error fetching data from National Grid: %s", e)
        return

    existing_ids = set()
    if os.path.exists(save_path):
        with open(save_path, mode='r', encoding='utf-8') as f:
            existing = csv.DictReader(f)
            for row in existing:
                existing_ids.add(row['incident_id'])

    with open(save_path, mode='a', newline='', encoding='utf-8') as f:
        fieldnames = ['incident_id', 'outage_start',
                      'planned', 'outage_end', 'region', 'postcodes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if f.tell() == 0:
            writer.writeheader()

        new_rows = 0
        for row in reader:
            incident_id = row['Incident ID']
            if incident_id not in existing_ids:
                writer.writerow({
                    'incident_id': incident_id,
                    'outage_start': row['Start Time'],
                    'planned': row['Planned'],
                    'outage_end': row['ETR'],
                    'region': row['Region'],
                    'postcodes': row['Postcodes']
                })
                new_rows += 1
                existing_ids.add(incident_id)

    logging.info("Appended %s new records to %s", new_rows, save_path)


def uk_power_networks_outage_data():
    '''Fetch and append unique UK Power Networks outage records.'''
    logging.info("Fetching data from UK Power Networks.")
    url = UK_POWER_NETWORKS_URL
    filename = 'ukpowernetworks_outage.csv'
    file_exists = os.path.exists(filename)

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logging.error("Error fetching data from UK Power Networks: %s", e)
        return

    existing_ids = set()
    if file_exists:
        with open(filename, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_ids.add(row['incident_id'])

    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        fieldnames = ['incident_id', 'outage_start',
                      'planned', 'outage_end', 'region', 'postcodes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if f.tell() == 0:
            writer.writeheader()

        new_rows = 0
        for record in data['results']:
            incident_id = record.get('incidentreference')
            if incident_id not in existing_ids:
                writer.writerow({
                    'incident_id': incident_id,
                    'outage_start': record.get('planneddate', 'N/A'),
                    'planned': 'Planned' if record.get('powercuttype') == 'Planned' else 'Unplanned',
                    'outage_end': record.get('estimatedrestorationdate', 'N/A'),
                    'region': 'UK Power Networks',
                    'postcodes': record.get('postcodesaffected', 'N/A')
                })
                existing_ids.add(incident_id)
                new_rows += 1

    logging.info("Appended %s new records to '%s'.", new_rows, filename)


def ssen_outage_data():
    '''Fetch and append unique SSEN outage records'''
    logging.info("Fetching data from SSEN.")
    url = SSEN_URL
    filename = 'ssen_outage_data.csv'
    file_exists = os.path.exists(filename)

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logging.error("Error fetching data from SSEN: %s", e)
        return

    existing_ids = set()
    if file_exists:
        with open(filename, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_ids.add(row['incident_id'])

    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        fieldnames = ['incident_id', 'outage_start',
                      'planned', 'outage_end', 'region', 'postcodes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if f.tell() == 0:
            writer.writeheader()

        new_rows = 0
        for fault in data.get('faults', []):
            incident_id = fault.get('reference')
            if incident_id not in existing_ids:
                writer.writerow({
                    'incident_id': incident_id,
                    'outage_start': fault.get('loggedAtUtc', 'N/A'),
                    'planned': fault.get('type', 'N/A'),
                    'outage_end': fault.get('estimatedRestorationTimeUtc', 'N/A'),
                    'region': 'SSEN',
                    'postcodes': ', '.join(fault.get('affectedAreas', [])) or 'N/A'
                })
                existing_ids.add(incident_id)
                new_rows += 1

    logging.info("Appended %s new records to '%s'.", new_rows, filename)


def sp_outage_scraper():
    '''Scrapes Scottish Power outage data and appends unique entries to CSV'''
    logging.info("Starting scrape for Scottish Power outage data.")
    url = 'https://www.spenergynetworks.co.uk/pages/power_cuts_list.aspx'
    filename = 'sp_outage_data.csv'

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        driver = setup_chrome_driver()

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, verify=False, headers=headers)
        if response.status_code != 200:
            logging.error("Failed to retrieve the webpage.")
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('div', class_='Item')

        existing_ids = set()
        if os.path.exists(filename):
            df_existing = pd.read_csv(filename)
            existing_ids = set(df_existing['incident_id'])

        new_data = []

        for row in rows:
            fields = row.find_all('div', class_='Field')

            reference = fields[0].find('span', class_='Value')
            reference = reference.text.strip() if reference else "N/A"

            created_on = fields[1].find('span', class_='Value')
            created_on = created_on.text.strip() if created_on else "N/A"

            estimated_on = fields[2].find('span', class_='Value')
            estimated_on = estimated_on.text.strip() if estimated_on else "N/A"

            status = fields[3].find('span', class_='Value')
            status = status.text.strip() if status else "N/A"

            affected_postcodes = fields[4].find('span', class_='Value')
            affected_postcodes = affected_postcodes.text.strip() if affected_postcodes else "N/A"

            if reference not in existing_ids:
                new_data.append(
                    [reference, created_on, estimated_on, status, affected_postcodes])

        if new_data:
            with open(filename, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if os.path.getsize(filename) == 0:
                    writer.writerow(
                        ['incident_id', 'outage_start', 'outage_end', 'status', 'postcodes'])

                writer.writerows(new_data)

            logging.info("Appended %s new records to '%s'.",
                         len(new_data), filename)

        driver.quit()

    except Exception as e:
        logging.error("Error during scrape: %s", e)


def scrape_northern_powergrid_map():
    '''Scrapes Northern Powergrid website for outage data'''

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = setup_chrome_driver()

    try:
        driver.get(NORTHERN_POWER_URL)
        logging.info("Opened URL: %s", NORTHERN_POWER_URL)

        wait = WebDriverWait(driver, 15)

        try:
            popup_bg = wait.until(
                EC.presence_of_element_located((By.ID, "b72-PopupBG")))
            logging.info("Popup found, clicking to dismiss...")
            ActionChains(driver).move_by_offset(10, 10).click().perform()
            time.sleep(1)
        except:
            logging.warning("No popup found or already dismissed.")

        try:
            power_cut_button = wait.until(
                EC.element_to_be_clickable((By.ID, "ButtonGroupItem6"))
            )
            power_cut_button.click()
            logging.info("Selected 'Current Power Cut' layer.")
        except:
            logging.error(
                "Failed to select the layer. Check button ID or visibility.")

        time.sleep(2)

        records = driver.find_elements(By.CSS_SELECTOR, ".record-list-item")
        logging.info("Found %s records.", len(records))

        northern_power_outage_data = []

        for record in records:
            try:
                power_cut_id = record.find_element(
                    By.CSS_SELECTOR, ".mobile-right").text.strip()
                category = record.find_element(By.CSS_SELECTOR, ".hide-tablet").text.strip(
                ) if record.find_elements(By.CSS_SELECTOR, ".hide-tablet") else "N/A"

                start_time_elem = record.find_elements(
                    By.CSS_SELECTOR, 'div[style*="width: 12%"] span')
                end_time_elem = record.find_elements(
                    By.CSS_SELECTOR, 'div[style*="width: 15%"] span')

                start_time = start_time_elem[0].text.strip(
                ) if start_time_elem else "N/A"
                end_time = end_time_elem[0].text.strip(
                ) if end_time_elem else "N/A"

                postcodes = []
                postcode_elements = record.find_elements(
                    By.CSS_SELECTOR, ".list-group.inline-postcodes span[data-expression]")
                for postcode in postcode_elements:
                    postcodes.append(postcode.text.strip())
                postcodes_str = ", ".join(postcodes)

                premises_affected = record.find_elements(
                    By.CSS_SELECTOR, ".hide-desktop")[2].text.strip()

                northern_power_outage_data.append({
                    "Power Cut ID": power_cut_id,
                    "Category": category,
                    "Start Time": start_time,
                    "End Time": end_time,
                    "Postcodes Affected": postcodes_str,
                    "Premises Affected": premises_affected
                })

                logging.info(
                    "Scraped: %s, %s, %s, %s, %s, %s", {power_cut_id}, {category}, {start_time}, {end_time}, {postcodes_str}, {premises_affected})

            except Exception as e:
                logging.error("Error with record: %s", e)
                continue

        df = pd.DataFrame(northern_power_outage_data)
        logging.info("Data frame created: %s", df.head())

        df.to_csv("northern_power_outage_data.csv", index=False)
        logging.info("Data saved to northern_power_outage_data.csv")

    finally:
        driver.quit()


def electric_nw_outage_data():
    '''Scrapes the Electric Northwest power cut website for data about outages'''

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = setup_chrome_driver()

    try:
        url = ELECTRIC_NW_URL
        driver.get(url)
        logging.info("Opened URL: %s", url)
        time.sleep(5)

        total_faults = len(driver.find_elements(
            By.CLASS_NAME, "c-fault-listing__item"))
        logging.info("Found %s total faults.", total_faults)

        all_outages = []

        for i in range(total_faults):
            try:
                faults = driver.find_elements(
                    By.CLASS_NAME, "c-fault-listing__item")
                fault = faults[i]

                button = fault.find_element(
                    By.CLASS_NAME, "c-fault-listing__link")
                driver.execute_script("arguments[0].scrollIntoView();", button)
                button.click()
                time.sleep(3)

                detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                info_list = detail_soup.select(".c-fault-information__list")

                outage_details = {}
                for ul in info_list:
                    for li in ul.select("li"):
                        title = li.select_one("h3")
                        desc = li.select_one("p")
                        if title and desc:
                            outage_details[title.text.strip()
                                           ] = desc.text.strip()

                all_outages.append(outage_details)

                back_button = driver.find_element(
                    By.CLASS_NAME, "c-fault-back__link")
                driver.execute_script(
                    "arguments[0].scrollIntoView();", back_button)
                back_button.click()
                time.sleep(3)

            except Exception as e:
                logging.error("Error processing fault #%s: %s", i + 1, e)
                continue

        csv_filename = 'electric_nw_outage_data.csv'
        if all_outages:
            fieldnames = sorted(set(k for d in all_outages for k in d.keys()))
            with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in all_outages:
                    writer.writerow(row)
            logging.info(
                "Data successfully saved to %s", csv_filename)
        else:
            logging.warning("No outage data found.")

    finally:
        driver.quit()


def create_empty_csv_files():
    """Create empty CSV files with headers to prevent errors in the cleaning process"""

    csv_files = {
        'northern_power_outage_data.csv': ['Power Cut ID', 'Category', 'Start Time', 'End Time', 'Postcodes Affected', 'Premises Affected'],
        'electric_nw_outage_data.csv': ['Incident ID', 'Type', 'Start Time', 'End Time', 'Region', 'Postcodes'],
        'sp_outage_data.csv': ['incident_id', 'outage_start', 'outage_end', 'status', 'postcodes'],
    }

    for filename, headers in csv_files.items():
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            logging.info("Creating empty CSV file with headers: %s", filename)
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)


if __name__ == "__main__":
    national_gird_outage_data()
    uk_power_networks_outage_data()
    ssen_outage_data()

    try:
        sp_outage_scraper()
    except Exception as e:
        logging.error("Error in sp_outage_scraper: %s", e)

    try:
        scrape_northern_powergrid_map()
    except Exception as e:
        logging.error("Error in scrape_northern_powergrid_map: %s", e)

    try:
        electric_nw_outage_data()
    except Exception as e:
        logging.error("Error in electric_nw_outage_data: %s", e)

        create_empty_csv_files()
    except Exception as e:
        logging.error("Critical error in ETL process: %s", e)
        create_empty_csv_files()
