auth_register_201_example = {
    "application/json": {
        "name": "My amazing project",
        "client_id": "pm8GMaIXIhkjQ4iDfXLOvVUUcIKGYRnMlZYApbda",
        "client_secret": (
            "YhVjvIBc7TuRJSvO2wIi344ez5SEreXLksV7GjalLiKDpxfbiM8qfUb5sNvcwFOh"
            "BUVzGNdzmmHvfyt6yU3aGrN6TAbMW8EOkRMOwhyXkN1iDetmzMMcxLVELf00BR2e"
        ),
    }
}

auth_token_200_example = {
    "application/json": {
        "access_token": "DLBYIcfnKfolaXKcmMC8RIDCavc2hW",
        "scope": "read write groups",
        "expires_in": 36000,
        "token_type": "Bearer",
    }
}

auth_key_info_200_example = {
    "application/json": {
        "requests_this_minute": 2,
        "requests_today": 40,
        "rate_limit_model": "enhanced",
    }
}

auth_key_info_403_example = {"application/json": "Forbidden"}
