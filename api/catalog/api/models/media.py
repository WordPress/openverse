import mimetypes

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import format_html

from catalog.api.models.base import OpenLedgerModel
from catalog.api.models.mixins import (
    ForeignIdentifierMixin,
    IdentifierMixin,
    MediaMixin,
)
from catalog.api.utils.attribution import get_attribution_text
from catalog.api.utils.licenses import get_license_url


PENDING = "pending_review"
MATURE_FILTERED = "mature_filtered"
DEINDEXED = "deindexed"
NO_ACTION = "no_action"

MATURE = "mature"
DMCA = "dmca"
OTHER = "other"


class AbstractMedia(
    IdentifierMixin, ForeignIdentifierMixin, MediaMixin, OpenLedgerModel
):
    """
    Generic model from which to inherit all media classes. This class stores
    information common to all media types indexed by Openverse.
    """

    watermarked = models.BooleanField(blank=True, null=True)

    license = models.CharField(
        max_length=50,
        help_text="The name of license for the media.",
    )
    license_version = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        help_text="The version of the media license.",
    )

    source = models.CharField(
        max_length=80,
        blank=True,
        null=True,
        db_index=True,
        help_text="The source of the data, meaning a particular dataset. "
        "Source and provider can be different. Eg: the Google Open "
        "Images dataset is source=openimages, but provider=flickr.",
    )
    last_synced_with_source = models.DateTimeField(blank=True, null=True, db_index=True)
    removed_from_source = models.BooleanField(default=False)

    view_count = models.IntegerField(
        blank=True,
        null=True,
        default=0,
    )

    tags = models.JSONField(
        blank=True,
        null=True,
        help_text="Tags with detailed metadata, such as accuracy.",
    )
    tags_list = ArrayField(
        base_field=models.CharField(max_length=255),
        blank=True,
        null=True,
        help_text="List of tags names without detailed metadata.",
    )

    category = models.CharField(
        max_length=80,
        blank=True,
        null=True,
        db_index=True,
        help_text="The top-level classification of this media file.",
    )

    meta_data = models.JSONField(blank=True, null=True)

    @property
    def license_url(self) -> str:
        """A direct link to the license deed or legal terms."""

        if self.meta_data and (url := self.meta_data.get("license_url")):
            return url
        else:
            return get_license_url(self.license.lower(), self.license_version)

    @property
    def attribution(self) -> str:
        """
        The plain-text English attribution for a media item. Use this to credit creators
        for their work and fulfill legal attribution requirements.
        """

        return get_attribution_text(
            self.title,
            self.creator,
            self.license.lower(),
            self.license_version,
            self.license_url,
        )

    class Meta:
        """
        Meta class for all media types indexed by Openverse. All concrete media
        classes should inherit their Meta class from this.
        """

        ordering = ["-created_on"]
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["foreign_identifier", "provider"],
                name="unique_provider_%(class)s",  # populated by concrete model
            ),
        ]


