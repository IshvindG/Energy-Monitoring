# pylint: skip-file
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
