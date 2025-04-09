import requests
import os
import csv
import time
from datetime import datetime
from os.path import exists
from bs4 import BeautifulSoup
import pandas as pd
import urllib3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Providers

# - SSEN ///
# - Northern Powergrid
# - Electricty NW
# - SP Energy ///
# - UK Power Networks ///
# - National Grid ///


def national_gird_outage_data():
    '''Fetch and append unique power outage records for Midlands (National Grid).'''
    url = "https://connecteddata.nationalgrid.co.uk/dataset/d6672e1e-c684-4cea-bb78-c7e5248b62a2/resource/292f788f-4339-455b-8cc0-153e14509d4d/download/power_outage_ext.csv"

    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(current_dir, "national_grid_power_outages.csv")

    response = requests.get(url)
    response.raise_for_status()
    content = response.content.decode('utf-8').splitlines()
    reader = csv.DictReader(content)

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

    print(f"Appended {new_rows} new records to {save_path}")


def uk_power_networks_outage_data():
    '''Fetch and append unique UK Power Networks outage records.'''
    url = "https://ukpowernetworks.opendatasoft.com/api/explore/v2.1/catalog/datasets/ukpn-live-faults/records"
    filename = 'ukpowernetworks_outage.csv'
    file_exists = os.path.exists(filename)

    response = requests.get(url)
    if response.status_code != 200:
        print(
            f"Failed to fetch data. HTTP Status code: {response.status_code}")
        return

    data = response.json()

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

    print(f"Appended {new_rows} new records to '{filename}'.")


def ssen_outage_data():
    '''Fetch and append unique SSEN outage records'''
    url = "http://api.sse.com/powerdistribution/network/v3/api/faults"
    filename = 'ssen_outage_data.csv'
    file_exists = os.path.exists(filename)

    response = requests.get(url)
    if response.status_code != 200:
        print("Error fetching data from API")
        return

    data = response.json()

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

    print(f"Appended {new_rows} new records to '{filename}'.")


def sp_outage_scraper():
    '''Scrapes Scottish Power outage data and appends unique entries to CSV'''
    url = 'https://www.spenergynetworks.co.uk/pages/power_cuts_list.aspx'
    filename = 'sp_outage_data.csv'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, verify=False, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve the webpage.")
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

        affected_area = fields[4].find('span', class_='Value')
        affected_area = affected_area.text.strip() if affected_area else "N/A"

        if reference not in existing_ids:
            new_data.append({
                'incident_id': reference,
                'outage_start': created_on,
                'planned': status,
                'outage_end': estimated_on,
                'region': 'Scottish Power',
                'postcodes': affected_area
            })
            existing_ids.add(reference)

    if new_data:
        df_new = pd.DataFrame(new_data)
        if os.path.exists(filename):
            df_new.to_csv(filename, mode='a', index=False, header=False)
        else:
            df_new.to_csv(filename, index=False)
        print(f"Appended {len(new_data)} new outage records.")
    else:
        print("No new records to append.")


def scrape_northern_powergrid_map():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get("https://power.northernpowergrid.com/Powercuts/map")

        wait = WebDriverWait(driver, 15)

        try:
            popup_bg = wait.until(
                EC.presence_of_element_located((By.ID, "b72-PopupBG")))
            print("Popup found, clicking to dismiss...")
            ActionChains(driver).move_by_offset(10, 10).click().perform()
            time.sleep(1)
        except:
            print("No popup found or already dismissed.")

        try:
            power_cut_button = wait.until(
                EC.element_to_be_clickable((By.ID, "ButtonGroupItem6")))
            power_cut_button.click()
            print("Selected 'Current Power Cut' layer.")
        except:
            print("Failed to select the layer. Check button ID or visibility.")

        time.sleep(2)

        records = driver.find_elements(By.CSS_SELECTOR, ".record-list-item")
        print(f"Found {len(records)} records.")

        northern_power_outage_data = []

        for record in records:
            try:
                power_cut_id = record.find_element(
                    By.CSS_SELECTOR, ".mobile-right").text.strip()

                category = record.find_element(
                    By.CSS_SELECTOR, ".hide-tablet").text.strip() if record.find_elements(By.CSS_SELECTOR, ".hide-tablet") else "N/A"

                start_time = record.find_elements(
                    By.CSS_SELECTOR, ".OSFillParent")[0].text.strip()

                end_time = record.find_elements(
                    By.CSS_SELECTOR, ".OSFillParent")[1].text.strip()

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

                print(
                    f"Scraped: {power_cut_id}, {category}, {start_time}, {end_time}, {postcodes_str}, {premises_affected}")

            except Exception as e:
                print(f"Error with record: {e}")
                continue

        df = pd.DataFrame(northern_power_outage_data)
        print(df)

        df.to_csv("northern_power_outage_data.csv", index=False)
        print("Data saved to northern_power_outage_data.csv")

    finally:
        driver.quit()


if __name__ == "__main__":
    national_gird_outage_data()
    uk_power_networks_outage_data()
    ssen_outage_data()
    sp_outage_scraper()
    scrape_northern_powergrid_map()
