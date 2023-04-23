from textwrap import dedent

from decouple import config


SPECTACULAR_SETTINGS = {
    "TITLE": "Openverse API",
    "DESCRIPTION": dedent(
        """
        Openverse is a search engine for openly-licensed media. The Openverse
        API is a system that allows programmatic access to public domain digital
        media. It is our ambition to index and catalog billions of
        openly-licensed works, including articles, songs, videos, photographs,
        paintings, and more. Using this API, developers will be able to access
        the digital commons in their own applications.
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
    "VERSION": config("SEMANTIC_VERSION", default="Version not specified"),
    "EXTERNAL_DOCS": {
        "description": "Openverse documentation",
        "url": "https://docs.openverse.org",
    },
    "SERVE_INCLUDE_SCHEMA": False,
    "SORT_OPERATION_PARAMETERS": False,
    "EXTENSIONS_INFO": {
        "x-logo": {
            "url": "https://raw.githubusercontent.com/WordPress/openverse/HEAD/brand/logo.svg",
            "backgroundColor": "#fafafa",
        }
    },
    "TAGS": [
        {
            "name": "auth",
            "externalDocs": {
                "description": "Authentication documentation",
                "url": "https://docs.openverse.org/authentication.html",
            },
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
