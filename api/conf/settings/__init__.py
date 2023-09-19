"""
Django settings for the Openverse API.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

from decouple import config
from split_settings.tools import include


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parents[2]

# The order of the arguments matters here. Please note
# - any setting in a later file will override the same in an earlier file
# - `base.py` contains core settings and should always be first
# - `openverse.py` contains app-specific settings and should always be last
include(
    # core settings
    "base.py",
    "security.py",
    "auth.py",
    "logging.py",
    "i18n.py",
    "static.py",
    # services
    "databases.py",
    "elasticsearch.py",
    "email.py",
    "aws.py",
    # additional packages
    "oauth2.py",
    "rest_framework.py",
    "sentry.py",
    "spectacular.py",
    "thumbnails.py",
    # Openverse-specific settings
    "link_validation_cache.py",
    "misc.py",
    "openverse.py",
)
