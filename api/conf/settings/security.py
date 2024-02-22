from socket import gethostbyname, gethostname

from django.core.exceptions import ImproperlyConfigured

from decouple import config

from conf.settings.base import ENVIRONMENT, INSTALLED_APPS, MIDDLEWARE


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("DJANGO_SECRET_KEY")  # required

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DJANGO_DEBUG_ENABLED", default=False, cast=bool)

# The domain we treat as "canonical" for this API instance, e.g., `api.` subdomain for production
CANONICAL_DOMAIN: str = config("CANONICAL_DOMAIN")  # required

_proto = "http" if "localhost" in CANONICAL_DOMAIN else "https"
CANONICAL_ORIGIN: str = f"{_proto}://{CANONICAL_DOMAIN}"

# Additional domains we serve for this API instance, e.g., `api-production.` subdomain for production
ADDITIONAL_DOMAINS: list[str] = config(
    "ADDITIONAL_DOMAINS", default="", cast=lambda x: x.split(",")
)

ALL_DOMAINS = [CANONICAL_DOMAIN] + ADDITIONAL_DOMAINS

ALLOWED_HOSTS = ALL_DOMAINS + [
    gethostname(),
    gethostbyname(gethostname()),
]

if DEBUG:
    ALLOWED_HOSTS += [
        "dev.openverse.test",  # used in local development
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
    ]

# Trusted origins for CSRF
# https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = [f"{_proto}://{domain}" for domain in ALL_DOMAINS]

# Allow anybody to access the API from any domain
if "corsheaders" not in INSTALLED_APPS:
    INSTALLED_APPS.append("corsheaders")

middleware = "corsheaders.middleware.CorsMiddleware"
if middleware not in MIDDLEWARE:
    MIDDLEWARE.insert(0, middleware)

CORS_ALLOW_ALL_ORIGINS = True
# https://github.com/adamchainz/django-cors-headers?tab=readme-ov-file#cors_expose_headers-sequencestr
# These headers are required for search response time analytics
CORS_EXPOSE_HEADERS = [
    "cf-cache-status",
    "cf-ray",
    "date",
]

# Proxy handling, for production
if config("IS_PROXIED", default=True, cast=bool):
    # https://docs.djangoproject.com/en/4.0/ref/settings/#secure-proxy-ssl-header
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Adding DJANGO_SECRET_KEY check
if SECRET_KEY == "example_key" and ENVIRONMENT != "local":
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY must not be 'example_key' in non-local environments."
    )
