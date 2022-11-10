import logging
from collections.abc import Collection
from typing import Any, NamedTuple

from airflow.exceptions import AirflowSkipException
from airflow.models import Variable
from requests_oauthlib import OAuth2Session


log = logging.getLogger(__name__)


class OauthProvider(NamedTuple):
    """Representation of the information needed to define an OAuth2 provider."""

    name: str
    auth_url: str
    refresh_url: str


OAUTH2_TOKEN_KEY = "OAUTH2_ACCESS_TOKENS"
OAUTH2_AUTH_KEY = "OAUTH2_AUTH_KEYS"
OAUTH2_PROVIDERS_KEY = "OAUTH2_PROVIDER_SECRETS"
OAUTH_PROVIDERS = [
    OauthProvider(
        name="freesound",
        auth_url="https://freesound.org/apiv2/oauth2/access_token/",
        refresh_url="https://freesound.org/apiv2/oauth2/access_token/",
    ),
]


def _var_get(key: str) -> dict[str, Any]:
    """
    Helper function for Variable retrieval with deserialization and dictionary default.
    """
    return Variable.get(key, default_var={}, deserialize_json=True)


def _update_tokens(
    provider_name: str,
    tokens: dict[str, str],
) -> None:
    """
    Update the access/refresh tokens for a specific provider in the Airflow Variable
    store. This update does not affect the tokens for any other existing providers.
    """
    log.info(f"Updating tokens for provider: {provider_name}")
    current_tokens = _var_get(OAUTH2_TOKEN_KEY)
    current_tokens[provider_name] = {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
    }
    Variable.set(OAUTH2_TOKEN_KEY, current_tokens, serialize_json=True)


def _get_provider_secrets(
    name: str, provider_secrets: dict[str, dict] = None
) -> dict[str, str]:
    """
    Retrieve provider secrets from the Airflow Variable store. Optionally provide
    a previously retrieved Variable value for improved performance.

    Providers are expected to *at least* have a `client_id`, and may have more
    information defined as necessary.
    """
    if provider_secrets is None:
        provider_secrets = _var_get(OAUTH2_PROVIDERS_KEY)
    secrets = provider_secrets.get(name)
    if secrets is None or "client_id" not in secrets:
        raise ValueError(
            f"Authorization requested for provider {name} but no secrets "
            f"were provided! Add secrets to the {OAUTH2_PROVIDERS_KEY} Variable and"
            f" ensure the provider has a client_id."
        )
    return secrets


def get_oauth_client(provider_name: str) -> OAuth2Session:
    """
    Create an OAuth2 client. This client behaves like a `requests.Session` instance,
    but will automatically add the authorization necessary for a particular provider.
    """
    secrets = _get_provider_secrets(provider_name)
    tokens = _var_get(OAUTH2_TOKEN_KEY)
    if provider_name not in tokens:
        raise KeyError(f"Access token not found for provider {provider_name}")
    return OAuth2Session(
        client_id=secrets["client_id"],
        token={**tokens[provider_name], "token_type": "Bearer"},
    )


def authorize_providers(providers: Collection[OauthProvider]) -> None:
    """
    Iterate through all of the specified providers and authorize those that may need it.
    The authorization flow will only be attempted if a provider has an authorization
    key defined in the Airflow Variable store.
    """
    provider_secrets = _var_get(OAUTH2_PROVIDERS_KEY)
    auth_tokens = _var_get(OAUTH2_AUTH_KEY)
    for provider in providers:
        # Only authorize if a token was provided
        if provider.name not in auth_tokens:
            continue
        auth_token = auth_tokens[provider.name]
        log.info(f"Attempting to authorize provider: {provider.name}")
        secrets = _get_provider_secrets(provider.name, provider_secrets)
        client = OAuth2Session(secrets["client_id"])
        # NOTE: It's possible that the secrets being stored might not all be needed
        # here, and may in fact be rejected. We won't know until we add more providers.
        tokens = client.fetch_token(provider.auth_url, code=auth_token, **secrets)
        _update_tokens(provider.name, tokens)
        # Remove the auth token since it is no longer needed nor accurate
        auth_tokens.pop(provider.name)
        Variable.set(OAUTH2_AUTH_KEY, auth_tokens, serialize_json=True)


def refresh(provider: OauthProvider) -> None:
    """
    Refresh the tokens for a given provider. This will use the stored refresh token to
    attempt a fetch of a new access/refresh token pair. The new tokens will be updated
    in the Airflow Variable store. Raises an AirflowSkipException if no tokens are
    defined for the provider.
    """
    current_tokens = _var_get(OAUTH2_TOKEN_KEY)
    if provider.name not in current_tokens:
        raise AirflowSkipException(
            f"Provider {provider.name} had no stored tokens, it may need to be "
            f"authorized first."
        )
    refresh_token = current_tokens[provider.name]["refresh_token"]
    secrets = _get_provider_secrets(provider.name)
    client = OAuth2Session(secrets["client_id"])
    log.info(f"Attempting token refresh for provider: {provider.name}")
    # NOTE: Same as above, **secrets may be too much info for some requests.
    new_tokens = client.refresh_token(
        provider.refresh_url, refresh_token=refresh_token, **secrets
    )
    _update_tokens(provider.name, new_tokens)
