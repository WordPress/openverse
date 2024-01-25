import factory
from factory.django import DjangoModelFactory

from api.models.audio import Audio, AudioAddOn, AudioReport, MatureAudio
from test.factory.faker import Faker
from test.factory.models.media import IdentifierFactory, MediaFactory


class MatureAudioFactory(DjangoModelFactory):
    class Meta:
        model = MatureAudio

    media_obj = factory.SubFactory("test.factory.models.audio.AudioFactory")


class AudioFactory(MediaFactory):
    _mature_factory = MatureAudioFactory

    class Meta:
        model = Audio


class AudioAddOnFactory(DjangoModelFactory):
    class Meta:
        model = AudioAddOn

    audio_identifier = IdentifierFactory(AudioFactory)

    waveform_peaks = Faker("waveform")


class AudioReportFactory(DjangoModelFactory):
    class Meta:
        model = AudioReport

    media_obj = factory.SubFactory(AudioFactory)
