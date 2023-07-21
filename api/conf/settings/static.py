"""
Static files (CSS, JavaScript, Images)
https://docs.djangoproject.com/en/4.2/howto/static-files/
"""

from decouple import config


# Static files only served by Django in local environments
# In live environments, the files are served by Nginx, copied out of the Django image
STATIC_ROOT = config("STATIC_ROOT", default="/static")

STATIC_URL = "static/"
