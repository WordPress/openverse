# Authentication

Authenticated users enjoy a higher rate limit by default, and if their
application needs it, can request for even higher limits. We highly recommend
signing up for a API key for any use case except casually trying out the API.

The Openverse API uses OAuth2 for the authentication flow.

## Registration

**Endpoint:**
<a href="../../api_docs/#tag/auth/operation/register"><code class="literal">/v1/auth_tokens/register/</code></a>
(includes request and response samples)

To register, send a `POST` request to the registration endpoint. If valid, you
should receive a JSON response with the fields `client_id` and `client_secret`.

```{caution}
Please ensure to save the `client_id` and `client_secret` securely because they
cannot be retrieved later.
```

You will receive an email with a verification link inside. Click on the link to
verify your ownership of the provided email address. Until you email address is
verified, the application will be same rate limits as an anonymous user.

## Authentication

**Endpoint:** `/v1/auth_tokens/token/`

In order to use the Openverse API endpoints, you need to include an access token
in the header. You can receive an access token by providing your client
credentials in a `POST` request to the aforementioned endpoint.

```console
$ curl \
  -X POST \
  -d "client_id=<client_id>&client_secret=<client_secret>&grant_type=client_credentials" \
  "https://api.openverse.engineering/v1/auth_tokens/token/"
```

```{caution}
This endpoint only accepts data as `application/x-www-form-urlencoded`.
Requests with JSON data are not accepted.
```

If valid, you should receive a JSON response with the fields `access_token`,
`scope`, `expires_in` and `token_type`.

```json
{
  "access_token": "DLBYIcfnKfolaXKcmMC8RIDCavc2hW",
  "scope": "read write groups",
  "expires_in": 36000,
  "token_type": "Bearer"
}
```

Once the access token expires, repeat this step to obtain a new one.

## Authenticated usage

Include the access token in the
['Authorization' header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization)
as a bearer token to use your key in your future API requests.

```
Authorization: Bearer <access_token>
```

You should keep an eye on your usage. Refer to the
[`key-info` operation](./rate_limits.md#key-info) for more information.
