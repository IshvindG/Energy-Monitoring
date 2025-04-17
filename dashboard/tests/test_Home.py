# pylint: skip-file
import pytest
import pandas as pd

from Home import latest_demand_metric, latest_price_metric, latest_generation_metric, latest_imports_metric, get_duration, format_demand_data, format_price_data


def test_get_duration():
    assert get_duration("24h") == "24 hours"
    assert get_duration("1 week") == "1 week"
    assert get_duration("1 month") == "1 month"
    assert get_duration("other") == "24 hours"


def test_format_demand_data():
    data = [
        {"demand_at": "2025-04-01T00:00:00Z", "total_demand": 5000},
        {"demand_at": "2025-04-01T01:00:00Z", "total_demand": 6000},
    ]
    df = format_demand_data(data)
    assert list(df.columns).count("Energy Demand") == 1
    assert df["Energy Demand"].iloc[0] == "5.00"
    assert pd.api.types.is_datetime64_any_dtype(df["demand_at"])


def test_format_price_data():
    data = [
        {
            "price_at": "2025-04-01T00:00:00Z",
            "price_per_mwh": "75.1234",
            "price_id": 1,
            "updated_at": "2025-04-01T00:01:00Z"
        },
        {
            "price_at": "2025-04-01T01:00:00Z",
            "price_per_mwh": "70.0000",
            "price_id": 2,
            "updated_at": "2025-04-01T01:01:00Z"
        }
    ]
    df = format_price_data(data)
    assert "Price per MWH" in df.columns
    assert df["Price per MWH"].iloc[0] == "75.12"
    assert "price_id" not in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["price_at"])


def test_latest_demand_metric():
    df = pd.DataFrame({
        "Energy Demand": ["5.00", "6.00"]
    })
    latest, diff = latest_demand_metric(df)
    assert latest == "6.0GW"
    assert diff == "1.0"


def test_latest_price_metric():
    df = pd.DataFrame({
        "Price per MWH": ["100.0000", "97.1234"]
    })
    latest, diff = latest_price_metric(df)
    assert latest == "£100.0"
    assert diff == "2.877"


def test_latest_generation_metric():
    df = pd.DataFrame({
        "fuel_category": ["Solar", "Wind", "Interconnectors"],
        "mw_generated": [300, 400, 100]
    })
    result = latest_generation_metric(df)
    assert result == "0.70GW"


def test_latest_imports_metric():
    df = pd.DataFrame({
        "fuel_category": ["Solar", "Interconnectors", "Interconnectors"],
        "mw_generated": [300, -50, 150]
    })
    result = latest_imports_metric(df)
    assert result == "0.15GW"
