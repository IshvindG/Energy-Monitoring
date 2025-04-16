# pylint: skip-file
import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import Timeout


from extract import perform_http_get, get_demand_data, get_generation_data, get_interconnect_data, get_pricing_data


TEST_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELINST"


def test_http_import_real():
    result = perform_http_get(TEST_URL)
    assert result is not None


def test_http_import():
    result = perform_http_get("https://data.elexon.co.uk/bmrs/api/v1")
    assert result is None


def test_retrieve_demand_data():
    demand_data = get_demand_data()
    assert type(demand_data) is list
    assert demand_data is not None


def test_retrieve_pricing_data():
    pricing_data = get_pricing_data()
    assert type(pricing_data) is dict
    assert pricing_data is not None


def test_retrieve_interconnect_data():
    interconnect_data = get_interconnect_data()
    assert type(interconnect_data) is dict
    assert interconnect_data is not None


def test_retrieve_generation_data():
    generation_data = get_generation_data()
    assert type(generation_data) is dict
    assert generation_data is not None


@patch('extract.requests.get')
def test_perform_http_get_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{'data': [x for x in range(1, 11)]}]
    mock_get.return_value = mock_response

    url = "https://example.com/data"
    result = perform_http_get(url)

    mock_get.assert_called_once_with(url, timeout=10)
    assert result == [{'data': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}]


@patch('extract.requests.get')
def test_perform_http_get_failure(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    url = "https://example.com/data"
    result = perform_http_get(url)

    mock_get.assert_called_once_with(url, timeout=10)
    assert result is None


@patch('extract.requests.get')
def test_perform_http_get_timeout(mock_get):
    mock_get.side_effect = Timeout

    url = "https://example.com/data"
    with pytest.raises(Timeout):
        perform_http_get(url)
