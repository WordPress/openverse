This documentation is focused towards consumers who are using the Openverse API.
To contribute to the development of the Openverse API, please refer to the
[Openverse developer documentation](https://docs.openverse.org/).

# Introduction

The Openverse API is a system that allows programmatic access to public domain
digital media. It is our ambition to index and catalog billions of
openly-licensed works, including articles, songs, videos, photographs,
paintings, and more. Using this API, developers will be able to access the
digital commons in their own applications.

# Rate limits

Please note that the API has imposed rate limits to prevent abuse. In the
response for each request that is subject to rate-limits, you can see the
`X-RateLimit-` headers for information about your permitted and available usage.
Exceeding the limit will result in '429: Too Many Requests' responses.

## Anonymous usage

Anonymous usage is subject to a rate limit of 100 requests per day and,
simultaneously, 5 requests per hour. This is fine for introducing yourself to
the API, but we strongly recommend that you obtain an API key as soon as
possible.

## Authenticated usage

Authorized clients have a higher rate limit of 10000 requests per day and 100
requests per minute. Additionally, Openverse can give your key an even higher
limit that fits your application's needs. See the
[Register and Authenticate section](#section/Register-and-Authenticate) for
instructions on obtaining an API key.

# Register and Authenticate

## Register for a key

Before using the Openverse API, you need to register access via OAuth2. This can
be done using the `/v1/auth_tokens/register/` endpoint.

Example on how to register for a key:

```bash
$ curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"name": "My amazing project", "description": "To access Openverse API", "email": "user@example.com"}' \
  "https://api.openverse.engineering/v1/auth_tokens/register/"
```

If your request is successful, you will get a `client_id` and `client_secret`.
Save these keys securely because you will not be able to see them again.

Example of successful request:

```json
{
  "client_secret": "YhVjvIBc7TuRJSvO2wIi344ez5SEreXLksV7GjalLiKDpxfbiM8qfUb5sNvcwFOhBUVzGNdzmmHvfyt6yU3aGrN6TAbMW8EOkRMOwhyXkN1iDetmzMMcxLVELf00BR2e",
  "client_id": "pm8GMaIXIhkjQ4iDfXLOvVUUcIKGYRnMlZYApbda",
  "name": "My amazing project"
}
```

## Authenticate

In order to use the Openverse API endpoints, you need to include access token in
the header. This can be done by exchanging your client credentials for a token
using the `/v1/auth_tokens/token/` endpoint.

Example on how to authenticate using OAuth2:

```bash
$ curl \
  -X POST \
  -d "client_id=pm8GMaIXIhkjQ4iDfXLOvVUUcIKGYRnMlZYApbda&client_secret=YhVjvIBc7TuRJSvO2wIi344ez5SEreXLksV7GjalLiKDpxfbiM8qfUb5sNvcwFOhBUVzGNdzmmHvfyt6yU3aGrN6TAbMW8EOkRMOwhyXkN1iDetmzMMcxLVELf00BR2e&grant_type=client_credentials" \
  "https://api.openverse.engineering/v1/auth_tokens/token/"
```

If your request is successful, you will get an access token.

Example of successful request:

```json
{
  "access_token": "DLBYIcfnKfolaXKcmMC8RIDCavc2hW",
  "scope": "read write groups",
  "expires_in": 36000,
  "token_type": "Bearer"
}
```

Check your email for a verification link. After you have followed the link, your
API key will be activated.

## Using Access Token

Include the `access_token` in the authorization header to use your key in your
future API requests.

Example on how to make an authenticated request:

```bash
$ curl \
  -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" \
  "https://api.openverse.engineering/v1/images?q=test"
```

> **NOTE:** Your token will be throttled like an anonymous user until the email
> address has been verified.

# Glossary

| Term              | Definition                                                                                                                                                                                    |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| API               | an abbreviation for Application Programming Interface                                                                                                                                         |
| OAuth2            | an authorization framework that enables a third party application to get access to an HTTP service                                                                                            |
| access token      | a private string that authorizes an application to make API requests                                                                                                                          |
| client ID         | a publicly exposed string used by Openverse API to identify the application                                                                                                                   |
| client secret     | a private string that authenticates the identity of the application to the Openverse API                                                                                                      |
| CC                | an abbreviation for Creative Commons                                                                                                                                                          |
| copyright         | a type of intellectual property that gives the owner an exclusive right to reproduce, publish, sell or distribute content                                                                     |
| mature content    | any content that requires the audience to be 18 and older                                                                                                                                     |
| sensitive content | any content that depicts graphic violence, adult content, and hostility or malice against others based on their race, religion, disability, sexual orientation, ethnicity and national origin |

# Contribute

We love pull requests! If you’re interested in
[contributing on Github](https://github.com/WordPress/openverse-api/blob/main/CONTRIBUTING.md),
here’s a todo list to get started.

- Read up about [Django REST Framework](https://www.django-rest-framework.org/),
  which is the framework used to build Openverse API
- Read up about [drf-yasg](https://drf-yasg.readthedocs.io/en/stable/), which is
  a tool used to generate real Swagger/OpenAPI 2.0 specifications
- Read up about Documentation Guidelines, which provides guidelines on how to
  contribute to documentation, documentation styles and cheat sheet for drf-yasg
- Run the server locally by following this
  [link](https://github.com/wordpress/openverse-api#running-the-server-locally)
- Update documentation or codebase
- Make sure the updates passed the automated tests in this
  [file](https://github.com/WordPress/openverse-api/blob/master/.github/workflows/integration-tests.yml)
- Commit and push
- Create pull request
