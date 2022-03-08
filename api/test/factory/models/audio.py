from test.factory.faker import Faker
from test.factory.models.media import IdentifierFactory, MediaFactory

from catalog.api.models.audio import Audio, AudioAddOn
from factory.django import DjangoModelFactory


class AudioFactory(MediaFactory):
    class Meta:
        model = Audio


class AudioAddOnFactory(DjangoModelFactory):
    class Meta:
        model = AudioAddOn

    audio_identifier = IdentifierFactory(AudioFactory)

    waveform_peaks = Faker("waveform")
