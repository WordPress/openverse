from decouple import config

from conf.settings.base import INSTALLED_APPS


if "rest_framework" not in INSTALLED_APPS:
    INSTALLED_APPS.append("rest_framework")


THROTTLE_ANON_BURST = config("THROTTLE_ANON_BURST", default="5/hour")
THROTTLE_ANON_SUSTAINED = config("THROTTLE_ANON_SUSTAINED", default="100/day")
THROTTLE_ANON_THUMBS = config("THROTTLE_ANON_THUMBS", default="150/minute")
THROTTLE_OAUTH2_THUMBS = config("THROTTLE_OAUTH2_THUMBS", default="500/minute")
THROTTLE_ANON_HEALTHCHECK = config("THROTTLE_ANON_HEALTHCHECK", default="3/minute")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
    ),
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "api.utils.drf_renderer.BrowsableAPIRendererWithoutForms",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "api.utils.throttle.BurstRateThrottle",
        "api.utils.throttle.SustainedRateThrottle",
        "api.utils.throttle.AnonThumbnailRateThrottle",
        "api.utils.throttle.OAuth2IdThumbnailRateThrottle",
        "api.utils.throttle.OAuth2IdSustainedRateThrottle",
        "api.utils.throttle.OAuth2IdBurstRateThrottle",
        "api.utils.throttle.EnhancedOAuth2IdSustainedRateThrottle",
        "api.utils.throttle.EnhancedOAuth2IdBurstRateThrottle",
        "api.utils.throttle.ExemptOAuth2IdRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon_burst": THROTTLE_ANON_BURST,
        "anon_sustained": THROTTLE_ANON_SUSTAINED,
        "anon_healthcheck": THROTTLE_ANON_HEALTHCHECK,
        "anon_thumbnail": THROTTLE_ANON_THUMBS,
        "oauth2_client_credentials_thumbnail": THROTTLE_OAUTH2_THUMBS,
        "oauth2_client_credentials_sustained": "10000/day",
        "oauth2_client_credentials_burst": "100/min",
        "enhanced_oauth2_client_credentials_sustained": "20000/day",
        "enhanced_oauth2_client_credentials_burst": "200/min",
        # ``None`` completely by-passes the rate limiting
        "exempt_oauth2_client_credentials": None,
    },
    "EXCEPTION_HANDLER": "api.utils.exceptions.exception_handler",
    "DEFAULT_SCHEMA_CLASS": "api.docs.base_docs.MediaSchema",
    # https://www.django-rest-framework.org/api-guide/throttling/#how-clients-are-identified
    # Live environments should configure this to an appropriate number
    "NUM_PROXIES": config(
        "NUM_PROXIES", default=None, cast=lambda x: int(x) if x is not None else None
    ),
}

if config("DISABLE_GLOBAL_THROTTLING", default=True, cast=bool):
    # Set all to ``None`` rather than deleting so that explicitly configured
    # throttled views in tests still have the default rates to fall back onto
    REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].update(
        **{k: None for k, _ in REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].items()}
    )
    del REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"]
