"""API utility for submitting form to AWS API Gateway"""
import requests

API_ENDPOINT = "https://v3xn7tths9.execute-api.eu-west-2.amazonaws.com/dev"


def submit_form(data):
    """Submit form data to API Endpoint"""
    try:
        response = requests.post(API_ENDPOINT, json=data, timeout=10)
        return response.status_code == 200
    except requests.RequestException as e:
        print("Error submitting form:", e)
        return False
