# pylint: skip-file
import pytest
from unittest.mock import patch, MagicMock
from alerts.send_alerts import (
    find_subscribers_from_db, create_subscriber_dict, find_provider_for_user,
    get_current_time_range, query_recent_outages, find_outage_info_for_user,
    alert_message_format, send_alert
)
from datetime import datetime, timedelta


@pytest.fixture
def mock_cursor():
    mock = MagicMock()
    mock.fetchall.return_value = [
        ("fake", "fakenumber", "fake@fake.com", None, 1, "fakefake")
    ]
    return mock


def test_find_subscribers_from_db(mock_cursor):
    users = find_subscribers_from_db(mock_cursor)
    assert isinstance(users, list)
    assert users[0][0] == "fake"


def test_create_subscriber_dict(mock_cursor):
    users = create_subscriber_dict(mock_cursor)
    assert users[0]["name"] == "fake"
    assert users[0]["email"] == "fake@fake.com"


@patch("alerts.send_alerts.find_provider_from_region_id")
def test_find_provider_for_user_with_region(mock_provider_lookup, mock_cursor):
    mock_provider_lookup.return_value = (123, "fakeregion")
    user = {"region_id": 1, "postcode": "fakefake"}
    user_with_provider = find_provider_for_user(mock_cursor, user)
    assert user_with_provider["provider_id"] == 123
    assert user_with_provider["region_name"] == "fakeregion"


@patch("alerts.send_alerts.get_region_from_postcode", return_value="fakeregion")
@patch("alerts.send_alerts.find_provider_from_region", return_value=321)
def test_find_provider_for_user_with_postcode(_, __, mock_cursor):
    user = {"postcode": "fakefake"}
    user_with_provider = find_provider_for_user(mock_cursor, user)
    assert user_with_provider["provider_id"] == 321
    assert user_with_provider["region_name"] == "fakeregion"


def test_get_current_time_range():
    past, now = get_current_time_range(5)
    assert isinstance(past, str)
    assert isinstance(now, str)


def test_query_recent_outages(mock_cursor):
    mock_cursor.fetchall.return_value = [
        (datetime.utcnow(), datetime.utcnow() + timedelta(minutes=10), True)
    ]
    outages = query_recent_outages(
        mock_cursor, 1, "2025-01-01 00:00:00", "2025-01-01 01:00:00")
    assert isinstance(outages, list)
    assert "outage_start" in outages[0]


def test_find_outage_info_for_user(mock_cursor):
    mock_cursor.fetchall.return_value = []
    user = {"provider_id": 1}
    user_outage = find_outage_info_for_user(mock_cursor, user)
    assert "outages" in user_outage
    assert isinstance(user_outage["outages"], list)


def test_alert_message_format_with_outage():
    user = {
        "name": "Alice",
        "region_name": "RegionX",
        "outages": [
            {"outage_start": "2025-01-01 10:00:00",
                "outage_end": "2025-01-01 12:00:00", "planned": True}
        ]
    }
    message = alert_message_format(user)
    assert "Alice" in message
    assert "RegionX" in message


def test_alert_message_format_no_outages():
    user = {
        "name": "Alice",
        "region_name": "RegionX",
        "outages": []
    }
    message = alert_message_format(user)
    assert message is None


@patch("alerts.send_alerts.boto3.client")
@patch("alerts.send_alerts.alert_message_format", return_value="Test Alert")
def test_send_alert_success(mock_msg_format, mock_boto_client):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    user = {
        "name": "Test",
        "email": "test@example.com",
        "region_name": "RegionX",
        "outages": [{"outage_start": "10:00", "outage_end": "12:00", "planned": True}]
    }
    send_alert(user)
    mock_client.send_raw_email.assert_called_once()
