from django.conf import settings
from django.db import models

from uuslug import uuslug

from api.constants.media_types import IMAGE_TYPE
from api.models.media import (
    AbstractDeletedMedia,
    AbstractMedia,
    AbstractMediaDecision,
    AbstractMediaDecisionThrough,
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
    One image media instance.

    Inherited fields
    ================
    category: eg. photograph, digitized_artwork & illustration
    """

    class Meta(AbstractMedia.Meta):
        db_table = "image"

    def get_absolute_url(self):
        """Enable the "View on site" link in the Django Admin."""

        from django.urls import reverse

        return reverse("image-detail", args=[str(self.identifier)])

    @property
    def sensitive(self) -> bool:
        return hasattr(self, "sensitive_image")


class DeletedImage(AbstractDeletedMedia):
    """
    Images deleted from the upstream source.

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
    Images with verified sensitivity reports.

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
    """
    User-submitted report of an image.

    This contains an ``ImageDecision`` as well, if moderators have made a decision
    for this report.
    """

    media_class = Image

    media_obj = models.ForeignKey(
        to="Image",
        to_field="identifier",
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        db_column="identifier",
        related_name="image_report",
        help_text="The reference to the image being reported.",
    )
    decision = models.ForeignKey(
        to="ImageDecision",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="The moderation decision for this report.",
    )

    class Meta:
        db_table = "nsfw_reports"


class ImageDecision(AbstractMediaDecision):
    """Moderation decisions taken for images."""

    media_class = Image

    media_objs = models.ManyToManyField(
        to="Image",
        through="ImageDecisionThrough",
        help_text="The image items being moderated.",
    )


class ImageDecisionThrough(AbstractMediaDecisionThrough):
    """
    Many-to-many reference table for image decisions.

    This is made explicit (rather than using Django's default) so that the image can
    be referenced by `identifier` rather than an arbitrary `id`.
    """

    media_obj = models.ForeignKey(
        Image,
        to_field="identifier",
        on_delete=models.CASCADE,
        db_column="identifier",
    )
    decision = models.ForeignKey(ImageDecision, on_delete=models.CASCADE)


class ImageList(AbstractMediaList):
    """A list of images. Currently unused."""

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
