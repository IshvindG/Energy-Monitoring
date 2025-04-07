import requests
import os


def download_power_outage_data():
    url = "https://connecteddata.nationalgrid.co.uk/dataset/d6672e1e-c684-4cea-bb78-c7e5248b62a2/resource/292f788f-4339-455b-8cc0-153e14509d4d/download/power_outage_ext.csv"

    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(current_dir, "national_grid_power_outages.csv")

    response = requests.get(url)
    response.raise_for_status()

    with open(save_path, "wb") as f:
        f.write(response.content)

    print(f"Downloaded and saved to {save_path}")


if __name__ == "__main__":
    download_power_outage_data()
