# pylint: skip-file
from fuel_types import FUEL_TYPES_URL, INTERCONNECTOR_URL, interconnector_map
import requests


def test_get_fuel_types_from_api():
    response = requests.get(FUEL_TYPES_URL)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert "COAL" in data
    assert "BIOMASS" in data


def test_interconnector_api():

    response = requests.get(INTERCONNECTOR_URL)

    assert response.status_code == 200

    data = response.json()
    interconnector = data[0]
    assert isinstance(data, list)
    assert "interconnectorId" in interconnector
    assert "interconnectorName" in interconnector
    assert "interconnectorBiddingZone" in interconnector


def test_interconnector_map():
    data = [{'ID': 123, "Name": "fake"}]

    assert interconnector_map(data) == {123: "fake"}
