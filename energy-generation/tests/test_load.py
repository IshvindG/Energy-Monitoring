# pylint: skip-file
import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import Timeout
from load import load_energy_solar_data, load_energy_generation_data, load_energy_demand_data, load_market_price_data


@patch('load.get_connection')
@patch('load.get_cursor')
def test_load_energy_generation_data(mock_get_cursor, mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_get_cursor.return_value = mock_cursor

    data = [
        {'generation': 300.0, 'fuelType': 'WIND',
            'publishTime': '2024-01-01T03:00:00Z'},
        {'generation': 450.5, 'fuelType': 'WIND',
            'publishTime': '2024-01-01T04:00:00Z'}
    ]

    load_energy_generation_data(data)

    expected_rows = [
        (300.0, 'WIND', '2024-01-01T03:00:00Z'),
        (450.5, 'WIND', '2024-01-01T04:00:00Z')
    ]
    mock_cursor.executemany.assert_called_once()
    args, _ = mock_cursor.executemany.call_args
    assert args[0].strip().startswith("INSERT INTO generations")
    assert list(args[1]) == expected_rows

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch('load.get_connection')
@patch('load.get_cursor')
def test_load_market_price_data(mock_get_cursor, mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_get_cursor.return_value = mock_cursor

    data = [
        {'startTime': '2024-01-01T05:00:00Z', 'price': 75.25}
    ]

    load_market_price_data(data)

    expected_row = ('2024-01-01T05:00:00Z', 75.25)
    mock_cursor.execute.assert_called_once()
    args, _ = mock_cursor.execute.call_args
    assert args[0].strip().startswith("INSERT INTO prices")
    assert args[1] == expected_row

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch('load.get_connection')
@patch('load.get_cursor')
def test_load_energy_demand_data(mock_get_cursor, mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_get_cursor.return_value = mock_cursor

    data = [
        {'startTime': '2024-01-01T06:00:00Z', 'demand': 10250.0}
    ]

    load_energy_demand_data(data)

    expected_row = ('2024-01-01T06:00:00Z', 10250.0)
    mock_cursor.execute.assert_called_once()
    args, _ = mock_cursor.execute.call_args
    assert args[0].strip().startswith("INSERT INTO demands")
    assert args[1] == expected_row

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch('load.get_connection')
@patch('load.get_cursor')
def test_load_energy_solar_data(mock_get_cursor, mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_get_cursor.return_value = mock_cursor

    data = [
        {'generation_mw': 100.5, 'fuelType': 'SOLAR',
            'publishTime': '2024-01-01T00:00:00Z'},
        {'generation_mw': 150.0, 'fuelType': 'SOLAR',
            'publishTime': '2024-01-01T01:00:00Z'}
    ]

    load_energy_solar_data(data)

    expected_values = [
        (100.5, 'SOLAR', '2024-01-01T00:00:00Z'),
        (150.0, 'SOLAR', '2024-01-01T01:00:00Z')
    ]
    mock_cursor.executemany.assert_called_once()
    args, _ = mock_cursor.executemany.call_args
    assert args[0].strip().startswith("INSERT INTO generations")
    assert list(args[1]) == expected_values

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
