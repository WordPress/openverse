from unittest import mock

import pytest
from airflow.exceptions import AirflowSkipException

from oauth2 import oauth2
from tests.dags.conftest import FAKE_OAUTH_PROVIDER_NAME


FAKE_OAUTH_PROVIDER = oauth2.OauthProvider(
    FAKE_OAUTH_PROVIDER_NAME, "auth_url", "refresh_url"
)


def test_var_get():
    expected = "fakeval"
    with mock.patch("oauth2.oauth2.Variable") as MockVariable:
        MockVariable.get.return_value = expected
        actual = oauth2._var_get("key")
        assert actual == expected
        assert MockVariable.get.call_args == mock.call(
            "key", default_var={}, deserialize_json=True
        )


def test_update_tokens(oauth_provider_var_mock):
    new_tokens = {"access_token": "new_access", "refresh_token": "new_refresh"}
    oauth2._update_tokens(FAKE_OAUTH_PROVIDER_NAME, new_tokens)
    expected = {FAKE_OAUTH_PROVIDER_NAME: new_tokens}
    assert oauth_provider_var_mock.set.call_args.args == (
        oauth2.OAUTH2_TOKEN_KEY,
        expected,
    )


def test_update_tokens_does_not_affect_other_providers(oauth_provider_var_mock):
    oauth_provider_var_mock.get.side_effect = None
    oauth_provider_var_mock.get.return_value = {
        FAKE_OAUTH_PROVIDER_NAME: {},
        "other_provider": {"access_token": "foo", "refresh_token": "bar"},
    }
    new_tokens = {"access_token": "new_access", "refresh_token": "new_refresh"}
    expected = {
        FAKE_OAUTH_PROVIDER_NAME: new_tokens,
        "other_provider": {"access_token": "foo", "refresh_token": "bar"},
    }
    oauth2._update_tokens(FAKE_OAUTH_PROVIDER_NAME, new_tokens)
    assert oauth_provider_var_mock.set.call_args.args == (
        oauth2.OAUTH2_TOKEN_KEY,
        expected,
    )


@pytest.mark.parametrize(
    "expected",
    [
        # Happy path
        {"client_id": "foo", "other_secret": "bar"},
        # Missing client_id
        pytest.param(
            {"missing_client": "bar"},
            marks=pytest.mark.raises(exception=ValueError),
        ),
        # Missing altogether
        pytest.param(None, marks=pytest.mark.raises(exception=ValueError)),
    ],
)
def test_get_provider_secrets(expected):
    provider_secrets = {FAKE_OAUTH_PROVIDER_NAME: expected}
    actual = oauth2._get_provider_secrets(FAKE_OAUTH_PROVIDER_NAME, provider_secrets)
    assert actual == expected


def test_get_provider_secrets_pulled_if_not_provided(oauth_provider_var_mock):
    actual = oauth2._get_provider_secrets(FAKE_OAUTH_PROVIDER_NAME)
    assert actual["client_id"] == "fakeclient"


def test_get_oauth_client(oauth_provider_var_mock):
    actual = oauth2.get_oauth_client(FAKE_OAUTH_PROVIDER_NAME)
    assert actual.client_id == "fakeclient"
    # Ensure token type has been added
    assert actual.token["token_type"] == "Bearer"


def test_get_oauth_client_missing(oauth_provider_var_mock, monkeypatch):
    monkeypatch.setattr(oauth2, "_get_provider_secrets", lambda x: {})
    with pytest.raises(KeyError):
        oauth2.get_oauth_client("missing")


def test_authorize_providers(oauth_provider_var_mock):
    with mock.patch("oauth2.oauth2.OAuth2Session") as MockOAuth2Session:
        oauth2.authorize_providers([FAKE_OAUTH_PROVIDER])
        # A new token was fetched
        MockOAuth2Session.return_value.fetch_token.assert_called_once()
        # 2 variables were set, one to update the token and one to remove the auth
        assert oauth_provider_var_mock.set.call_count == 2
        # The auth tokens should now be empty, since the provider was authorized
        assert oauth_provider_var_mock.set.call_args.args[1] == {}


def test_authorize_providers_no_providers_to_auth(oauth_provider_var_mock):
    with mock.patch("oauth2.oauth2.OAuth2Session") as MockOAuth2Session:
        oauth2.authorize_providers(
            [oauth2.OauthProvider("other", auth_url="auth", refresh_url="refresh")]
        )
        MockOAuth2Session.assert_not_called()
        oauth_provider_var_mock.set.assert_not_called()


def test_refresh(oauth_provider_var_mock):
    with mock.patch("oauth2.oauth2.OAuth2Session") as MockOAuth2Session:
        oauth2.refresh(FAKE_OAUTH_PROVIDER)
        # A token was refreshed
        MockOAuth2Session.return_value.refresh_token.assert_called_once()
        # Tokens were updated
        assert oauth_provider_var_mock.set.call_args.args[0] == oauth2.OAUTH2_TOKEN_KEY


def test_refresh_no_tokens(oauth_provider_var_mock):
    provider = oauth2.OauthProvider("other", auth_url="auth", refresh_url="refresh")
    with pytest.raises(AirflowSkipException):
        oauth2.refresh(provider)
