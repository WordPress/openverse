from http.client import HTTPResponse
from urllib.request import urlopen

from decouple import config


SENSITIVE_TERMS_URL = config(
    "SENSITIVE_TERMS_URL",
    default="http://localhost:8001/static/mock_sensitive_terms.txt",
)


def get_sensitive_terms() -> list[str]:
    response: HTTPResponse = urlopen(SENSITIVE_TERMS_URL)
    return [line.decode("utf-8") for line in response.readlines()]
