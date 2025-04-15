"""Script to connect dashboard form to unsubscribe lambda"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_ENDPOINT_UNSUBSCRIBE = os.getenv("UNSUB_LINK")


def submit_form(data: dict):
    """Submitting form to lambda using api gateway"""
    try:
        response = requests.post(
            API_ENDPOINT_UNSUBSCRIBE, json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print("Error submitting form:", e)
        return False
