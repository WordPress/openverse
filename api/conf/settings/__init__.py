"""
Django settings for the Openverse API.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from socket import gethostbyname, gethostname

from decouple import config

from conf.settings.aws import *
from conf.settings.elasticsearch import *
from conf.settings.email import *
from conf.settings.link_validation_cache import *
from conf.settings.logging import *
from conf.settings.misc import *
from conf.settings.oauth2 import *
from conf.settings.rest_framework import *
from conf.settings.sentry import *
from conf.settings.spectacular import *
from conf.settings.thumbnails import *


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("DJANGO_SECRET_KEY")  # required

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DJANGO_DEBUG_ENABLED", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(",") + [
    gethostname(),
    gethostbyname(gethostname()),
]

if lb_url := config("LOAD_BALANCER_URL", default=""):
    ALLOWED_HOSTS.append(lb_url)

if DEBUG:
    ALLOWED_HOSTS += [
        "dev.openverse.test",  # used in local development
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
    ]

BASE_URL = config("BASE_URL", default="https://openverse.org/")

# Trusted origins for CSRF
# https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = ["https://*.openverse.engineering"]

# Allow anybody to access the API from any domain
CORS_ORIGIN_ALLOW_ALL = True

# Proxy handling, for production
if config("IS_PROXIED", default=True, cast=bool):
    # https://docs.djangoproject.com/en/4.0/ref/settings/#use-x-forwarded-host
    USE_X_FORWARDED_HOST = True
    # https://docs.djangoproject.com/en/4.0/ref/settings/#secure-proxy-ssl-header
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# S3 storage
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings

USE_S3 = config("USE_S3", default=False, cast=bool)

if USE_S3:
    AWS_STORAGE_BUCKET_NAME = config("LOGOS_BUCKET", default="openverse_api-logos-prod")
    AWS_S3_SIGNATURE_VERSION = "s3v4"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party installed apps
    "oauth2_provider",
    "rest_framework",
    "corsheaders",
    "sslserver",
    "drf_spectacular",
]

if USE_S3:
    INSTALLED_APPS.append("storages")

# Keep first-party apps last
INSTALLED_APPS.append("api")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Third-party middleware
    "oauth2_provider.middleware.OAuth2TokenMiddleware",
]

DJANGO_DB_LOGGING = config("DJANGO_DB_LOGGING", cast=bool, default=False)
if not DEBUG and DJANGO_DB_LOGGING:
    # WARNING: Do not run in production long-term as it can impact performance.
    MIDDLEWARE.append(
        "api.middleware.force_debug_cursor_middleware.force_debug_cursor_middleware"  # noqa: E501
    )

ROOT_URLCONF = "conf.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "conf.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": config("DJANGO_DATABASE_HOST", default="localhost"),
        "PORT": config("DJANGO_DATABASE_PORT", default=5432, cast=int),
        "USER": config("DJANGO_DATABASE_USER", default="deploy"),
        "PASSWORD": config("DJANGO_DATABASE_PASSWORD", default="deploy"),
        "NAME": config("DJANGO_DATABASE_NAME", default="openledger"),
        "OPTIONS": {
            "application_name": config(
                "DJANGO_DATABASE_APPLICATION_NAME", default="openverse-api"
            ),
        },
    }
}

# Caches

REDIS_HOST = config("REDIS_HOST", default="localhost")
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
REDIS_PASSWORD = config("REDIS_PASSWORD", default="")


def _make_cache_config(dbnum: int, **overrides) -> dict:
    return {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{dbnum}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
        | overrides.pop("OPTIONS", {}),
    } | overrides


CACHES = {
    # Site cache writes to 'default'
    "default": _make_cache_config(0),
    # For rapidly changing stats that we don't want to hammer the database with
    "traffic_stats": _make_cache_config(1),
    # For ensuring consistency among multiple Django workers and servers.
    # Used by Redlock.
    "locks": _make_cache_config(2),
    # Used for tracking tallied figures that shouldn't expire and are indexed
    # with a timestamp range (for example, the key could a timestamp valid
    # for a given week), allowing historical data analysis.
    "tallies": _make_cache_config(3, TIMEOUT=None),
}

# Authentication backends
# https://docs.djangoproject.com/en/4.2/ref/settings/#authentication-backends

AUTHENTICATION_BACKENDS = (
    "oauth2_provider.backends.OAuth2Backend",
    "django.contrib.auth.backends.ModelBackend",
)

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Storage
# https://docs.djangoproject.com/en/4.2/ref/settings/#storages

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

if USE_S3:
    STORAGES["default"]["BACKEND"] = "storages.backends.s3boto3.S3Boto3Storage"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# Where to collect static files in production/development deployments
STATIC_ROOT = config("STATIC_ROOT", default="/var/api_static_content/static")

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
