from test.constants import API_URL, KNOWN_ENVS

import aiohttp
import pytest

from api.utils import aiohttp as aiohttp_utils


def show_env_name():
    env_name = KNOWN_ENVS.get(API_URL, "unknown")
    message = f"with API {API_URL}" if env_name == "unknown" else ""
    print(f"Testing {env_name} environment {message}")


@pytest.fixture(scope="session", autouse=True)
async def aiohttp_session():
    async with aiohttp.ClientSession() as session:
        aiohttp_utils._SESSION = session
        yield
