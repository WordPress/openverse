from django.db import models
from django.utils.html import format_html
from uuslug import uuslug

import catalog.api.controllers.search_controller as search_controller
from catalog.api.models.media import (
    AbstractMedia,
    AbstractMediaReport,
    AbstractDeletedMedia,
    AbstractMatureMedia,
    AbstractMediaList,

    PENDING,
    MATURE_FILTERED,
    DEINDEXED,
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
