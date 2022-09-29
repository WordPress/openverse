from django.conf import settings
from django.db import models

from uuslug import uuslug

from catalog.api.constants.media_types import IMAGE_TYPE
from catalog.api.models.media import (
    AbstractDeletedMedia,
    AbstractMatureMedia,
    AbstractMedia,
    AbstractMediaList,
    AbstractMediaReport,
)
from catalog.api.models.mixins import FileMixin


class ImageFileMixin(FileMixin):
    """
    This mixin adds fields related to image resolution to the standard file
    mixin. Do not use this as the sole base class.
    """

    width = models.IntegerField(
        blank=True,
        null=True,
        help_text="The width of the image in pixels. Not always available.",
    )
    height = models.IntegerField(
        blank=True,
        null=True,
        help_text="The height of the image in pixels. Not always available.",
    )

    @property
    def resolution_in_mp(self):  # ~ MP or megapixels
        return (self.width * self.height) / 1e6

    class Meta:
        abstract = True


class Image(ImageFileMixin, AbstractMedia):
    """
    Inherited fields
    ================
    category: eg. photograph, digitized_artwork & illustration
    """

    class Meta(AbstractMedia.Meta):
        db_table = "image"

    @property
    def mature(self) -> bool:
        return MatureImage.objects.filter(identifier=self.identifier).exists()


class DeletedImage(AbstractDeletedMedia):
    """
    Stores identifiers of images that have been deleted from the source. Do not create
    instances of this model manually. Create an ``ImageReport`` instance instead.
    """

    media_class = Image
    es_index = settings.MEDIA_INDEX_MAPPING[IMAGE_TYPE]


class MatureImage(AbstractMatureMedia):
    """
    Stores all images that have been flagged as 'mature'. Do not create instances of
    this model manually. Create an ``ImageReport`` instance instead.
    """

    media_class = Image
    es_index = settings.MEDIA_INDEX_MAPPING[IMAGE_TYPE]


class ImageReport(AbstractMediaReport):
    media_class = Image
    mature_class = MatureImage
    deleted_class = DeletedImage

    class Meta:
        db_table = "nsfw_reports"

    @property
    def image_url(self):
        return super(ImageReport, self).url("photos")


class ImageList(AbstractMediaList):
    images = models.ManyToManyField(
        Image,
        related_name="lists",
        help_text="A list of identifier keys corresponding to images.",
    )

    class Meta:
        db_table = "imagelist"

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.title, instance=self)
        super(ImageList, self).save(*args, **kwargs)
