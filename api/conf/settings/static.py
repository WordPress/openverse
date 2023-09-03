from decouple import config


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# Where to collect static files in production/development deployments
STATIC_ROOT = config("STATIC_ROOT", default="/static")

STATIC_URL = "static/"
