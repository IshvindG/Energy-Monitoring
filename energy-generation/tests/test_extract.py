# pylint: skip-file
import pytest

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
