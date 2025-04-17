# pylint: skip-file
from database import get_connection_to_db
import pytest
from unittest.mock import patch, Mock
from api import submit_form


def test_submit_form_success():
    mock_data = {
        "first_name": "fake",
        "last_name": "man",
        "email": "fake_man@fakeemail.com",
        "type": "newsletter"
    }

    with patch("api.requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        assert submit_form(mock_data) is True
        mock_post.assert_called_once()


def test_submit_form_failure():
    mock_data = {
        "first_name": "fake",
        "email": "fake@fakeemail.com",
        "type": "alert"
    }

    with patch("api.requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        assert submit_form(mock_data) is False
        mock_post.assert_called_once()


def test_get_connection_to_db():
    mock_conn = Mock()

    with patch("database.psycopg2.connect", return_value=mock_conn) as mock_connect:
        connection = get_connection_to_db()

        mock_connect.assert_called_once()
        assert connection == mock_conn
