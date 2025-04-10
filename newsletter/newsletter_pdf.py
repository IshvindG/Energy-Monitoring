
"""Script to generate a pdf report for the newsletter"""
from dotenv import load_dotenv
from xhtml2pdf import pisa
import newsletter


def convert_html_to_pdf(source_html, output_filename):
    """Convert HTML to PDF using xhtml2pdf."""
    try:
        with open(output_filename, "w+b") as result_file:
            pisa_status = pisa.CreatePDF(source_html, dest=result_file)
    except Exception as e:
        print(f"Error converting HTML to PDF: {e}")
        return False
    return pisa_status.err == 0


def create_html_report(data: dict):
    """Generate an HTML report based on the data."""

    highest_price, highest_price_date = data.get(
        "Highest Price", ("N/A", "N/A"))

    report_html = f"""
    <html>
        <head><title>Monthly Energy Report</title></head>
        <body>
            <h1>Monthly Energy Report</h1>
            <div style="margin-bottom: 20px;">
                <h3>KPI - Highest Price</h3>
                <p><strong>Price:</strong> €{highest_price}</p>
                <p><strong>Date:</strong> {highest_price_date}</p>
            </div>
            <div style="margin-bottom: 20px;">
                <h3>KPI - Lowest Price</h3>
                <p><strong>Price:</strong> €{data.get("Lowest Price", "N/A")}</p>
            </div>
            <div style="margin-bottom: 20px;">
                <h3>KPI - Total Demand</h3>
                <p><strong>Total Demand:</strong> {data.get("Total Demand", "N/A")} MWh</p>
            </div>
            <div style="margin-bottom: 20px;">
                <h3>KPI - Avg Daily Demand</h3>
                <p><strong>Avg Daily Demand:</strong> {data.get("Avg Daily Demand", "N/A")} MWh</p>
            </div>
            <div style="margin-bottom: 20px;">
                <h3>KPI - Highest Demand</h3>
                <p><strong>Highest Demand:</strong> {data.get("Highest Demand", "N/A")} MWh</p>
            </div>
            <div style="margin-bottom: 20px;">
                <h3>KPI - Lowest Demand</h3>
                <p><strong>Lowest Demand:</strong> {data.get("Lowest Demand", "N/A")} MWh</p>
            </div>
        </body>
    </html>
"""

    return report_html


def create_pdf_report(data: dict, filename: str):
    """Create a PDF report from the HTML data."""
    html_content = create_html_report(data)
    convert_html_to_pdf(html_content, filename)


def create_report_data():
    """Gathering all data from database"""
    db_connection = newsletter.get_connection_to_db()
    curr = db_connection.cursor()
    date_today, date_last_month = newsletter.get_dates()
    date_today = newsletter.format_dates(date_today)
    date_last_month = newsletter.format_dates(date_last_month)

    highest_price, highest_price_date = newsletter.get_highest_price_over_past_month(
        curr, date_today, date_last_month)

    report_data = {
        "Highest Price": (highest_price, highest_price_date),
        "Lowest Price": newsletter.get_lowest_price_over_past_month(curr,
                                                                    date_today,
                                                                    date_last_month),
        "Total Demand": newsletter.get_total_demand_over_past_month(curr,
                                                                    date_today,
                                                                    date_last_month),
        "Avg Daily Demand": newsletter.get_average_demand_per_day_over_past_month(curr,
                                                                                  date_today,
                                                                                  date_last_month),
        "Highest Demand": newsletter.get_highest_demand(curr, date_today, date_last_month),
        "Lowest Demand": newsletter.get_lowest_demand(curr, date_today, date_last_month),
    }

    return report_data


if __name__ == "__main__":
    load_dotenv()

    report_info = create_report_data()
    create_pdf_report(report_info, "monthly_report.pdf")
