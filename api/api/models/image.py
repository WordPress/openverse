from django.conf import settings
from django.db import models

from uuslug import uuslug

from api.constants.media_types import IMAGE_TYPE
from api.models.media import (
    AbstractDeletedMedia,
    AbstractMedia,
    AbstractMediaDecision,
    AbstractMediaList,
    AbstractMediaReport,
    AbstractSensitiveMedia,
)
from api.models.mixins import FileMixin


class ImageFileMixin(FileMixin):
    """
    This mixin adds fields related to image resolution to the standard file mixin.

    Do not use this as the sole base class.
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
    Represents one image media instance.

    Inherited fields
    ================
    category: eg. photograph, digitized_artwork & illustration
    """

    class Meta(AbstractMedia.Meta):
        db_table = "image"

    @property
    def sensitive(self) -> bool:
        return hasattr(self, "sensitive_image")


class DeletedImage(AbstractDeletedMedia):
    """
    Stores identifiers of images that have been deleted from the source.

    Do not create instances of this model manually. Create an ``ImageReport`` instance
    instead.
    """

    media_class = Image
    es_index = settings.MEDIA_INDEX_MAPPING[IMAGE_TYPE]

    media_obj = models.OneToOneField(
        to="Image",
        to_field="identifier",
        on_delete=models.DO_NOTHING,
        primary_key=True,
        db_constraint=False,
        db_column="identifier",
        related_name="deleted_image",
        help_text="The reference to the deleted image.",
    )


class SensitiveImage(AbstractSensitiveMedia):
    """
    Stores all images that have been flagged as 'mature'.

    Do not create instances of this model manually. Create an ``ImageReport`` instance
    instead.
    """

    media_class = Image
    es_index = settings.MEDIA_INDEX_MAPPING[IMAGE_TYPE]

    media_obj = models.OneToOneField(
        to="Image",
        to_field="identifier",
        on_delete=models.DO_NOTHING,
        primary_key=True,
        db_constraint=False,
        db_column="identifier",
        related_name="sensitive_image",
        help_text="The reference to the sensitive image.",
    )

    class Meta:
        db_table = "api_matureimage"


class ImageReport(AbstractMediaReport):
    media_class = Image
    sensitive_class = SensitiveImage
    deleted_class = DeletedImage
    url_frag = "images"

    media_obj = models.ForeignKey(
        to="Image",
        to_field="identifier",
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        db_column="identifier",
        related_name="image_report",
        help_text="The reference to the image being reported.",
    )

    class Meta:
        db_table = "nsfw_reports"


class ImageDecision(AbstractMediaDecision):
    """Represents moderation decisions taken for images."""

    media_class = Image

    media_objs = models.ManyToManyField(
        to="Image",
        db_constraint=False,
        help_text="The image items being moderated.",
    )


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
        super().save(*args, **kwargs)
