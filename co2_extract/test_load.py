import pytest
import pandas as pd
from unittest.mock import patch, MagicMock, mock_open
from co2_load import connect_to_db, load_csv, insert_carbon_intensities


@patch("co2_load.psycopg2.connect")
def test_connect_to_db_success(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    conn, cur = connect_to_db()

    assert conn == mock_conn
    assert cur == mock_cursor
    mock_connect.assert_called_once()


@patch("co2_load.psycopg2.connect", side_effect=Exception("Connection error"))
def test_connect_to_db_failure(mock_connect):
    with pytest.raises(Exception, match="Connection error"):
        connect_to_db()


@patch("co2_load.pd.read_csv")
def test_load_csv(mock_read_csv):
    dummy_df = pd.DataFrame({"a": [1], "b": [2]})
    mock_read_csv.return_value = dummy_df

    result = load_csv("fake_path.csv")
    assert result.equals(dummy_df)
    mock_read_csv.assert_called_once_with("fake_path.csv")


def test_insert_carbon_intensities_success():
    df = pd.DataFrame([
        {
            "region_name": "North Wales and Merseyside",
            "index": "Low",
            "measure": 120.0,
            "time_of_measure": "2024-01-01T12:00:00"
        }
    ])

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [42]

    insert_carbon_intensities(df, mock_conn, mock_cursor)

    mock_cursor.execute.assert_any_call(
        "SELECT region_id FROM regions WHERE region_name = %s",
        ("North Wales & Merseyside",)
    )

    mock_cursor.execute.assert_any_call(
        """
                INSERT INTO carbon_intensities (index, forecast_measure, measure_at, region_id)
                VALUES (%s, %s, %s, %s)
            """,
        ("Low", 120.0, "2024-01-01T12:00:00", 42)
    )

    mock_conn.commit.assert_called_once()


def test_insert_carbon_intensities_missing_region(caplog):
    df = pd.DataFrame([
        {
            "region_name": "Unknown Region",
            "index": "High",
            "measure": 450.0,
            "time_of_measure": "2024-01-01T13:00:00"
        }
    ])

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None

    insert_carbon_intensities(df, mock_conn, mock_cursor)

    assert "Region not found in database: Unknown Region" in caplog.text
    mock_conn.commit.assert_called_once()
