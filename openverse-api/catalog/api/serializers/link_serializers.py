import redlock
import os
import logging as log
from rest_framework.serializers import ModelSerializer, Serializer, URLField, \
    ValidationError
from catalog.api.controllers.link_controller import get_next_shortened_path
from catalog.api.models import ShortenedLink
from catalog import settings
from urllib.parse import urlparse
from rest_framework import serializers

# Create a lock inside of Redis to ensure that multiple server workers don't
# try to create the same shortened URL.
__parsed_redis_url = urlparse(settings.CACHES['locks']['LOCATION'])
__host, __port = __parsed_redis_url.netloc.split(':')
__db_num = __parsed_redis_url.path[1] if __parsed_redis_url.path else None
__password = os.environ.get("REDIS_PASSWORD")
# Clients will attempt to acquire the lock infinitely with a 1 second delay.
url_lock = redlock.Redlock(
    [{"host": __host, "port": __port, "db": __db_num, "password": __password}],
    retry_count=1, retry_delay=1000
)


class ShortenedLinkResponseSerializer(Serializer):
    shortened_url = URLField(
        help_text="A shortened link on the `shares.cc` domain."
    )


class ShortenedLinkSerializer(ModelSerializer):
    """
    A single shortened URL, mapping a shortened path at shares.cc to a full
    URL elsewhere on the CC Catalog platform.
    """
    full_url = serializers.URLField(
        max_length=1000,
        help_text="The URL to shorten. Only URLs on the Openverse domain will "
                  "be accepted. "
                  f"Valid domains: `{settings.SHORT_URL_WHITELIST}`. "
                  f"Valid paths: `{settings.SHORT_URL_PATH_WHITELIST}`."
    )

    class Meta:
        model = ShortenedLink
        fields = ('full_url',)

    def validate_full_url(self, value):
        parsed_url = urlparse(value)
        url = '{url.netloc}'.format(url=parsed_url)
        path = '{url.path}'.format(url=parsed_url)
        if url not in settings.SHORT_URL_WHITELIST:
            raise ValidationError(
                "You can only create a short URL to items inside of the CC "
                "Catalog. Pointing to other domains is not allowed."
            )

        found_allowed_path = False
        for allowed_path in settings.SHORT_URL_PATH_WHITELIST:
            if path.startswith(allowed_path):
                found_allowed_path = True

        if not found_allowed_path:
            raise ValidationError(
                "Illegal path. Valid paths must start with"
                f" {settings.SHORT_URL_PATH_WHITELIST}"
            )

        return value

    def save(self):
        two_seconds_ms = 1000 * 2
        lock = url_lock.lock('unique_url_lock', ttl=two_seconds_ms)
        shortened_path = None
        if lock:
            try:
                last_url = str(
                    ShortenedLink
                    .objects
                    .latest(field_name='created_on')
                    .shortened_path
                )
            except ShortenedLink.DoesNotExist:
                # No URLs exist. Create the first one.
                last_url = None

            shortened_path = get_next_shortened_path(last_url)
            full_url = self.validated_data['full_url']
            shortened_link_instance = ShortenedLink(
                shortened_path=shortened_path,
                full_url=full_url
            )
            shortened_link_instance.save()
            url_lock.unlock(lock)
            return shortened_path
        else:
            log.error('Failed to acquire URL lock.')
        return shortened_path
