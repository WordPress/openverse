import mimetypes
from textwrap import dedent

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

import structlog
from elasticsearch import Elasticsearch, NotFoundError
from openverse_attribution.license import License

from api.constants.moderation import DecisionAction
from api.models.base import OpenLedgerModel
from api.models.mixins import ForeignIdentifierMixin, IdentifierMixin, MediaMixin


PENDING = "pending_review"
MATURE_FILTERED = "mature_filtered"
DEINDEXED = "deindexed"
NO_ACTION = "no_action"

MATURE = "mature"
DMCA = "dmca"
OTHER = "other"

logger = structlog.get_logger(__name__)


class AbstractMedia(
    IdentifierMixin, ForeignIdentifierMixin, MediaMixin, OpenLedgerModel
):
    """
    Generic model from which to inherit all media classes.

    This class stores information common to all media types indexed by Openverse.

    Properties
    ==========
    id: >-
        This is Django's automatic primary key, used for models that do not
        define one explicitly.
    """

    watermarked = models.BooleanField(
        blank=True,
        null=True,
        help_text="Whether the media contains a watermark. Not currently leveraged.",
    )

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
    last_synced_with_source = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        help_text="The date the media was last updated from the upstream source.",
    )
    removed_from_source = models.BooleanField(
        default=False,
        help_text="Whether the media has been removed from the upstream source.",
    )

    view_count = models.IntegerField(
        blank=True, null=True, default=0, help_text="Vestigial field, purpose unknown."
    )

    tags = models.JSONField(
        blank=True,
        null=True,
        help_text=dedent("""
        JSON array of objects containing tags for the media. Each tag object
        is expected to have:

        - `name`: The tag itself (e.g. "dog")
        - `provider`: The source of the tag
        - `accuracy`: If the tag was added using a machine-labeler, the confidence
        for that label expressed as a value between 0 and 1.

        Note that only `name` and `accuracy` are presently surfaced in API results.
        """),
    )

    category = models.CharField(
        max_length=80,
        blank=True,
        null=True,
        db_index=True,
        help_text="The top-level classification of this media file.",
    )

    meta_data = models.JSONField(
        blank=True,
        null=True,
        help_text=dedent("""
        JSON object containing extra data about the media item. No fields are expected,
        but if the `license_url` field is available, it will be used for determining
        the license URL for the media item. The `description` field, if available, is
        also indexed into Elasticsearch and as a search field on queries.
        """),
    )

    @property
    def license_url(self) -> str | None:
        """A direct link to the license deed or legal terms."""

        if self.meta_data and (url := self.meta_data.get("license_url")):
            return url

        logger.warning(
            "Media item missing `license_url` in `meta_data`",
            media_class=self.__class__.__name__,
            identifier=self.identifier,
        )
        try:
            return License(self.license.lower(), self.license_version).url
        except ValueError:
            return None

    @property
    def attribution(self) -> str | None:
        """Legally valid attribution for the media item in plain-text English."""

        try:
            return License(
                self.license.lower(),
                self.license_version,
            ).get_attribution_text(
                self.title,
                self.creator,
                self.license_url,
            )
        except ValueError:
            return None

    class Meta:
        """
        Meta class for all media types indexed by Openverse.

        All concrete media classes should inherit their Meta class from this.
        """

        ordering = ["-created_on"]
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["foreign_identifier", "provider"],
                name="unique_provider_%(class)s",  # populated by concrete model
            ),
        ]

    def __str__(self):
        """
        Return the string representation of the model, used in the Django admin site.

        :return: the string representation of the model
        """

        return f"{self.__class__.__name__}: {self.identifier}"


