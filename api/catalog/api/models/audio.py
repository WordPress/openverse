import catalog.api.controllers.search_controller as search_controller
from catalog.api.models import OpenLedgerModel
from catalog.api.models.media import (
    AbstractAltFile,
    AbstractDeletedMedia,
    AbstractMatureMedia,
    AbstractMedia,
    AbstractMediaList,
    AbstractMediaReport,
)
from catalog.api.models.mixins import FileMixin, ForeignIdentifierMixin, MediaMixin
from django.contrib.postgres.fields import ArrayField
from django.db import models
from uuslug import uuslug


class AltAudioFile(AbstractAltFile):
    def __init__(self, attrs):
        self.bit_rate = attrs.get("bit_rate")
        self.sample_rate = attrs.get("sample_rate")
        super(AltAudioFile, self).__init__(attrs)

    @property
    def sample_rate_in_khz(self):
        return self.sample_rate / 1e3

    @property
    def bit_rate_in_kbps(self):
        return self.bit_rate / 1e3

    def __str__(self):
        br = self.bit_rate_in_kbps
        sr = self.sample_rate_in_khz
        return f"<AltAudioFile {br}kbps / {sr}kHz>"

    def __repr__(self):
        return str(self)


class AudioSet(ForeignIdentifierMixin, MediaMixin, FileMixin, OpenLedgerModel):
    """
    This is an ordered collection of audio files, such as a podcast series or
    an album. Not to be confused with AudioList which is a many-to-many
    collection of audio files, like a playlist or favourites library.

    The FileMixin inherited by this model refers not to audio but album art.
    """

    class Meta:
        db_table = "audioset"  # drop the `api_` prefix
        constraints = [
            models.UniqueConstraint(
                fields=["foreign_identifier", "provider"],
                name="unique_foreign_identifier_provider",
            ),
        ]

    @property
    def identifier(self):
        return f"{self.provider}--{self.foreign_identifier}"

    @property
    def tracks(self):
        return Audio.objects.filter(
            provider=self.provider,
            audio_set_foreign_identifier=self.foreign_identifier,
        )


class AudioFileMixin(FileMixin):
    """
    This mixin adds fields related to audio quality to the standard file mixin.
    Do not use this as the sole base class.
    """

    bit_rate = models.IntegerField(
        blank=True,
        null=True,
        help_text="Number in bits per second, eg. 128000.",
    )
    sample_rate = models.IntegerField(
        blank=True,
        null=True,
        help_text="Number in hertz, eg. 44100.",
    )

    @property
    def sample_rate_in_khz(self):
        return self.sample_rate / 1e3

    @property
    def bit_rate_in_kbps(self):
        return self.bit_rate / 1e3

    class Meta:
        abstract = True


class Audio(AudioFileMixin, AbstractMedia):
    """
    Inherited fields
    ================
    category: eg. music, sound_effect, podcast, news & audiobook
    """

    # Replaces the foreign key to AudioSet
    audio_set_foreign_identifier = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="Reference to set of which this track is a part.",
    )
    audio_set_position = models.IntegerField(
        blank=True, null=True, help_text="Ordering of the audio in the set."
    )

    genres = ArrayField(
        base_field=models.CharField(
            max_length=80,
            blank=True,
        ),
        null=True,
        db_index=True,
        help_text="The artistic style of this audio file, "
        "eg. hip-hop (music) / tech (podcasts).",
    )

    duration = models.IntegerField(
        blank=True,
        null=True,
        help_text="The time length of the audio file in milliseconds.",
    )

    alt_files = models.JSONField(
        blank=True,
        null=True,
        help_text="JSON describing alternative files for this audio.",
    )

    @property
    def alternative_files(self):
        if hasattr(self.alt_files, "__iter__"):
            return [AltAudioFile(alt_file) for alt_file in self.alt_files]
        return None

    @property
    def duration_in_s(self):
        return self.duration / 1e3

    @property
    def audio_set(self):
        try:
            return AudioSet.objects.get(
                provider=self.provider,
                foreign_identifier=self.audio_set_foreign_identifier,
            )
        except AudioSet.DoesNotExist:
            return None

    class Meta(AbstractMedia.Meta):
        db_table = "audio"


class AudioReport(AbstractMediaReport):
    class Meta:
        db_table = "nsfw_reports_audio"

    @property
    def audio_url(self):
        return super(AudioReport, self).url("audio")

    def save(self, *args, **kwargs):
        kwargs.update(
            {
                "index_name": "audio",
                "media_class": Audio,
                "mature_class": MatureAudio,
                "deleted_class": DeletedAudio,
            }
        )
        super(AudioReport, self).save(*args, **kwargs)


class DeletedAudio(AbstractDeletedMedia):
    pass


class MatureAudio(AbstractMatureMedia):
    """Stores all audios that have been flagged as 'mature'."""

    def delete(self, *args, **kwargs):
        es = search_controller.es
        aud = Audio.objects.get(identifier=self.identifier)
        es_id = aud.id
        es.update(index="audio", id=es_id, body={"doc": {"mature": False}})
        super(MatureAudio, self).delete(*args, **kwargs)


class AudioList(AbstractMediaList):
    audios = models.ManyToManyField(
        Audio,
        related_name="lists",
        help_text="A list of identifier keys corresponding to audios.",
    )

    class Meta:
        db_table = "audiolist"

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.title, instance=self)
        super(AudioList, self).save(*args, **kwargs)
