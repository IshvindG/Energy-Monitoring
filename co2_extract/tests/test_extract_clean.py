# pylint: skip-file

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
import pandas as pd
from requests.exceptions import RequestException


from co2_extract_clean import (
    get_time_range, build_sql_query, fetch_data, classify_intensity,
    clean_data, save_to_csv
)


def test_get_time_range_format():
    start, end = get_time_range(hours_back=1)
    fmt = '%Y-%m-%dT%H:%M:%S.000Z'
    datetime.strptime(start, fmt)
    datetime.strptime(end, fmt)
    delta = datetime.strptime(end, fmt) - datetime.strptime(start, fmt)
    assert abs(delta - timedelta(hours=1)) < timedelta(seconds=1)


def test_build_sql_query_includes_dates():
    query = build_sql_query('2024-01-01T00:00:00.000Z',
                            '2024-01-01T01:00:00.000Z')
    assert '2024-01-01T00:00:00.000Z' in query
    assert '2024-01-01T01:00:00.000Z' in query
    assert 'SELECT COUNT(*)' in query


@patch('co2_extract_clean.requests.get')
def test_fetch_data_success(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "result": {
            "records": [{"datetime": "2024-01-01T00:00:00", "_id": 1, "London": "120"}]
        }
    }
    mock_get.return_value = mock_response
    records = fetch_data("SELECT * FROM dummy")
    assert isinstance(records, list)
    assert records[0]["_id"] == 1


@patch('co2_extract_clean.requests.get')
def test_fetch_data_error(mock_get):
    mock_get.side_effect = RequestException("API error")
    records = fetch_data("SELECT * FROM dummy")
    assert records == []


@pytest.mark.parametrize("value, expected", [
    (None, 'unknown'),
    (float('nan'), 'unknown'),
    (100, 'Low'),
    (200, 'Medium'),
    (350, 'High'),
])
def test_classify_intensity(value, expected):
    result = classify_intensity(value)
    assert result == expected


def test_clean_data_structure():
    raw_records = [
        {"datetime": "2024-01-01T00:00:00", "_id": 1,
            "London": "100", "Manchester": "220"},
        {"datetime": "2024-01-01T00:30:00", "_id": 2,
            "London": "180", "Manchester": "320"},
    ]
    df = clean_data(raw_records)
    assert list(df.columns) == ['time_of_measure',
                                'region_name', 'measure', 'index']
    assert df.shape[0] == 4
    assert df['index'].tolist() == ['Low', 'Medium', 'Medium', 'High']


def test_save_to_csv(tmp_path):
    df = pd.DataFrame({
        'time_of_measure': ['2024-01-01T00:00:00'],
        'region_name': ['London'],
        'measure': [100],
        'index': ['Low']
    })
    file_path = tmp_path / "output.csv"
    save_to_csv(df, str(file_path))
    assert file_path.exists()
    saved_df = pd.read_csv(file_path)
    assert saved_df.equals(df)
