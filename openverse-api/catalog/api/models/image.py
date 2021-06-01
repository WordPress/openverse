from django.db import models
from uuslug import uuslug

import catalog.api.controllers.search_controller as search_controller
from catalog.api.models.media import (
    AbstractMedia,
    AbstractMediaReport,
    AbstractDeletedMedia,
    AbstractMatureMedia,
    AbstractMediaList,
)


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


class ImageReport(AbstractMediaReport):
    class Meta:
        db_table = 'nsfw_reports'

    @property
    def image_url(self):
        return super(ImageReport, self).url('photos')

    def save(self, *args, **kwargs):
        kwargs.update({
            'index_name': 'image',
            'media_class': Image,
            'mature_class': MatureImage,
            'deleted_class': DeletedImage,
        })
        super(ImageReport, self).save(*args, **kwargs)


class DeletedImage(AbstractDeletedMedia):
    pass


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


class ImageList(AbstractMediaList):
    images = models.ManyToManyField(
        Image,
        related_name="lists",
        help_text="A list of identifier keys corresponding to images."
    )

    class Meta:
        db_table = 'imagelist'

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.title, instance=self)
        super(ImageList, self).save(*args, **kwargs)
