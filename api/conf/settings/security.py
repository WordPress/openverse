from socket import gethostbyname, gethostname, gaierror

from decouple import config

from conf.settings.base import INSTALLED_APPS, MIDDLEWARE


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("DJANGO_SECRET_KEY")  # required

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DJANGO_DEBUG_ENABLED", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(",")
try:
    hostname = gethostname()
    ALLOWED_HOSTS.append(hostname)
    ALLOWED_HOSTS.append(gethostbyname(hostname))
except gaierror:
    # Unable to get hostname and/or host by that hostname.
    pass

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
if "corsheaders" not in INSTALLED_APPS:
    INSTALLED_APPS.append("corsheaders")

middleware = "corsheaders.middleware.CorsMiddleware"
if middleware not in MIDDLEWARE:
    MIDDLEWARE.insert(0, middleware)

CORS_ORIGIN_ALLOW_ALL = True

# Proxy handling, for production
if config("IS_PROXIED", default=True, cast=bool):
    # https://docs.djangoproject.com/en/4.0/ref/settings/#use-x-forwarded-host
    USE_X_FORWARDED_HOST = True
    # https://docs.djangoproject.com/en/4.0/ref/settings/#secure-proxy-ssl-header
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
