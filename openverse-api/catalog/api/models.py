from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
from django.utils.html import format_html
from oauth2_provider.models import AbstractApplication
from uuslug import uuslug

import catalog.api.controllers.search_controller as search_controller
from catalog.api.licenses import ATTRIBUTION, get_license_url


class OpenLedgerModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __iter__(self):
        for field_name in self._meta.get_fields():
            value = getattr(self, field_name, None)
            yield (field_name, value)

    class Meta:
        abstract = True


class AbstractMedia(OpenLedgerModel):
    """
    Abstract class to store information common across all media types indexed by
    Openverse. All concrete media classes should inherit from this class.
    """

    # ID
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

    # Media
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

    # Creator
    creator = models.CharField(max_length=2000, blank=True, null=True)
    creator_url = models.URLField(max_length=2000, blank=True, null=True)

    # Licensing
    license = models.CharField(max_length=50)
    license_version = models.CharField(max_length=25, blank=True, null=True)

    # Sync
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

    # Popularity
    view_count = models.IntegerField(default=0)

    # Tagging
    tags = JSONField(blank=True, null=True)
    tags_list = ArrayField(
        models.CharField(max_length=255), blank=True, null=True
    )

    # Miscellaneous
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


class Image(AbstractMedia):
    thumbnail = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="The thumbnail for the image, if any."
    )

    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)

    class Meta(AbstractMedia.Meta):
        db_table = 'image'


class AbstractDeletedMedia(OpenLedgerModel):
    identifier = models.UUIDField(
        unique=True,
        primary_key=True,
        help_text="The identifier of the deleted image."
    )

    class Meta:
        abstract = True


class DeletedImage(AbstractDeletedMedia):
    pass


class ContentProvider(models.Model):
    provider_identifier = models.CharField(max_length=50, unique=True)
    provider_name = models.CharField(max_length=250, unique=True)
    created_on = models.DateTimeField(auto_now=False)
    domain_name = models.CharField(max_length=500)
    filter_content = models.BooleanField(
        null=False, default=False, verbose_name='Hide content'
    )
    notes = models.TextField(null=True)

    class Meta:
        db_table = 'content_provider'


class SourceLogo(models.Model):
    source = models.OneToOneField(ContentProvider, on_delete=models.CASCADE)
    image = models.ImageField()


class ImageList(OpenLedgerModel):
    title = models.CharField(max_length=2000, help_text="Display name")
    images = models.ManyToManyField(
        Image,
        related_name="lists",
        help_text="A list of identifier keys corresponding to images."
    )
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
        db_table = 'imagelist'

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.title, instance=self)
        super(ImageList, self).save(*args, **kwargs)


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


class OAuth2Registration(models.Model):
    """
    Information about API key applicants.
    """
    name = models.CharField(
        max_length=150,
        unique=True,
        help_text="A unique human-readable name for your application or "
                  "project requiring access to the CC Catalog API."
    )
    description = models.CharField(
        max_length=10000,
        help_text="A description of what you are trying to achieve with your "
                  "project using the API. Please provide as much detail as "
                  "possible!"
    )
    email = models.EmailField(
        help_text="A valid email that we can reach you at if we have any "
                  "questions about your use case or data consumption."
    )


class ThrottledApplication(AbstractApplication):
    """
    An OAuth2 application with adjustable rate limits.
    """
    RATE_LIMIT_MODELS = [
        ('standard', 'standard'),  # Default rate limit for all API keys.
        ('enhanced', 'enhanced')   # Rate limits for "super" keys, granted on a
                                   # case-by-case basis.
    ]
    rate_limit_model = models.CharField(
        max_length=20,
        choices=RATE_LIMIT_MODELS,
        default='standard'
    )
    verified = models.BooleanField(default=False)


class OAuth2Verification(models.Model):
    """
    An email verification code sent by noreply-catalog. After verification
    occurs, the entry should be deleted.
    """
    associated_application = models.ForeignKey(
        ThrottledApplication,
        on_delete=models.CASCADE
    )
    email = models.EmailField()
    code = models.CharField(max_length=256, db_index=True)


class AbstractMatureMedia(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    identifier = models.UUIDField(
        unique=True,
        primary_key=True
    )

    class Meta:
        abstract = True


class MatureImage(AbstractMatureMedia):
    """ Stores all images that have been flagged as 'mature'. """

    def delete(self, *args, **kwargs):
        es = search_controller.es
        img = Image.objects.get(identifier=self.identifier)
        es_id = img.id
        es.update(
            index='image',
            id=es_id,
            body={'doc': {'mature': False}}
        )
        super(MatureImage, self).delete(*args, **kwargs)


PENDING = 'pending_review'
MATURE_FILTERED = 'mature_filtered'
DEINDEXED = 'deindexed'
NO_ACTION = 'no_action'

MATURE = 'mature'
DMCA = 'dmca'
OTHER = 'other'


class AbstractMediaReport(models.Model):
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


class ImageReport(AbstractMediaReport):
    class Meta:
        db_table = 'nsfw_reports'

    @property
    def image_url(self):
        url = f'https://search.creativecommons.org/photos/{self.identifier}'
        return format_html(f'<a href={url}>{url}</a>')

    def save(self, *args, **kwargs):
        update_required = {MATURE_FILTERED, DEINDEXED}
        if self.status in update_required:
            es = search_controller.es
            try:
                img = Image.objects.get(identifier=self.identifier)
            except Image.DoesNotExist:
                super(ImageReport, self).save(*args, **kwargs)
                return
            es_id = img.id
            if self.status == MATURE_FILTERED:
                MatureImage(identifier=self.identifier).save()
                es.update(
                    index='image',
                    id=es_id,
                    body={'doc': {'mature': True}}
                )
            elif self.status == DEINDEXED:
                # Delete from the API database (we'll still have a copy of the
                # metadata upstream in the catalog)
                img.delete()
                # Add to the deleted images table so we don't reindex it later
                DeletedImage(identifier=self.identifier).save()
                # Remove from search results
                es.delete(index='image', id=es_id)
            es.indices.refresh(index='image')
        # All other reports on the same image with the same reason need to be
        # given the same status. Deindexing an image results in all reports on
        # the image being marked 'deindexed' regardless of the reason.
        same_img_reports = ImageReport.objects.filter(
            identifier=self.identifier,
            status=PENDING
        )
        if self.status != DEINDEXED:
            same_img_reports = same_img_reports.filter(reason=self.reason)
        same_img_reports.update(status=self.status)
        super(ImageReport, self).save(*args, **kwargs)
