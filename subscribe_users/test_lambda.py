from subscribe_lambda import user_details, define_user_info
import json
import pytest


def test_define_user_info():

    response = response = {
        "body": json.dumps({
            "first_name": "first",
            "last_name": "last",
            "phone": "number",
            "postcode": "area",
            "region": "areas",
            "email": "fakeemail",
            "type": "newsletter",
            "fake": "fake",
            "fake2": "fake",
            "fake3": "fake"
        })
    }

    assert define_user_info(response) == {"first_name": "first",
                                          "last_name": "last",
                                          "phone": "number",
                                          "postcode": "area",
                                          "region": "areas",
                                          "email": "fakeemail",
                                          "type": "newsletter"}


def test_define_user_info_edge_case():
    response = {}
    with pytest.raises(ValueError):
        define_user_info(response)


def test_user_details():
    user = {"first_name": "first",
            "last_name": "last",
            "phone": "number",
            "postcode": "area",
            "region": "areas",
            "email": "fakeemail",
            "type": "newsletter"}
    assert user_details(user) == (
        "first", "last", "number", "fakeemail", "area", "areas")


def test_user_details_edge_case():
    user = {}
    with pytest.raises(ValueError):
        user_details(user)
