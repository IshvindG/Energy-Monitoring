# pylint: skip-file

import pytest
from unittest.mock import patch, MagicMock
import load_power_outage as lpo


@patch("load_power_outage.psycopg2.connect")
@patch("load_power_outage.pd.read_csv")
def test_upload_data_from_csv(mock_read_csv, mock_connect):
    mock_df = MagicMock()

    mock_df.iterrows.return_value = iter([
        (0, {
            'reference_id': 'ref123',
            'outage_start': '2023-01-01 10:00',
            'outage_end': '2023-01-01 11:00',
            'Provider_name': 'TestProvider',
            'planned': 'true'
        })
    ])
    mock_read_csv.return_value = mock_df

    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    with patch("load_power_outage.get_provider_id", return_value=1), \
            patch("load_power_outage.check_if_outage_exists", return_value=False), \
            patch("load_power_outage.insert_outage_data") as mock_insert:

        lpo.upload_data_from_csv("fakefile.csv")

        mock_connect.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
        mock_insert.assert_called_once()
