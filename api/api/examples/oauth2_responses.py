auth_register_201_example = {
    "application/json": {
        "name": "My amazing project",
        "client_id": "<Openverse API client ID>",
        "client_secret": "<Openverse API client secret>",
    }
}

auth_token_200_example = {
    "application/json": {
        "access_token": "<Openverse API token>",
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
