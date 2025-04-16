# pylint: skip-file
import pytest
from unittest.mock import MagicMock
from datetime import datetime
from newsletter.newsletter import (
    format_dates,
    get_average_price_over_past_month,
    get_highest_price_over_past_month,
    get_lowest_price_over_past_month,
    get_total_demand_over_past_month,
    get_average_demand_per_day_over_past_month,
    get_highest_demand,
    get_lowest_demand,
    get_average_demand_historical,
    get_total_generation,
    get_total_renewable,
    get_average_carbon_intensity,
    get_region_with_best_avg_carbon_intensity,
    get_region_with_worst_avg_carbon_intensity,
    get_hour_with_best_avg_carbon_intensity,
    get_hour_with_worst_avg_carbon_intensity,
)


@pytest.fixture
def mock_cursor():
    return MagicMock()


@pytest.fixture
def date_range():
    return "2025-04-15 00:00:00", "2025-03-15 00:00:00"


def test_format_dates():
    from datetime import datetime
    date = datetime(2024, 1, 5, 13, 45, 12)
    assert format_dates(date) == "2024-01-05 13:45:12"


def test_get_average_price_over_past_month(mock_cursor, date_range):
    mock_cursor.fetchone.return_value = [105.5267]
    result = get_average_price_over_past_month(mock_cursor, *date_range)
    assert result == 105.53


def test_get_highest_price_over_past_month(mock_cursor, date_range):
    mock_cursor.fetchone.return_value = [
        234.9, datetime(2025, 4, 10, 12, 0, 0)]
    result = get_highest_price_over_past_month(mock_cursor, *date_range)
    assert result[0] == 234.9
    assert isinstance(result[1], str)


def test_get_lowest_price_over_past_month(mock_cursor, date_range):
    mock_cursor.fetchone.return_value = [
        80.123, datetime(2025, 4, 10, 12, 0, 0)]
    price, date = get_lowest_price_over_past_month(mock_cursor, *date_range)
    assert price == "80.123"
    assert isinstance(date, str)


def test_get_total_demand_over_past_month(mock_cursor, date_range):
    mock_cursor.fetchone.return_value = [9387432]
    assert get_total_demand_over_past_month(
        mock_cursor, *date_range) == 9387432


def test_get_average_demand_per_day_over_past_month(mock_cursor, date_range):
    mock_cursor.fetchone.return_value = [158203.567]
    result = get_average_demand_per_day_over_past_month(
        mock_cursor, *date_range)
    assert result == 158203.57


def test_get_highest_demand(mock_cursor, date_range):
    mock_cursor.fetchone.return_value = [
        45230, datetime(2025, 4, 10, 12, 0, 0)]
    result = get_highest_demand(mock_cursor, *date_range)
    assert result[0] == 45230
    assert isinstance(result[1], str)


def test_get_lowest_demand(mock_cursor, date_range):
    mock_cursor.fetchone.return_value = [
        12000, datetime(2025, 4, 10, 12, 0, 0)]
    result = get_lowest_demand(mock_cursor, *date_range)
    assert result[0] == 12000
    assert isinstance(result[1], str)


def test_get_average_demand_historical(mock_cursor):
    mock_cursor.fetchone.return_value = [123456.789]
    assert get_average_demand_historical(mock_cursor) == 123456.79


def test_get_total_generation(mock_cursor, date_range):
    mock_cursor.fetchone.return_value = [23400000]
    assert get_total_generation(mock_cursor, *date_range) == 23400000


def test_get_total_renewable(mock_cursor, date_range):
    mock_cursor.fetchone.return_value = [15400000]
    assert get_total_renewable(mock_cursor, *date_range) == 15400000


def test_get_average_carbon_intensity(mock_cursor, date_range):
    mock_cursor.fetchone.return_value = [148.98]
    assert get_average_carbon_intensity(mock_cursor, *date_range) == 148.98


def test_get_region_with_best_avg_carbon_intensity(mock_cursor, date_range):
    mock_cursor.fetchone.return_value = ["Scotland"]
    assert get_region_with_best_avg_carbon_intensity(
        mock_cursor, *date_range) == "Scotland"


def test_get_region_with_worst_avg_carbon_intensity(mock_cursor, date_range):
    mock_cursor.fetchone.return_value = ["London"]
    assert get_region_with_worst_avg_carbon_intensity(
        mock_cursor, *date_range) == "London"


def test_get_hour_with_best_avg_carbon_intensity(mock_cursor, date_range):
    mock_cursor.fetchone.return_value = [3]
    assert get_hour_with_best_avg_carbon_intensity(
        mock_cursor, *date_range) == 3


def test_get_hour_with_worst_avg_carbon_intensity(mock_cursor, date_range):
    mock_cursor.fetchone.return_value = [17]
    assert get_hour_with_worst_avg_carbon_intensity(
        mock_cursor, *date_range) == 17
