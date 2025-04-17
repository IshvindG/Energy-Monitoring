# pylint: skip-file
import pytest
import pandas as pd

from Home import latest_demand_metric, latest_price_metric, latest_generation_metric, latest_imports_metric


@pytest.fixture
def demand_df():
    return pd.DataFrame({
        'Energy Demand': [100, 200, 300, 400],
    })


@pytest.fixture
def price_df():
    return pd.DataFrame({
        'Price per MWH': [50, 60, 70, 80],
    })


@pytest.fixture
def generation_df():
    return pd.DataFrame({
        'fuel_category': ['Renewables', 'Interconnectors', 'Fossil', 'Renewables'],
        'mw_generated': [500, 200, 300, 400],
    })


def test_latest_demand_metric(demand_df):
    result = latest_demand_metric(demand_df)
    assert result == "400GW"


def test_latest_price_metric(price_df):
    result = latest_price_metric(price_df)
    assert result == "80"


def test_latest_generation_metric(generation_df):
    result = latest_generation_metric(generation_df)
    assert result == "1.20GW"


def test_latest_imports_metric(generation_df):
    result = latest_imports_metric(generation_df)
    assert result == "0.20GW"
