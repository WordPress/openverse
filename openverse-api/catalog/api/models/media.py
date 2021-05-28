from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models

from catalog.api.licenses import ATTRIBUTION, get_license_url
from catalog.api.models.base import OpenLedgerModel

PENDING = 'pending_review'
MATURE_FILTERED = 'mature_filtered'
DEINDEXED = 'deindexed'
NO_ACTION = 'no_action'

MATURE = 'mature'
DMCA = 'dmca'
OTHER = 'other'


class AbstractMedia(OpenLedgerModel):
    """
    Generic model from which to inherit all media classes. This class stores
    information common to all media types indexed by Openverse.
    """

    identifier = models.UUIDField(
        unique=True,
        db_index=True,
        help_text="Our unique identifier for a CC work."
    )
    foreign_identifier = models.CharField(
        unique=True,
        max_length=1000,
        blank=True,
        null=True,
        db_index=True,
        help_text="The identifier provided by the upstream source."
    )

    title = models.CharField(max_length=2000, blank=True, null=True)
    foreign_landing_url = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="The landing page of the work."
    )
    url = models.URLField(
        unique=True,
        max_length=1000,
        help_text="The actual URL to the image."
    )
    filesize = models.IntegerField(blank=True, null=True)
    watermarked = models.NullBooleanField(blank=True, null=True)

    creator = models.CharField(max_length=2000, blank=True, null=True)
    creator_url = models.URLField(max_length=2000, blank=True, null=True)

    license = models.CharField(max_length=50)
    license_version = models.CharField(max_length=25, blank=True, null=True)

    provider = models.CharField(
        max_length=80,
        blank=True,
        null=True,
        db_index=True,
        help_text="The content provider, e.g. Flickr, 500px...")
    source = models.CharField(
        max_length=80,
        blank=True,
        null=True,
        db_index=True,
        help_text="The source of the data, meaning a particular dataset. Source"
                  " and provider can be different: the Google Open Images "
                  "dataset is source=openimages., but provider=Flickr."
    )
    last_synced_with_source = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True
    )
    removed_from_source = models.BooleanField(default=False)

    view_count = models.IntegerField(default=0)

    tags = JSONField(blank=True, null=True)
    tags_list = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        null=True
    )

    meta_data = JSONField(blank=True, null=True)

    @property
    def license_url(self):
        _license = str(self.license)
        license_version = str(self.license_version)
        return get_license_url(_license, license_version)

    @property
    def attribution(self):
        _license = str(self.license)
        license_version = str(self.license_version)
        if self.title:
            title = '"' + str(self.title) + '"'
        else:
            title = 'This work'
        if self.creator:
            creator = 'by ' + str(self.creator) + ' '
        else:
            creator = ''
        attribution = ATTRIBUTION.format(
            title=title,
            creator=creator,
            _license=_license.upper(),
            version=license_version,
            license_url=str(self.license_url)
        )
        return attribution

    class Meta:
        """
        Meta class for all media types indexed by Openverse. All concrete media
        classes should inherit their Meta class from this.
        """
        ordering = ['-created_on']
        abstract = True


class AbstractMediaReport(models.Model):
    """
    Generic model from which to inherit all reported media classes. 'Reported'
    here refers to content reports such as mature, copyright-violating or
    deleted content.
    """

    REPORT_CHOICES = [
        (MATURE, MATURE),
        (DMCA, DMCA),
        (OTHER, OTHER)
    ]

    STATUS_CHOICES = [
        (PENDING, PENDING),
        (MATURE_FILTERED, MATURE_FILTERED),
        (DEINDEXED, DEINDEXED),
        (NO_ACTION, NO_ACTION)
    ]

    created_at = models.DateTimeField(auto_now_add=True)

    identifier = models.UUIDField(
        help_text="The ID for image to be reported."
    )
    reason = models.CharField(
        max_length=20,
        choices=REPORT_CHOICES,
        help_text="The reason to report image to Creative Commons."
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="The explanation on why image is being reported."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    class Meta:
        abstract = True


class AbstractDeletedMedia(OpenLedgerModel):
    """
    Generic model from which to inherit all deleted media classes. 'Deleted'
    here refers to media which has been deleted at the source.
    """

    identifier = models.UUIDField(
        unique=True,
        primary_key=True,
        help_text="The identifier of the deleted image."
    )

    class Meta:
        abstract = True


class AbstractMatureMedia(models.Model):
    """
    Generic model from which to inherit all mature media classes.
    """

    created_on = models.DateTimeField(auto_now_add=True)
    identifier = models.UUIDField(
        unique=True,
        primary_key=True
    )

    class Meta:
        abstract = True


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
        db_index=True
    )
    auth = models.CharField(
        max_length=64,
        help_text="A randomly generated string assigned upon list creation. "
                  "Used to authenticate updates and deletions."
    )

    class Meta:
        abstract = True
