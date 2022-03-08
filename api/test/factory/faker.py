from factory import Faker
from faker.providers import BaseProvider
from faker.utils.distribution import choices_distribution


class WaveformProvider(BaseProvider):
    _float_space = [x / 100.0 for x in range(101)] * 20

    @classmethod
    def generate_waveform(cls) -> list[float]:
        return choices_distribution(cls._float_space, p=None, length=1000)

    def waveform(self) -> list[float]:
        return WaveformProvider.generate_waveform()


Faker.add_provider(WaveformProvider)
