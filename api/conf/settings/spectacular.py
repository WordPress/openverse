from textwrap import dedent

from conf.settings.base import INSTALLED_APPS
from conf.settings.misc import API_VERSION


if "drf_spectacular" not in INSTALLED_APPS:
    INSTALLED_APPS.append("drf_spectacular")

SPECTACULAR_SETTINGS = {
    "TITLE": "Openverse API",
    "DESCRIPTION": dedent(
        """
        Openverse is a search engine for openly-licensed media. The Openverse
        API is a system that allows programmatic access to public domain digital
        media. It is our ambition to index and catalog billions of
        openly-licensed works, including articles, songs, videos, photographs,
        paintings, and more.

        Using this API, developers will be able to access the digital commons in
        their own applications. You can see some examples of
        [apps built with Openverse](https://docs.openverse.org/api/reference/made_with_ov.html)
        in our docs.
        """
    ),
    "TOS": "https://docs.openverse.org/terms_of_service.html",
    "CONTACT": {
        "name": "Openverse",
        "email": "openverse@wordpress.org",
    },
    "LICENSE": {
        "name": "MIT License",
        "url": "https://github.com/WordPress/openverse/blob/main/LICENSE",
    },
    "VERSION": API_VERSION,
    "EXTERNAL_DOCS": {
        "description": "Openverse documentation",
        "url": "http://docs.openverse.org/api/user/index.html",
    },
    "SERVE_INCLUDE_SCHEMA": False,
    "SORT_OPERATION_PARAMETERS": False,
    "EXTENSIONS_INFO": {
        "x-logo": {
            "url": "https://raw.githubusercontent.com/WordPress/openverse/HEAD/documentation/meta/brand/logo.svg",
            "backgroundColor": "#fafafa",
        }
    },
    "TAGS": [
        {
            "name": "auth",
            "description": dedent(
                """
                The API has rate-limiting and throttling in place to prevent
                abuse. In the response for each request that is subject to
                rate-limits, you can see the `X-RateLimit-` headers for info
                about your permitted and available usage. Exceeding the limit
                will result in '429: Too Many Requests' responses.

                - Anonymous clients are limited to make 5 req/hour and
                  100 req/day. Therefore we recommend registering for
                  authenticated usage.

                - Authenticated clients can make 100 req/minute and 10,000
                  req/day. Additionally, you can request a higher limit to fit
                  your application's needs.

                To authenticate yourself, you must sign up for an API key using
                the `register` endpoint and then get an access token using the
                `token` endpoint. Read on to know about these endpoints.

                In subsequent requests, include your access token as a bearer
                token in the `Authorization` header.

                ```
                Authorization: Bearer <access_token>
                ```
                """
            ),
        },
        {
            "name": "audio",
            "description": "These are endpoints pertaining to audio files.",
        },
        {
            "name": "images",
            "description": "These are endpoints pertaining to images.",
        },
    ],
    "REDOC_UI_SETTINGS": {
        "theme": {
            "logo": {"gutter": "20px"},
            "typography": {"headings": {"fontFamily": "inherit", "fontWeight": 700}},
        }
    },
}
