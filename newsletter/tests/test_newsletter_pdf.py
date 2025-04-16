# pylint: skip-file
import pytest
from unittest.mock import patch, MagicMock, mock_open
from newsletter.newsletter_pdf import create_html_report, convert_html_to_pdf, create_pdf_report, create_report_data


sample_data = {
    "Highest Price": 120.5,
    "Highest Price Date": "2025-04-12 13:00:00",
    "Lowest Price": 50.25,
    "Lowest Price Date": "2025-03-18 03:00:00",
    "Total Demand": 450000,
    "Avg Daily Demand": 15000,
    "Highest Demand": 60000,
    "Highest Demand Date": "2025-03-20 15:00:00",
    "Lowest Demand": 10000,
    "Lowest Demand Date": "2025-03-25 04:00:00",
    "Total Generation": 480000,
    "Total Renewable": 200000,
    "Avg Price": 87.45,
    "Avg Carbon Intensity": 150,
    "Best Region": "North",
    "Worst Region": "South",
    "Best Hour": "02:00",
    "Worst Hour": "18:00",
    "percentage": 41.67
}


def test_create_html_report():
    html_template = "<html><body>{{Highest Price}} at {{Highest Price Date}}</body></html>"
    expected = "<html><body>120.5 at 2025-04-12 13:00:00</body></html>"

    with patch("builtins.open", mock_open(read_data=html_template)):
        html = create_html_report(sample_data, "fake_template.html")
        assert html == expected


def test_convert_html_to_pdf_success():
    with patch("builtins.open", mock_open()) as mocked_file:
        with patch("newsletter.newsletter_pdf.pisa.CreatePDF") as mock_pdf:
            mock_pdf.return_value.err = 0
            result = convert_html_to_pdf("<p>Test</p>", "output.pdf")
            assert result is True
            mock_pdf.assert_called_once()


def test_convert_html_to_pdf_failure():
    with patch("builtins.open", mock_open()) as mocked_file:
        with patch("newsletter.newsletter_pdf.pisa.CreatePDF", side_effect=Exception("Fail")):
            result = convert_html_to_pdf("<p>Test</p>", "output.pdf")
            assert result is False


def test_create_pdf_report():
    with patch("newsletter.newsletter_pdf.create_html_report") as mock_html:
        with patch("newsletter.newsletter_pdf.convert_html_to_pdf") as mock_pdf:
            mock_html.return_value = "<p>HTML</p>"
            mock_pdf.return_value = True
            create_pdf_report(sample_data, "report.pdf", "template.html")
            mock_html.assert_called_once()
            mock_pdf.assert_called_once()


@patch("newsletter.newsletter_pdf.newsletter")
def test_create_report_data(mock_newsletter):
    mock_conn = MagicMock()
    mock_newsletter.get_connection_to_db.return_value.cursor.return_value = mock_conn
    mock_newsletter.get_dates.return_value = (
        "2025-04-15 00:00:00", "2025-03-15 00:00:00")
    mock_newsletter.format_dates.side_effect = lambda x: x

    mock_newsletter.get_highest_price_over_past_month.return_value = (
        120.5, "2025-04-12 13:00:00")
    mock_newsletter.get_lowest_price_over_past_month.return_value = (
        50.25, "2025-03-18 03:00:00")
    mock_newsletter.get_total_demand_over_past_month.return_value = 450000
    mock_newsletter.get_average_demand_per_day_over_past_month.return_value = 15000
    mock_newsletter.get_highest_demand.return_value = (
        60000, "2025-03-20 15:00:00")
    mock_newsletter.get_lowest_demand.return_value = (
        10000, "2025-03-25 04:00:00")
    mock_newsletter.get_total_generation.return_value = 480000
    mock_newsletter.get_total_renewable.return_value = 200000
    mock_newsletter.get_average_price_over_past_month.return_value = 87.45
    mock_newsletter.get_average_carbon_intensity.return_value = 150
    mock_newsletter.get_region_with_best_avg_carbon_intensity.return_value = "North"
    mock_newsletter.get_region_with_worst_avg_carbon_intensity.return_value = "South"
    mock_newsletter.get_hour_with_best_avg_carbon_intensity.return_value = "02:00"
    mock_newsletter.get_hour_with_worst_avg_carbon_intensity.return_value = "18:00"

    data = create_report_data()
    assert data["Highest Price"] == 120.5
    assert data["Total Demand"] == 450000
    assert round(data["percentage"], 2) == round((200000 / 480000) * 100, 2)
