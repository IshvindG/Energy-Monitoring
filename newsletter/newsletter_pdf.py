
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


def create_html_report(data: dict, template_path: str) -> str:
    """Generate an HTML report by replacing placeholders in the HTML template."""
    try:
        with open(template_path, "r", encoding="utf-8") as file:
            html_template = file.read()

        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            html_template = html_template.replace(placeholder, str(
                round(value, 2)) if isinstance(value, float) else str(value))

        return html_template

    except FileNotFoundError:
        print(f"Error: Template file '{template_path}' not found.")
        return ""


def create_pdf_report(data: dict, filename: str, template_path: str):
    """Create a PDF report from the HTML data."""
    html_content = create_html_report(data, template_path)
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
    lowest_price, lowest_price_date = newsletter.get_lowest_price_over_past_month(
        curr, date_today, date_last_month)
    highest_demand, highest_demand_date = newsletter.get_highest_demand(
        curr, date_today, date_last_month)
    lowest_demand, lowest_demand_date = newsletter.get_lowest_demand(
        curr, date_today, date_last_month)

    report_data = {
        "Highest Price": highest_price,
        "Highest Price Date": highest_price_date,
        "Lowest Price": lowest_price,
        "Lowest Price Date": lowest_price_date,
        "Total Demand": newsletter.get_total_demand_over_past_month(curr,
                                                                    date_today,
                                                                    date_last_month),
        "Avg Daily Demand": newsletter.get_average_demand_per_day_over_past_month(curr,
                                                                                  date_today,
                                                                                  date_last_month),
        "Highest Demand": highest_demand,
        "Highest Demand Date": highest_demand_date,
        "Lowest Demand": lowest_demand,
        "Lowest Demand Date": lowest_demand_date,
        "Total Generation": newsletter.get_total_generation(curr, date_today, date_last_month),
        "Total Renewable": newsletter.get_total_renewable(curr, date_today, date_last_month),
        "Avg Price": newsletter.get_average_price_over_past_month(curr, date_today, date_last_month),
        "Avg Carbon Intensity": newsletter.get_average_carbon_intensity(curr, date_today, date_last_month),
        "Best Region": newsletter.get_region_with_best_avg_carbon_intensity(curr, date_today, date_last_month),
        "Worst Region": newsletter.get_region_with_worst_avg_carbon_intensity(curr, date_today, date_last_month),
        "Best Hour": newsletter.get_hour_with_best_avg_carbon_intensity(curr, date_today, date_last_month),
        "Worst Hour": newsletter.get_hour_with_worst_avg_carbon_intensity(curr, date_today, date_last_month),
        "percentage": (newsletter.get_total_renewable(curr, date_today, date_last_month) / newsletter.get_total_generation(curr, date_today, date_last_month)) * 100
    }

    return report_data


if __name__ == "__main__":
    load_dotenv()

    report_info = create_report_data()
    create_pdf_report(report_info, "monthly_report.pdf", "newsletter.html")
