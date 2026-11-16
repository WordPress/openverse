from unittest import mock

import pytest
from pook.interceptors import aiohttp as pook_aiohttp


@pytest.fixture(scope="session", autouse=True)
def pook_aiohttp_stream_writer():
    """
    Pass the ``stream_writer`` argument that aiohttp 3.14 made required.

    pook builds its mock ``ClientResponse`` without it, so every aiohttp
    request matched by a pook mock fails with a ``TypeError``. Remove this
    fixture once https://github.com/h2non/pook/issues/184 is released.
    """

    original = pook_aiohttp.HTTPResponse

    def http_response(*args, **kwargs):
        return original(*args, stream_writer=mock.Mock(), **kwargs)

    with mock.patch.object(pook_aiohttp, "HTTPResponse", http_response):
        yield
