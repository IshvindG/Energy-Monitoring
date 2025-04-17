# pylint: skip-file

import pytest
import pandas as pd
import numpy as np
import os
from unittest import mock
from unittest.mock import patch, mock_open, MagicMock
import clean_power_outage1 as cpo

CLEAN_CSV = 'clean_power_outage_data.csv'


@pytest.fixture(autouse=True)
def cleanup_csv():
    if os.path.exists(CLEAN_CSV):
        os.remove(CLEAN_CSV)
    yield
    if os.path.exists(CLEAN_CSV):
        os.remove(CLEAN_CSV)


def test_create_empty_clean_csv_creates_file():
    cpo.create_empty_clean_csv()
    assert os.path.exists(CLEAN_CSV)
    df = pd.read_csv(CLEAN_CSV)
    expected_columns = ['reference_id', 'outage_start',
                        'outage_end', 'Provider_name', 'planned']
    assert list(df.columns) == expected_columns
    assert df.empty


def test_create_empty_clean_csv_does_not_overwrite_existing_file():
    df = pd.DataFrame({'reference_id': [123]})
    df.to_csv(CLEAN_CSV, index=False)

    with patch("logging.info") as mock_log:
        cpo.create_empty_clean_csv()
        mock_log.assert_any_call("Clean CSV already exists.")


@patch('pandas.read_csv')
@patch('pandas.DataFrame.to_csv')
def test_clean_electric_nw_adds_new_data(mock_to_csv, mock_read_csv):
    input_df = pd.DataFrame({
        'Reference': ['REF123'],
        'First reported at': ['2023-01-01 10:00'],
        'Estimated time of restoration': ['2023-01-01 14:00']
    })
    mock_read_csv.side_effect = [input_df, pd.DataFrame(
        columns=['reference_id'])]

    cpo.clean_electric_nw()

    assert mock_to_csv.called
    args, kwargs = mock_to_csv.call_args
    assert kwargs['mode'] == 'a'
    assert kwargs['header'] is False


@patch('pandas.read_csv')
@patch('pandas.DataFrame.to_csv')
def test_clean_national_grid_adds_data(mock_to_csv, mock_read_csv):
    input_df = pd.DataFrame({
        'incident_id': ['NG123'],
        'outage_start': ['2023-01-01 08:00'],
        'outage_end': ['2023-01-01 12:00'],
        'planned': ['true']
    })
    mock_read_csv.side_effect = [
        input_df, pd.DataFrame(columns=['reference_id'])]

    cpo.clean_national_grid()
    assert mock_to_csv.called


@patch('pandas.read_csv')
@patch('pandas.DataFrame.to_csv')
def test_clean_sp_handles_status_and_nan(mock_to_csv, mock_read_csv):
    input_df = pd.DataFrame({
        'incident_id': ['SP456'],
        'outage_start': ['2023-01-01 11:00'],
        'outage_end': ['2023-01-01 13:00'],
        'status': ['live']
    })
    mock_read_csv.side_effect = [
        input_df, pd.DataFrame(columns=['reference_id'])]

    cpo.clean_sp()
    assert mock_to_csv.called


def test_clean_northern_power_skips_on_missing_file():
    with patch("os.path.exists", return_value=False):
        with patch("logging.warning") as mock_warn:
            cpo.clean_northern_power()
            mock_warn.assert_any_call(
                "northern_power_outage_data.csv is empty or doesn't exist. Skipping processing.")


@patch('pandas.read_csv')
@patch('pandas.DataFrame.to_csv')
def test_clean_ssen_adds_data(mock_to_csv, mock_read_csv):
    input_df = pd.DataFrame({
        'incident_id': ['SSE789'],
        'outage_start': ['2023-01-01 09:00'],
        'outage_end': ['2023-01-01 10:00'],
        'planned': ['LV']
    })
    mock_read_csv.side_effect = [
        input_df, pd.DataFrame(columns=['reference_id'])]

    cpo.clean_ssen()
    assert mock_to_csv.called


@patch('pandas.read_csv')
@patch('pandas.DataFrame.to_csv')
def test_clean_uk_power_adds_data(mock_to_csv, mock_read_csv):
    input_df = pd.DataFrame({
        'incident_id': ['UKP999'],
        'outage_start': ['2023-01-01 07:00'],
        'outage_end': ['2023-01-01 08:30'],
        'planned': ['Planned']
    })
    mock_read_csv.side_effect = [
        input_df, pd.DataFrame(columns=['reference_id'])]

    cpo.clean_uk_power()
    assert mock_to_csv.called
