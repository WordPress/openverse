import factory
from factory.django import DjangoModelFactory

from api.models.audio import (
    Audio,
    AudioAddOn,
    AudioReport,
    DeletedAudio,
    SensitiveAudio,
)
from test.factory.faker import Faker
from test.factory.models.media import (
    IdentifierFactory,
    MediaFactory,
    MediaReportFactory,
)


class SensitiveAudioFactory(DjangoModelFactory):
    class Meta:
        model = SensitiveAudio

    media_obj = factory.SubFactory("test.factory.models.audio.AudioFactory")


class DeletedAudioFactory(DjangoModelFactory):
    class Meta:
        model = DeletedAudio

    media_obj = factory.SubFactory("test.factory.models.audio.AudioFactory")


class AudioFactory(MediaFactory):
    _sensitive_factory = SensitiveAudioFactory

    class Meta:
        model = Audio


class AudioAddOnFactory(DjangoModelFactory):
    class Meta:
        model = AudioAddOn

    audio_identifier = IdentifierFactory(AudioFactory)

    waveform_peaks = Faker("waveform")


class AudioReportFactory(MediaReportFactory):
    class Meta:
        model = AudioReport

    media_obj = factory.SubFactory(AudioFactory)
