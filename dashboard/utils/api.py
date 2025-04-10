<<<<<<< HEAD
"""API utility for submitting form to AWS API Gateway"""
=======
"""Script to connect dashboard form to subscribe lambda"""
>>>>>>> 95025e8 (updating dashboard to add unsubscribe page and tweaking lambdas)
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_ENDPOINT_SUBSCRIBE = os.getenv("SUB_LINK")


<<<<<<< HEAD
def submit_form(data):
    """Submit form data to API Endpoint"""
    try:
        response = requests.post(API_ENDPOINT, json=data, timeout=10)
=======
def submit_form(data: dict):
    """Submitting form to api gateway"""
    try:
        response = requests.post(API_ENDPOINT_SUBSCRIBE, json=data)
>>>>>>> 95025e8 (updating dashboard to add unsubscribe page and tweaking lambdas)
        return response.status_code == 200
    except requests.RequestException as e:
        print("Error submitting form:", e)
        return False
