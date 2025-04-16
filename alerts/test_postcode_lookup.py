# pylint: skip-file
from postcode_lookup import get_region_from_postcode, find_provider_from_region, get_connection_to_db, find_provider_from_region_id
import pytest


def test_get_region_from_postcode():
    assert get_region_from_postcode('E1 7DB') == 'London'
    assert get_region_from_postcode('FK2 8FX') == 'Scotland'


def test_get_region_from_postcode_error():

    with pytest.raises(ValueError):
        get_region_from_postcode('12fsasd')
        get_region_from_postcode('sdfji0348')


def test_region_mappings_works():

    assert get_region_from_postcode("LL57 2DG") == "Wales"


def test_get_provider_from_region():
    db_connection = get_connection_to_db()
    db_cursor = db_connection.cursor()
    assert find_provider_from_region(db_cursor, 'London') == 6
    assert find_provider_from_region(db_cursor, 'Wales') == 2


def test_get_provider_from_region_fake_region():
    db_connection = get_connection_to_db()
    db_cursor = db_connection.cursor()
    with pytest.raises(ValueError):
        find_provider_from_region(db_cursor, 'Cairo')
        find_provider_from_region(db_cursor, 'fake')


def test_get_provider_from_region_id():
    db_connection = get_connection_to_db()
    db_cursor = db_connection.cursor()
    assert find_provider_from_region_id(db_cursor, 30) == (6, 'London')
    assert find_provider_from_region_id(db_cursor, 34) == (2, 'Wales')


def test_get_provider_from_region_id_fake_region_id():
    db_connection = get_connection_to_db()
    db_cursor = db_connection.cursor()
    with pytest.raises(ValueError):
        find_provider_from_region_id(db_cursor, 123)
