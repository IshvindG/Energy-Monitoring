"""API utility for submitting form to AWS API Gateway"""
import os
import requests
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

API_ENDPOINT_SUBSCRIBE = os.getenv("SUB_LINK")


@st.cache_resource
def submit_form(data):
    """Submit form data to API Endpoint"""
    try:
        response = requests.post(API_ENDPOINT_SUBSCRIBE, json=data, timeout=10)
        return response.status_code == 200
    except requests.RequestException as e:
        print("Error submitting form:", e)
        return False
