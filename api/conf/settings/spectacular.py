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
                Openverse provides free and open access to the Openverse API to
                anonymous and registered users. [Refer to the API documentation
                site for information on how to register](https://api.openverse.org/v1/#tag/auth).

                All Openverse API users are subject to rate limits and restrictions
                on how much of Openverse's dataset can be accessed through the API.
                [Individuals should contact Openverse to request expanded access to
                the API](https://github.com/WordPress/openverse#keep-in-touch).
                Requests are considered on a case-by-case basis and are subject to
                evaluation in light of [Openverse's Terms of Service](https://docs.openverse.org/terms_of_service.html).
                Escalated access may be revoked at any time.

                To authenticate yourself, you must sign up for an API key using
                the `register` endpoint and then get an access token using the
                `token` endpoint. Read on to know about these endpoints.

                In subsequent requests, include your access token as a bearer
                token in the `Authorization` header.

                ```
                Authorization: Bearer <access_token>
                ```

                ### Rate limits

                Openverse endpoints are rate limited. Anonymous requests should be
                sufficient for most users. Indeed, https://openverse.org itself
                operates using anonymous requests from the browser.

                Registered users are automatically granted slightly higher limits.
                Further increases to rate limits are available upon request (see above).

                Every Openverse API response that was subject to rate-limits includes
                headers outlining the permitted and available usage. Exceeding the limit
                will result in '429: Too Many Requests' responses.

                ### Pagination

                Openverse's dataset is valuable, and the
                [Terms of Service](https://docs.openverse.org/terms_of_service.html)
                disallow scraping under all circumstances. As such, pagination
                for anonymous users is limited, accommodating only the typical
                usage on https://openverse.org. Pagination is limited in terms
                of the size of individual pages and the total number of works
                visible for a query (pagination depth).

                Authenticated users are subject to the same limit of total works
                available for a query, but may request larger individual pages.

                Increases to pagination limits on page size and total depth are
                available upon request (see above).
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
