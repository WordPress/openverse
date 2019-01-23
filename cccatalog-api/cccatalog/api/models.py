from uuslug import slugify, uuslug
from django.db import models
from django.conf import settings
from django.utils.safestring import mark_safe
from django.contrib.postgres.fields import JSONField, ArrayField


class OpenLedgerModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __iter__(self):
        for field_name in self._meta.get_fields():
            try:
                value = getattr(self, field_name, None)
                yield (field_name, value)
            except:
                pass

    class Meta:
        abstract = True


class Image(OpenLedgerModel):
    # A unique identifier that we assign on ingestion. This is "our" identifier.
    # See the event handler below for the algorithm to generate this value
    identifier = models.UUIDField(unique=True,db_index=True)

    # The provider of the data, typically a partner like Flickr or 500px
    provider = models.CharField(max_length=80, blank=True, null=True, db_index=True)

    # The source of the data, meaning a particular dataset. Source and provider
    # can be different: the Google Open Images dataset is source=openimages,
    # but provider=Flickr (since all images are Flickr-originated)
    source = models.CharField(max_length=80, blank=True, null=True, db_index=True)

    # The identifier that was defined by the source or provider. This may
    # need to be extended to support multiple values when we begin to
    # reconcile duplicates
    foreign_identifier = models.CharField(unique=True, max_length=1000, blank=True, null=True, db_index=True)

    # The entry point URL that we got from the external source, such as the
    # HTTP referrer, or the landing page recorded by the provider/source
    foreign_landing_url = models.CharField(max_length=1000, blank=True, null=True)

    # The actual URL to the primary resolution of the image
    # Note that this is unique!
    url = models.URLField(unique=True, max_length=1000)

    # The primary thumbnail URL for this image
    thumbnail = models.URLField(max_length=1000, blank=True, null=True)

    # Image dimensions, if available
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)

    # The original filesize, if available, in bytes
    filesize = models.IntegerField(blank=True, null=True)

    # The license string as specified in licenses.py
    # This field is _required_, we have no business having a record of an image
    # if we don't know its license
    license = models.CharField(max_length=50)

    # The license version as a string, optional as we may not have good metadata
    # This is a string to accommodate potential oddball/foreign values, but normally
    # should be a decimal like "2.0"
    license_version = models.CharField(max_length=25, blank=True, null=True)

    # The author/creator/licensee, not that we'll know for sure
    creator = models.CharField(max_length=2000, blank=True, null=True)

    # The URL to the creator's identity or profile, if known
    creator_url = models.URLField(max_length=2000, blank=True, null=True)

    # The title of the image, if available
    title = models.CharField(max_length=2000, blank=True, null=True)

    # Denormalized tags as an array, for easier syncing with Elasticsearch
    tags_list = ArrayField(models.CharField(max_length=255), blank=True, null=True)

    tags = JSONField(blank=True, null=True)

    # The last time this image was synced with the URL in `foreign_landing_url`
    # A null value here means we have never synced it
    last_synced_with_source = models.DateTimeField(blank=True, null=True, db_index=True)

    # True if this image has been removed from the source
    removed_from_source = models.BooleanField(default=False)

    # "Tombstone" metadata, only occasionally available
    meta_data = JSONField(blank=True, null=True)

    # The number of views the image has received.
    view_count = models.IntegerField(default=0)

    # Whether the image has been watermarked.
    watermarked = models.NullBooleanField(blank=True, null=True)

    def __str__(self):
        return '%r by %r from %r [%r %r]' % (
        self.title, self.creator, self.provider, self.license, self.license_version)

    def image_tag(self):
        return mark_safe('<img src="%s" width="150" />' % (self.url))

    image_tag.short_description = 'Image'

    class Meta:
        db_table = 'image'
        ordering = ['-created_on']


class ContentProvider(models.Model):
    provider_identifier = models.CharField(max_length=50)
    provider_name = models.CharField(max_length=250, unique=True)
    created_on = models.DateTimeField(auto_now=False)
    domain_name = models.CharField(max_length=500)
    filter_content = models.BooleanField(null=False, default=False)
    notes = models.TextField(null=True)

    class Meta:
        db_table = 'content_provider'

class ImageTags(OpenLedgerModel):
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, blank=True, null=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = (('tag', 'image'))
        db_table = 'image_tags'


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
    # Source can be a provider/source (like 'openimages', or 'user')
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
