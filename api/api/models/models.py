from django.db import models

from api.constants.media_types import MEDIA_TYPE_CHOICES
from api.models.base import OpenLedgerModel


class ContentSource(models.Model):
    """
    A content source instance can only be mapped to a single media type.

    For sources with multiple media types, use different identifiers while
    keeping the same display name.

    For example,
    - Wikimedia for audio can have
        ``source_identifier`` as  "wikimedia_audio" and
        ``source_name`` as "Wikimedia"
    - Wikimedia for images can have
        ``source_identifier`` as "wikimedia_images" or "wikimedia" and
        ``source_name`` as "Wikimedia"
    """

    source_identifier = models.CharField(
        max_length=50, unique=True, db_column="provider_identifier"
    )
    source_name = models.CharField(max_length=250, db_column="provider_name")
    created_on = models.DateTimeField(auto_now=False)
    domain_name = models.CharField(max_length=500)
    filter_content = models.BooleanField(
        null=False, default=False, verbose_name="Hide content"
    )
    notes = models.TextField(null=True)
    media_type = models.CharField(
        max_length=80,
        choices=MEDIA_TYPE_CHOICES,
    )

    class Meta:
        db_table = "content_provider"


class Tag(OpenLedgerModel):
    foreign_identifier = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=1000, blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, max_length=255)

    class Meta:
        db_table = "tag"
