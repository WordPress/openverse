from unittest import mock

import pytest
from oauth2 import oauth2
from requests import Response


FAKE_OAUTH_PROVIDER_NAME = "fakeprovider"


def _var_get_replacement(*args, **kwargs):
    values = {
        oauth2.OAUTH2_TOKEN_KEY: {
            FAKE_OAUTH_PROVIDER_NAME: {
                "access_token": "fakeaccess",
                "refresh_token": "fakerefresh",
            }
        },
        oauth2.OAUTH2_AUTH_KEY: {FAKE_OAUTH_PROVIDER_NAME: "fakeauthtoken"},
        oauth2.OAUTH2_PROVIDERS_KEY: {
            FAKE_OAUTH_PROVIDER_NAME: {
                "client_id": "fakeclient",
                "client_secret": "fakesecret",
            }
        },
    }
    return values[args[0]]


@pytest.fixture
def oauth_provider_var_mock():
    with mock.patch("oauth2.oauth2.Variable") as MockVariable:
        MockVariable.get.side_effect = _var_get_replacement
        yield MockVariable


def _make_response(*args, **kwargs):
    """
    Mock the request used during license URL validation.

    Most times the results of this function are expected to end with a `/`, so if the
    URL provided does not we add it.
    """
    response: Response = mock.Mock(spec=Response)
    if args:
        response.ok = True
        url = args[0]
        if isinstance(url, str) and not url.endswith("/"):
            url += "/"
        response.url = url
    return response


@pytest.fixture(autouse=True)
def requests_get_mock():
    """
    Mock request.get calls that occur during testing.

    This is primarily done by the `common.urls.rewrite_redirected_url` function.
    """
    with mock.patch("common.urls.requests_get", autospec=True) as mock_get:
        mock_get.side_effect = _make_response
        yield


@pytest.fixture
def freeze_time(monkeypatch):
    """
    Patch the `datetime.datetime.now` function to return a fixed, settable time.

    This effectively freezes time.
    https://stackoverflow.com/a/28073449 CC BY-SA 3.0
    """
    import datetime

    original = datetime.datetime

    class FreezeMeta(type):
        def __instancecheck__(self, instance):
            if type(instance) == original or type(instance) == Freeze:
                return True

    class Freeze(datetime.datetime):
        __metaclass__ = FreezeMeta

        @classmethod
        def freeze(cls, val):
            cls.frozen = val

        @classmethod
        def now(cls):
            return cls.frozen

        @classmethod
        def delta(cls, timedelta=None, **kwargs):
            """Move time fwd/bwd by the delta."""
            from datetime import timedelta as td

            if not timedelta:
                timedelta = td(**kwargs)
            cls.frozen += timedelta

    monkeypatch.setattr(datetime, "datetime", Freeze)
    Freeze.freeze(original.now())
    return Freeze
