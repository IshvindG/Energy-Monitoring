# pylint: skip-file
import pytest
from unittest.mock import patch, mock_open, MagicMock
from newsletter.send_email import send_email_with_attachment, generate_email_body


def test_generate_email_body():
    email = """Dear FAKE,

It's that exciting time of the month again! Check out the attached newsletter for an exclusive
insight into recent energy prices, demands and more!

Your favourite energy team,
WattWatch"""
    assert generate_email_body("FAKE") == email


@patch("builtins.open", new_callable=mock_open, read_data=b"fake-pdf-content")
@patch("boto3.client")
def test_send_email_success(mock_boto_client, mock_file):
    mock_ses = MagicMock()
    mock_ses.send_raw_email.return_value = {"MessageId": "1234"}
    mock_boto_client.return_value = mock_ses

    with patch.dict("os.environ", {"SENDER_EMAIL": "fakeboss@fake.com"}):
        send_email_with_attachment(
            "report.pdf", "fakeunderling@fake.com", "FAKE")

    mock_boto_client.assert_called_once_with("ses", region_name="eu-west-2")
    mock_file.assert_called_once_with("report.pdf", "rb")
    mock_ses.send_raw_email.assert_called_once()


@patch("builtins.open", new_callable=mock_open, read_data=b"fake-pdf-content")
@patch("boto3.client")
def test_send_email_failure(mock_boto_client, mock_file, capsys):
    mock_ses = MagicMock()
    mock_ses.send_raw_email.side_effect = Exception("SES is down")
    mock_boto_client.return_value = mock_ses

    with patch.dict("os.environ", {"SENDER_EMAIL": "fakeboss@fake.com"}):
        send_email_with_attachment("report.pdf", "fake@fakemail.com", "FAKE")

    captured = capsys.readouterr()
    assert "Failed to send email: SES is down" in captured.out
