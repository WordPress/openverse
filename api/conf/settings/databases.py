from decouple import config


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": config("DJANGO_DATABASE_HOST", default="localhost"),
        "PORT": config("DJANGO_DATABASE_PORT", default=50254, cast=int),
        "USER": config("DJANGO_DATABASE_USER", default="deploy"),
        "PASSWORD": config("DJANGO_DATABASE_PASSWORD", default="deploy"),
        "NAME": config("DJANGO_DATABASE_NAME", default="openledger"),
        # Default of 30 matches RDS documentation's advised max DNS caching time
        # https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html#CHAP_BestPractices.DiskPerformance
        "CONN_MAX_AGE": config("DJANGO_CONN_MAX_AGE", default=30),
        "CONN_HEALTH_CHECKS": config(
            "DJANGO_CONN_HEALTH_CHECKS", default=True, cast=bool
        ),
        "OPTIONS": {
            "application_name": config(
                "DJANGO_DATABASE_APPLICATION_NAME", default="openverse-api"
            ),
        },
    }
}
