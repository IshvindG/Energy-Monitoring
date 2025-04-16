# pylint: skip-file
import pytest
import pandas as pd

from transform import filter_by_largest, transform_energy_generation, transform_energy_demand, transform_market_price


def test_filter_by_largest():
    data = {
        'timestamp': ['2025-04-01', '2025-04-02', '2025-04-03', '2025-04-02'],
        'value': [10, 20, 30, 40]
    }
    df = pd.DataFrame(data)

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    result_df = filter_by_largest('timestamp', df)

    expected_timestamp = pd.to_datetime('2025-04-03')
    assert all(result_df['timestamp'] == expected_timestamp)
    assert len(result_df) == 1
    assert result_df.iloc[0]['value'] == 30


def test_transform_energy_generation():
    data = {
        "dataset": ["FUELGEN", "FUELGEN", "FUELGEN"],
        "publishTime": ["2025-04-21T12:43:21", "2025-04-21T12:43:21", "2025-04-21T12:43:21"],
        "startTime": ["2025-04-21T12:43:21", "2025-04-21T12:43:21", "2025-04-21T12:43:21"],
        "settlementDate": ["2025-04-21", "2025-04-21", "2025-04-21"],
        "settlementPeriod": [1, 2, 1],
        "fuelType": ["Solar", "Wind", "Gas"],
        "generation": [2300, 231, 2133]
    }

    df = pd.DataFrame(data)
    transformed_data = transform_energy_generation(df)

    expected_data = {
        "publishTime": ["2025-04-21T12:43:21", "2025-04-21T12:43:21", "2025-04-21T12:43:21"],
        "fuelType": ["Solar", "Wind", "Gas"],
        "generation": [2300, 231, 2133]
    }
    expected_df = pd.DataFrame(expected_data)
    expected_df['publishTime'] = pd.to_datetime(
        expected_df['publishTime'], utc=True)

    assert list(transformed_data.columns) == list(expected_df.columns)
    assert list(transformed_data['publishTime']) == list(
        expected_df['publishTime'])


def test_transform_energy_demand():
    data = {
        "recordType": ["VD", "VD", "VD"],
        "startTime": ["2025-04-11T23:05:00Z", "2025-04-11T23:10:00Z", "2025-04-11T23:15:00Z"],
        "demand": [23760, 23663, 23577]
    }

    df = pd.DataFrame(data)

    transformed_data = transform_energy_demand(df)

    expected_data = {
        "startTime": ["2025-04-11T23:15:00Z"],
        "demand": [23577]
    }

    expected_df = pd.DataFrame(expected_data)
    expected_df['startTime'] = pd.to_datetime(
        expected_df['startTime'], utc=True)

    assert list(transformed_data.columns) == list(expected_df.columns)
    assert list(transformed_data['startTime']) == list(
        expected_df['startTime'])
    assert list(transformed_data['demand']) == list(
        expected_df['demand'])


def test_transform_market_price():
    data = {
        "startTime": ["2025-04-13T22:30:00Z", "2025-04-13T22:00:00Z", "2025-04-13T21:30:00Z"],
        "dataProvider": ["APXMIDP", "APXMIDP", "APXMIDP"],
        "settlementDate": ["2025-04-13", "2025-04-13", "2025-04-13"],
        "settlementPeriod": [47, 48, 49],
        "price": [86.86, 84.63, 76.64],
        "volume": [1631.8, 1492.3, 2671.5]
    }
    df = pd.DataFrame(data)

    transformed_data = transform_market_price(df)

    expected_data = {
        "startTime": ["2025-04-13T22:30:00Z"],
        "price": [86.86],
        "volume": [1631.8]
    }

    expected_df = pd.DataFrame(expected_data)
    expected_df['startTime'] = pd.to_datetime(
        expected_df['startTime'], utc=True)

    assert list(transformed_data.columns) == list(expected_df.columns)
    assert list(transformed_data['startTime']) == list(
        expected_df['startTime'])
    assert list(transformed_data['price']) == list(
        expected_df['price'])
    assert list(transformed_data['volume']) == list(
        expected_df['volume'])
