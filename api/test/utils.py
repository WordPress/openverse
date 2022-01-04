from test.constants import API_URL, KNOWN_ENVS


def show_env_name():
    env_name = KNOWN_ENVS.get(API_URL, "unknown")
    message = f"with API {API_URL}" if env_name == "unknown" else ""
    print(f"Testing {env_name} environment {message}")
