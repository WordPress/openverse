# OAuth2 Setup

## TL;DR

- Provider secrets (e.g. `client_id`, etc.) are stored in the
  `OAUTH2_PROVIDER_SECRETS` Variable.
- Authorization tokens (one time use) are stored in `OAUTH2_AUTH_KEYS`.
- Access/refresh token pairs are stored in `OAUTH2_ACCESS_TOKENS`.
- The Authorization DAG can be run as needed to authorize (or re-authorize)
  providers.
- The Token Refresh DAG is run every 12 hours and refreshes all tokens currently
  stored.
- Use the [`OAuth2DelayedRequester`](../common/requester.py) in a provider API
  script that requires OAuth2

## Overview

The functions and DAGs defined in this module provide a mechanism for generating
and maintaining the tokens necessary for interacting with sources that require
OAuth2 authentication.

OAuth2 providers are authenticated through a three-step mechanism:

1. Initiate authorization
2. Use authorization to create authentication tokens
3. (sometime later) Refresh the authentication tokens as needed

The authentication tokens that are created as a result of step 2 above can be
used in subsequent requests to the service to access resources that are only
made available to authenticated clients. The expiration time for an access token
differs by service. If a token expires before it is refreshed, the authorization
step will need to be restarted from step 1.

## Variables

We are using three Airflow variables to store the information related to OAuth2:

- `OAUTH2_PROVIDER_SECRETS`
- `OAUTH2_AUTH_KEYS`
- `OAUTH2_ACCESS_TOKENS`

### `OAUTH2_PROVIDER_SECRETS`

This Variable holds the provider secrets which are necessary for initiating
authorization. At minimum, this must have a `client_id` value per-provider, and
different providers may require more information.

**Format**:

```json
{
  "provider1": {
    "client_id": "<p_1_client>"
  },
  "provider2": {
    "client_id": "<p_2_client>",
    "client_secret": "<p_2_secret>"
  },
  "provider3": {
    "client_id": "<p_3_client>",
    "auth_level": "<sample_val>"
  }
}
```

### `OAUTH2_AUTH_KEYS`

This Variable holds any authorization keys that are needed to generate an
access/refresh token pair for a provider. It will typically remain empty until
one (or more) providers need new keys. Once this Variable has been populated,
the Authorization DAG can be run.

**Format**:

```json
{
  "provider1": "<auth_key_1>",
  "provider2": "<auth_key_2>"
}
```

### `OAUTH2_ACCESS_TOKENS`

This variable holds the access/refresh token pairs for all authorized providers.
These values are updated automatically and **should not** need to be
touched/modified directly. The Authorization DAG and Token Refresh DAG will
populate it.

**Format**:

```json
{
  "provider1": {
    "access_token": "<p_1_access>",
    "refresh_token": "<p_1_refresh>"
  },
  "provider2": {
    "access_token": "<p_2_access>",
    "refresh_token": "<p_2_refresh>"
  }
}
```

## DAGs

### Authorization DAG

**File:** [`authorize_dag.py`](authorize_dag.py)

This DAG will use any available authorization tokens to generate an
access/refresh token pair for a provider. It is run as-needed once the
appropriate Variable has been updated.

### Token Refresh DAG

**File:** [`token_refresh_dag.py`](token_refresh_dag.py)

This DAG refreshes the access/token pairs for all providers. In order to prevent
tokens from expiring, it is scheduled every 12 hours.

If a provider is defined but it does not have any access/token pairs entered,
the task for that provider will be skipped. If a provider's keys have expired,
the refresh (and the task) will fail.

## Authorization URLs

Each provider uses a different base URL for initiating the authorization
process. This library can assist with generating a `client_id`-specific URL for
each provider. In order to create an authorization URL, the provider's secrets
must be present (see [above](#oauth2_provider_secrets)).

Example:

```python
In [1]: import oauth2

In [2]: client = oauth2.get_oauth_client("freesound")

In [3]: client.authorization_url("https://freesound.org/apiv2/oauth2/authorize/")
Out[3]:
('https://freesound.org/apiv2/oauth2/authorize/?response_type=code&client_id=[redacted]&state=aZz039X8nhzo1yt0iE2e7U4pqf8yTu',
 'aZz039X8nhzo1yt0iE2e7U4pqf8yTu')
```

### Known Authorization URLs:

1. [Freesound](https://freesound.org/docs/api/authentication.html#oauth2-authentication):
   https://freesound.org/apiv2/oauth2/authorize/

## Integration with Provider API Scripts

Once everything is set up for an OAuth2 provider, the
[`OAuth2DelayedRequester`](../common/requester.py) can be used instead of the
`DelayedRequester` for the provider API script. No other changes are necessary!
