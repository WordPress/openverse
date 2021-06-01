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


class Audio(AbstractMedia):
    pass


class AudioReport(AbstractMediaReport):
    class Meta:
        db_table = 'nsfw_reports_audio'

    @property
    def audio_url(self):
        return super(AudioReport, self).url('audio')

    def save(self, *args, **kwargs):
        kwargs.update({
            'index_name': 'audio',
            'media_class': Audio,
            'mature_class': MatureAudio,
            'deleted_class': DeletedAudio,
        })
        super(AudioReport, self).save(*args, **kwargs)


class DeletedAudio(AbstractDeletedMedia):
    pass


class MatureAudio(AbstractMatureMedia):
    """ Stores all audios that have been flagged as 'mature'. """

    def delete(self, *args, **kwargs):
        es = search_controller.es
        aud = Audio.objects.get(identifier=self.identifier)
        es_id = aud.id
        es.update(
            index='audio',
            id=es_id,
            body={'doc': {'mature': False}}
        )
        super(MatureAudio, self).delete(*args, **kwargs)


class AudioList(AbstractMediaList):
    audios = models.ManyToManyField(
        Audio,
        related_name="lists",
        help_text="A list of identifier keys corresponding to audios."
    )

    class Meta:
        db_table = 'audiolist'

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.title, instance=self)
        super(AudioList, self).save(*args, **kwargs)
