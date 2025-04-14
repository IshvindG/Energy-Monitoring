import unittest
from unittest.mock import patch, mock_open, MagicMock
import requests
import os

import extract_power_outage1


class TestOutageScraper(unittest.TestCase):

    @patch("extract_power_outage1.requests.get")
    @patch("builtins.open", new_callable=mock_open, read_data="incident_id\n123")
    @patch("os.path.exists")
    def test_national_grid_data_fetch_success(self, mock_exists, mock_open_fn, mock_get):
        mock_exists.return_value = True
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = (
            b"Incident ID,Start Time,Planned,ETR,Region,Postcodes\n"
            b"456,2023-01-01,Yes,2023-01-02,Midlands,AB1\n"
        )

        extract_power_outage1.national_gird_outage_data()
        self.assertTrue(mock_get.called)
        self.assertIn("power_outages", mock_open_fn.call_args[0][0])

    @patch("extract_power_outage1.requests.get")
    def test_national_grid_data_fetch_fail(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException(
            "Connection failed")
        result = extract_power_outage1.national_gird_outage_data()
        self.assertIsNone(result)

    @patch("extract_power_outage1.requests.get")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_uk_power_networks_outage_data(self, mock_open_fn, mock_exists, mock_get):
        mock_exists.return_value = False
        mock_get.return_value.json.return_value = {
            "results": [{
                "incidentreference": "abc123",
                "planneddate": "2023-01-01",
                "powercuttype": "Planned",
                "estimatedrestorationdate": "2023-01-02",
                "postcodesaffected": "AB1"
            }]
        }

        extract_power_outage1.uk_power_networks_outage_data()
        mock_get.assert_called_once()
        self.assertIn("ukpowernetworks", mock_open_fn.call_args[0][0])

    @patch("extract_power_outage1.requests.get")
    def test_uk_power_networks_api_fail(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("API down")
        result = extract_power_outage1.uk_power_networks_outage_data()
        self.assertIsNone(result)

    @patch("extract_power_outage1.requests.get")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_ssen_outage_data(self, mock_open_fn, mock_exists, mock_get):
        mock_exists.return_value = False
        mock_get.return_value.json.return_value = {
            "faults": [{
                "reference": "ssen123",
                "loggedAtUtc": "2023-01-01",
                "type": "Unplanned",
                "estimatedRestorationTimeUtc": "2023-01-02",
                "affectedAreas": ["AB1", "AB2"]
            }]
        }

        extract_power_outage1.ssen_outage_data()
        mock_get.assert_called_once()
        self.assertIn("ssen_outage_data.csv", mock_open_fn.call_args[0][0])

    @patch("extract_power_outage1.webdriver.Chrome")
    @patch("extract_power_outage1.Service")
    def test_setup_chrome_driver_success(self, mock_service, mock_chrome):
        driver_mock = MagicMock()
        mock_chrome.return_value = driver_mock
        driver = extract_power_outage1.setup_chrome_driver()
        self.assertEqual(driver, driver_mock)

    @patch("extract_power_outage1.webdriver.Chrome", side_effect=Exception("Driver fail"))
    def test_setup_chrome_driver_fail(self, mock_chrome):
        result = extract_power_outage1.setup_chrome_driver()
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