class AbstractMediaReport(models.Model):
    """
    Generic model from which to inherit all reported media classes.

    'Reported' here refers to content reports such as sensitive, copyright-violating or
    deleted content. Subclasses must populate the field ``media_class``.
    """

    media_class: type[models.Model] = None
    """the model class associated with this media type e.g. ``Image`` or ``Audio``"""

    REPORT_CHOICES = [(MATURE, MATURE), (DMCA, DMCA), (OTHER, OTHER)]

    STATUS_CHOICES = [
        (PENDING, PENDING),
        (MATURE_FILTERED, MATURE_FILTERED),
        (DEINDEXED, DEINDEXED),
        (NO_ACTION, NO_ACTION),
    ]

    created_at = models.DateTimeField(auto_now_add=True)

    media_obj = models.ForeignKey(
        to="AbstractMedia",
        to_field="identifier",
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        db_column="identifier",
        related_name="abstract_media_report",
        help_text="The reference to the media being reported.",
    )
    """
    There can be many reports associated with a single media item, hence foreign key.
    Sub-classes must override this field to point to a concrete sub-class of
    ``AbstractMedia``.
    """

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
    """
    All statuses except ``PENDING`` are deprecated. Instead refer to the
    property ``is_pending``.
    """

    decision = models.ForeignKey(
        to="AbstractMediaDecision",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="The moderation decision for this report.",
    )

    class Meta:
        abstract = True

    def clean(self):
        """Clean fields and raise errors that can be handled by Django Admin."""

        if not self.media_class.objects.filter(identifier=self.media_obj_id).exists():
            raise ValidationError(
                f"No '{self.media_class.__name__}' instance "
                f"with identifier '{self.media_obj_id}'."
            )

    def media_url(self, request=None) -> str:
        """
        Build the URL of the media item. This uses ``reverse`` and
        ``request.build_absolute_uri`` to build the URL without having to worry
        about canonical URL or trailing slashes.

        :param request: the current request object, to get absolute URLs
        :return: the URL of the media item
        """

        url = reverse(
            f"{self.media_class.__name__.lower()}-detail",
            args=[self.media_obj_id],
        )
        if request is not None:
            url = request.build_absolute_uri(url)
        return url

    def url(self, request=None) -> str:
        url = self.media_url(request)
        return format_html(f"<a href={url}>{url}</a>")

    @property
    def is_pending(self) -> bool:
        """
        Determine if the report has not been moderated and does not have an
        associated decision. Use the inverse of this function to determine
        if a report has been reviewed and moderated.

        :return: whether the report is in the "pending" state
        """

        return self.decision_id is None

    def save(self, *args, **kwargs):
        """Perform a clean, and then save changes to the DB."""

        self.clean()
        super().save(*args, **kwargs)


class AbstractMediaDecision(OpenLedgerModel):
    """Generic model from which to inherit all moderation decision classes."""

    media_class: type[models.Model] = None
    """the model class associated with this media type e.g. ``Image`` or ``Audio``"""

    moderator = models.ForeignKey(
        to="auth.User",
        on_delete=models.DO_NOTHING,
        help_text="The moderator who undertook this decision.",
    )
    """
    The ``User`` referenced by this field must be a part of the moderators'
    group.
    """

    media_objs = models.ManyToManyField(
        to="AbstractMedia",
        through="AbstractMediaDecisionThrough",
        help_text="The media items being moderated.",
    )
    """
    This is a many-to-many relation, using a bridge table, to enable bulk
    moderation which applies a single action to more than one media items.
    """

    notes = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="The moderator's explanation for the decision or additional notes.",
    )

    action = models.CharField(
        max_length=32,
        choices=DecisionAction.choices,
        help_text="Action taken by the moderator.",
    )

    class Meta:
        abstract = True


