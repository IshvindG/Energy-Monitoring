import requests

API_ENDPOINT = "https://v3xn7tths9.execute-api.eu-west-2.amazonaws.com/dev"


def submit_form(data):
    try:
        response = requests.post(API_ENDPOINT, json=data)
        return response.status_code == 200
    except Exception as e:
        print("Error submitting form:", e)
        return False
