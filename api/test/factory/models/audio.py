from test.factory.faker import Faker
from test.factory.models.media import IdentifierFactory, MediaFactory

import factory
from factory.django import DjangoModelFactory

from api.models.audio import Audio, AudioAddOn, AudioReport, SensitiveAudio


class SensitiveAudioFactory(DjangoModelFactory):
    class Meta:
        model = SensitiveAudio

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


class AudioReportFactory(DjangoModelFactory):
    class Meta:
        model = AudioReport

    media_obj = factory.SubFactory(AudioFactory)