class AbstractMediaDecisionThrough(models.Model):
    """
    Generic model for the many-to-many reference table between media and decisions.

    This is made explicit (rather than using Django's default) so that the media can
    be referenced by `identifier` rather than an arbitrary `id`.
    """

    media_class: type[models.Model] = None
    """the model class associated with this media type e.g. ``Image`` or ``Audio``"""
    sensitive_media_class: type[models.Model] = None
    """the model class associated with this media type e.g. ``SensitiveImage`` or ``SensitiveAudio``"""
    deleted_media_class: type[models.Model] = None
    """the model class associated with this media type e.g. ``DeletedImage`` or ``DeletedAudio``"""

    media_obj = models.ForeignKey(
        AbstractMedia,
        to_field="identifier",
        on_delete=models.DO_NOTHING,
        db_column="identifier",
        db_constraint=False,
    )
    decision = models.ForeignKey(AbstractMediaDecision, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def perform_action(self):
        """Perform the action specified in the decision."""

        if self.decision.action in {
            DecisionAction.DEINDEXED_SENSITIVE,
            DecisionAction.DEINDEXED_COPYRIGHT,
        }:
            self.deleted_media_class.objects.create(media_obj=self.media_obj)

        if self.decision.action == DecisionAction.MARKED_SENSITIVE:
            self.sensitive_media_class.objects.create(media_obj=self.media_obj)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.perform_action()


class PerformIndexUpdateMixin:
    @property
    def indexes(self):
        return [self.es_index, f"{self.es_index}-filtered"]

    def _perform_index_update(self, method: str, raise_errors: bool, **es_method_args):
        """
        Call ``method`` on the Elasticsearch client.

        Automatically handles ``DoesNotExist`` warnings, forces a refresh,
        and calls the method for origin and filtered indexes.
        """
        es: Elasticsearch = settings.ES

        try:
            document_id = self.media_obj.id
        except self.media_class.DoesNotExist:
            if raise_errors:
                raise ValidationError(
                    f"No '{self.media_class.__name__}' instance "
                    f"with identifier {self.media_obj.identifier}."
                )

        for index in self.indexes:
            try:
                getattr(es, method)(
                    index=index,
                    id=document_id,
                    refresh=True,
                    **es_method_args,
                )
            except NotFoundError:
                # This is expected for the filtered index, but we should still
                # log, just in case.
                logger.warning(
                    f"Document with _id {document_id} not found "
                    f"in {index} index. No update performed."
                )
                continue


class AbstractDeletedMedia(PerformIndexUpdateMixin, OpenLedgerModel):
    """
    Generic model from which to inherit all deleted media classes.

    'Deleted' here refers to media which has been deleted at the source or intentionally
    de-indexed by us. Unlike sensitive reports, this action is irreversible. Subclasses
    must populate ``media_class`` and ``es_index`` fields.
    """

    media_class: type[models.Model] = None
    """the model class associated with this media type e.g. ``Image`` or ``Audio``"""
    es_index: str = None
    """the name of the ES index from ``settings.MEDIA_INDEX_MAPPING``"""

    media_obj = models.OneToOneField(
        to="AbstractMedia",
        to_field="identifier",
        on_delete=models.DO_NOTHING,
        primary_key=True,
        db_constraint=False,
        db_column="identifier",
        related_name="deleted_abstract_media",
        help_text="The reference to the deleted media.",
    )
    """
    Sub-classes must override this field to point to a concrete sub-class of
    ``AbstractMedia``.
    """

    class Meta:
        abstract = True

    def _update_es(self, raise_errors: bool) -> models.Model:
        self._perform_index_update(
            "delete",
            raise_errors,
        )

    def save(self, *args, **kwargs):
        self._update_es(True)
        super().save(*args, **kwargs)
        self.media_obj.delete()  # remove the actual model instance


class AbstractSensitiveMedia(PerformIndexUpdateMixin, models.Model):
    """
    Generic model from which to inherit all sensitive media classes.

    Subclasses must populate ``media_class`` and ``es_index`` fields.
    """

    media_class: type[models.Model] = None
    """the model class associated with this media type e.g. ``Image`` or ``Audio``"""
    es_index: str = None
    """the name of the ES index from ``settings.MEDIA_INDEX_MAPPING``"""

    created_on = models.DateTimeField(auto_now_add=True)

    media_obj = models.OneToOneField(
        to="AbstractMedia",
        to_field="identifier",
        on_delete=models.DO_NOTHING,
        primary_key=True,
        db_constraint=False,
        db_column="identifier",
        related_name="sensitive_abstract_media",
        help_text="The reference to the sensitive media.",
    )
    """
    Sub-classes must override this field to point to a concrete sub-class of
    ``AbstractMedia``.
    """

    class Meta:
        abstract = True

    def _update_es(self, is_mature: bool, raise_errors: bool):
        """
        Update the Elasticsearch document associated with the given model.

        :param is_mature: whether to mark the media item as mature
        :param raise_errors: whether to raise an error if the no media item is found
        """
        self._perform_index_update(
            "update",
            raise_errors,
            doc={"mature": is_mature},
        )

    def save(self, *args, **kwargs):
        self._update_es(True, True)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._update_es(False, False)
        super().delete(*args, **kwargs)


class AbstractMediaList(OpenLedgerModel):
    """
    Generic model from which to inherit media lists.

    Each subclass should define its own `ManyToManyField` to point to a subclass of
    `AbstractMedia`.
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
    :py:class:`api.models.mixins.FileMixin` class.
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
