register_api_oauth2_201_example = {
    "application/json": {
        "name": "My amazing project",
        "client_id": "pm8GMaIXIhkjQ4iDfXLOvVUUcIKGYRnMlZYApbda",
        "client_secret": "YhVjvIBc7TuRJSvO2wIi344ez5SEreXLksV7GjalLiKDpxfbiM8qfUb5sNvcwFOhBUVzGNdzmmHvfyt6yU3aGrN6TAbMW8EOkRMOwhyXkN1iDetmzMMcxLVELf00BR2e",  # noqa: E501
    }
}

key_info_200_example = {
    "application/json": {
        "requests_this_minute": 2,
        "requests_today": 40,
        "rate_limit_model": "enhanced",
    }
}

key_info_403_example = {"application/json": "Forbidden"}

key_info_500_example = {"application/json": "Unknown API key rate limit type"}