class AbstractMediaReport(models.Model):
    """
    Generic model from which to inherit all reported media classes. 'Reported'
    here refers to content reports such as mature, copyright-violating or
    deleted content. Subclasses must populate ``media_class``, ``mature_class`` and
    ``deleted_class`` fields.
    """

    media_class: type[models.Model] = None
    """the model class associated with this media type e.g. ``Image`` or ``Audio``"""
    mature_class: type[models.Model] = None
    """the class storing mature media e.g. ``MatureImage`` or ``MatureAudio``"""
    deleted_class: type[models.Model] = None
    """the class storing deleted media e.g. ``DeletedImage`` or ``DeletedAudio``"""

    BASE_URL = settings.BASE_URL

    REPORT_CHOICES = [(MATURE, MATURE), (DMCA, DMCA), (OTHER, OTHER)]

    STATUS_CHOICES = [
        (PENDING, PENDING),
        (MATURE_FILTERED, MATURE_FILTERED),
        (DEINDEXED, DEINDEXED),
        (NO_ACTION, NO_ACTION),
    ]

    created_at = models.DateTimeField(auto_now_add=True)

    identifier = models.UUIDField(help_text="The ID for media to be reported.")
    reason = models.CharField(
        max_length=20,
        choices=REPORT_CHOICES,
        help_text="The reason to report media to Openverse.",
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="The explanation on why media is being reported.",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    class Meta:
        abstract = True

    def clean(self):
        """
        This function raises errors that can be handled by Django's admin interface.
        """

        if not self.media_class.objects.filter(identifier=self.identifier).exists():
            raise ValidationError(
                f"No '{self.media_class.__name__}' instance"
                f"with identifier {self.identifier}."
            )

    def url(self, media_type):
        url = f"{AbstractMediaReport.BASE_URL}v1/{media_type}/{self.identifier}"
        return format_html(f"<a href={url}>{url}</a>")

    def save(self, *args, **kwargs):
        """
        Extend the ``save()`` functionality with Elasticsearch integration to
        update records and refresh indices.

        Media marked as mature or deleted also leads to instantiation of their
        corresponding mature or deleted classes.
        """

        self.clean()

        if self.status == MATURE_FILTERED:
            # Create an instance of the mature class for this media. This will
            # automatically set the ``mature`` field in the ES document.
            self.mature_class.objects.create(identifier=self.identifier)
        elif self.status == DEINDEXED:
            # Create an instance of the deleted class for this media, so that we don't
            # reindex it later. This will automatically delete the ES document and the
            # DB instance.
            self.deleted_class.objects.create(identifier=self.identifier)

        same_reports = self.__class__.objects.filter(
            identifier=self.identifier,
            status=PENDING,
        )
        if self.status != DEINDEXED:
            same_reports = same_reports.filter(reason=self.reason)
        same_reports.update(status=self.status)

        super().save(*args, **kwargs)


class AbstractDeletedMedia(OpenLedgerModel):
    """
    Generic model from which to inherit all deleted media classes. 'Deleted'
    here refers to media which has been deleted at the source or intentionally
    de-indexed by us. Unlike mature reports, this action is irreversible. Subclasses
    must populate ``media_class`` and ``es_index`` fields.
    """

    media_class: type[models.Model] = None
    """the model class associated with this media type e.g. ``Image`` or ``Audio``"""
    es_index: str = None
    """the name of the ES index from ``settings.MEDIA_INDEX_MAPPING``"""

    identifier = models.UUIDField(
        unique=True, primary_key=True, help_text="The identifier of the deleted media."
    )

    class Meta:
        abstract = True

    def _update_es(self, raise_errors: bool) -> models.Model:
        es = settings.ES
        try:
            obj = self.media_class.objects.get(identifier=self.identifier)
            es.delete(index=self.es_index, id=obj.id)
            es.indices.refresh(index=self.es_index)
            return obj
        except self.media_class.DoesNotExist:
            if raise_errors:
                raise ValidationError(
                    f"No '{self.media_class.__name__}' instance"
                    f"with identifier {self.identifier}."
                )

    def save(self, *args, **kwargs):
        obj = self._update_es(True)
        obj.delete()  # remove the actual model instance
        super().save(*args, **kwargs)


class AbstractMatureMedia(models.Model):
    """
    Generic model from which to inherit all mature media classes. Subclasses must
    populate ``media_class`` and ``es_index`` fields.
    """

    media_class: type[models.Model] = None
    """the model class associated with this media type e.g. ``Image`` or ``Audio``"""
    es_index: str = None
    """the name of the ES index from ``settings.MEDIA_INDEX_MAPPING``"""

    created_on = models.DateTimeField(auto_now_add=True)
    identifier = models.UUIDField(unique=True, primary_key=True)

    class Meta:
        abstract = True

    def _update_es(self, is_mature: bool, raise_errors: bool):
        """
        Update the Elasticsearch document associated with the given model.

        :param is_mature: whether to mark the media item as mature
        :param raise_errors: whether to raise an error if the no media item is found
        """

        es = settings.ES
        try:
            obj = self.media_class.objects.get(identifier=self.identifier)
            es.update(
                index=self.es_index, id=obj.id, body={"doc": {"mature": is_mature}}
            )
            es.indices.refresh(index=self.es_index)
        except self.media_class.DoesNotExist:
            if raise_errors:
                raise ValidationError(
                    f"No '{self.media_class.__name__}' instance"
                    f"with identifier {self.identifier}."
                )

    def save(self, *args, **kwargs):
        self._update_es(True, True)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._update_es(False, False)
        super().delete(*args, **kwargs)


class AbstractMediaList(OpenLedgerModel):
    """
    Generic model from which to inherit media lists. Each subclass should define
    its own `ManyToManyField` to point to a subclass of `AbstractMedia`.
    """

    title = models.CharField(max_length=2000, help_text="Display name")
    slug = models.CharField(
        max_length=200,
        help_text="A unique identifier used to make a friendly URL for "
        "downstream API consumers.",
        unique=True,
        db_index=True,
    )
    auth = models.CharField(
        max_length=64,
        help_text="A randomly generated string assigned upon list creation. "
        "Used to authenticate updates and deletions.",
    )

    class Meta:
        abstract = True


class AbstractAltFile:
    """
    This is not a Django model.

    This Python class serves as the schema for an alternative file. An alt file
    provides alternative qualities, formats and resolutions that are available
    from the provider that are not canonical.

    The schema of the class must correspond to that of the
    :py:class:`catalog.api.models.mixins.FileMixin` class.
    """

    def __init__(self, attrs):
        self.url = attrs.get("url")
        self.filesize = attrs.get("filesize")
        self.filetype = attrs.get("filetype")

    @property
    def size_in_mib(self):  # ~ MiB or mibibytes
        return self.filesize / 2**20

    @property
    def size_in_mb(self):  # ~ MB or megabytes
        return self.filesize / 1e6

    @property
    def mime_type(self):
        """
        Get the MIME type of the file inferred from the extension of the file.
        :return: the inferred MIME type of the file
        """

        return mimetypes.types_map[f".{self.filetype}"]
