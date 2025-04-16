from subscribe_lambda import user_details


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
