# pylint: skip-file
from postcode_lookup import get_region_from_postcode, find_provider_from_region, get_connection_to_db, find_provider_from_region_id
import pytest
from unittest.mock import MagicMock


def test_get_region_from_postcode():
    assert get_region_from_postcode('E1 7DB') == 'London'
    assert get_region_from_postcode('FK2 8FX') == 'Scotland'


def test_get_region_from_postcode_error():

    with pytest.raises(ValueError):
        get_region_from_postcode('12fsasd')

    with pytest.raises(ValueError):
        get_region_from_postcode('sdfji0348')


def test_region_mappings_works():

    assert get_region_from_postcode("LL57 2DG") == "Wales"


def test_find_provider_from_region_success():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [(6,)]

    result = find_provider_from_region(mock_cursor, "London")
    assert result == 6
    mock_cursor.execute.assert_called_once()
    mock_cursor.fetchall.assert_called_once()


def test_find_provider_from_region_invalid():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = None

    with pytest.raises(ValueError):
        find_provider_from_region(mock_cursor, "Cairo")


def test_find_provider_from_region_id_success():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [(6, "London")]

    result = find_provider_from_region_id(mock_cursor, 30)
    assert result == (6, "London")


def test_find_provider_from_region_id_invalid():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = None

    with pytest.raises(ValueError):
        find_provider_from_region_id(mock_cursor, 1792394234)
