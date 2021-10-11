import mimetypes

from django.db import models


class IdentifierMixin(models.Model):
    """
    This mixin adds fields related to unique ID, both internal and external, to
    any model. Do not use this as the sole base class.

    The mixins adds
    - identifier: UUIDField
    - foreign_identifier: CharField
    """

    identifier = models.UUIDField(
        unique=True,
        db_index=True,
        help_text="Our unique identifier for an open-licensed work.",
    )
    foreign_identifier = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        db_index=True,
        help_text="The identifier provided by the upstream source.",
    )

    class Meta:
        abstract = True


class MediaMixin(models.Model):
    """
    This mixin adds fields related to a creative creation such as the title of
    the work and info about the artist. Do not use this as the sole base class.

    The mixin adds
    - title: CharField
    - foreign_landing_url: CharField
    - creator: CharField
    - creator_url: CharField
    """

    title = models.CharField(max_length=2000, blank=True, null=True)
    foreign_landing_url = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="The landing page of the work.",
    )

    creator = models.CharField(max_length=2000, blank=True, null=True)
    creator_url = models.URLField(max_length=2000, blank=True, null=True)

    # Because all forms of media have a thumbnail for visual representation
    thumbnail = models.URLField(
        max_length=1000, blank=True, null=True, help_text="The thumbnail for the media."
    )

    class Meta:
        abstract = True


class FileMixin(models.Model):
    """
    This mixin adds fields related to file such as the file URL and size to any
    model. Do not use this as the sole base class.
    """

    url = models.URLField(
        unique=True, max_length=1000, help_text="The actual URL to the media file."
    )
    filesize = models.IntegerField(
        blank=True,
        null=True,
        help_text="Number in bytes, e.g. 1024.",
        # Bytes for parity with the HTTP Content-Length header
    )
    filetype = models.CharField(
        max_length=80,
        blank=True,
        null=True,
        help_text="The type of the file, related to the file extension.",
    )

    @property
    def size_in_mib(self):  # ~ MiB or mibibytes
        return self.filesize / 2 ** 20

    @property
    def size_in_mbs(self):  # ~ MB or megabytes
        return self.filesize / 1e6

    @property
    def mime_type(self):
        """
        Get the MIME type of the file inferred from the extension of the file.
        :return: the inferred MIME type of the file
        """

        return mimetypes.types_map[f".{self.filetype}"]

    class Meta:
        abstract = True
