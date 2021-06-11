from django.contrib.postgres.fields import JSONField
from django.db import models
from uuslug import uuslug

import catalog.api.controllers.search_controller as search_controller
from catalog.api.models import OpenLedgerModel
from catalog.api.models.media import (
    AbstractMedia,
    AbstractMediaReport,
    AbstractDeletedMedia,
    AbstractMatureMedia,
    AbstractMediaList,
)
from catalog.api.models.mixins import (
    IdentifierMixin,
    MediaMixin,
    FileMixin,
)


class AudioSet(IdentifierMixin, MediaMixin, FileMixin, OpenLedgerModel):
    """
    This is an ordered collection of audio files, such as a podcast series or
    an album. Not to be confused with AudioList which is a many-to-many
    collection of audio files, like a playlist or favourites library.

    The FileMixin inherited by this model refers not to audio but album art.
    """

    pass


class Audio(AbstractMedia):
    set = models.ForeignKey(
        help_text='Reference to set of which this track is a part.',
        to=AudioSet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    set_position = models.IntegerField(
        blank=True,
        null=True,
        help_text='Ordering of the audio in the set.'
    )

    genre = models.CharField(
        max_length=80,
        blank=True,
        null=True,
        db_index=True,
        help_text='',
    )
    type = models.CharField(
        max_length=80,
        blank=True,
        null=True,
        db_index=True,
        help_text='',
    )

    duration = models.IntegerField(
        blank=True,
        null=True,
        help_text='The time length of the audio file in milliseconds.'
    )
    bit_rate = models.IntegerField(
        blank=True,
        null=True,
        help_text='Number in bits per second, eg. 128000.',
    )
    sample_rate = models.IntegerField(
        blank=True,
        null=True,
        help_text='Number in hertz, eg. 44100.',
    )

    alt_files = JSONField(
        blank=True,
        null=True,
        help_text='JSON describing alternative files for this audio',
    )

    @property
    def alternative_files(self):
        return []  # TODO: Return Python object parsed from `alt_files` field

    class Meta:
        db_table = 'audio'


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
