from decouple import config

from conf.settings.base import INSTALLED_APPS, STORAGES


# S3 storage
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings

USE_S3 = config("USE_S3", default=False, cast=bool)


if USE_S3:
    if "storages" not in INSTALLED_APPS:
        INSTALLED_APPS.append("storages")

    STORAGES["default"]["BACKEND"] = "storages.backends.s3boto3.S3Boto3Storage"

    AWS_STORAGE_BUCKET_NAME = config("LOGOS_BUCKET", default="openverse_api-logos-prod")
    AWS_S3_SIGNATURE_VERSION = "s3v4"
