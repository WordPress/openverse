from django.db import models

from catalog.api.constants.media_types import MEDIA_TYPES
from catalog.api.models.base import OpenLedgerModel


class ContentProvider(models.Model):
    """
    A content provider instance can only be mapped to a single media type. For
    providers providing multiple media types, use different identifiers while
    keeping the same display name.

    For example,
    - Wikimedia for audio can have
        ``provider_identifier`` as  wikimedia_audio" and
        ``provider_name`` as "Wikimedia"
    - Wikimedia for images can have
        ``provider_identifier`` as "wikimedia_images" or "wikimedia" and
        ``provider_name`` as "Wikimedia"
    """
    provider_identifier = models.CharField(max_length=50, unique=True)
    provider_name = models.CharField(max_length=250)
    created_on = models.DateTimeField(auto_now=False)
    domain_name = models.CharField(max_length=500)
    filter_content = models.BooleanField(
        null=False,
        default=False,
        verbose_name='Hide content'
    )
    notes = models.TextField(null=True)
    media_type = models.CharField(
        max_length=80,
        choices=MEDIA_TYPES,
    )

    class Meta:
        db_table = 'content_provider'


class SourceLogo(models.Model):
    source = models.OneToOneField(ContentProvider, on_delete=models.CASCADE)
    image = models.ImageField()


class Tag(OpenLedgerModel):
    foreign_identifier = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=1000, blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, max_length=255)

    class Meta:
        db_table = 'tag'


class ShortenedLink(OpenLedgerModel):
    shortened_path = models.CharField(
        unique=True,
        max_length=10,
        help_text="The path to the shortened URL, e.g. tc3n834. The resulting "
                  "URL will be shares.cc/tc3n834.",
        db_index=True
    )
    full_url = models.URLField(unique=True, max_length=1000, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
