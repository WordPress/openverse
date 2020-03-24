from consumer import poll_consumer
from util import process_image
from functools import partial
from io import BytesIO
from PIL import Image
import json
import pytest


class FakeMessage:
    def __init__(self, value):
        self.value = value


class FakeConsumer:
    def __init__(self):
        self.messages = []

    def insert(self, message):
        self.messages.append(
            FakeMessage(bytes(message, 'utf-8'))
        )

    def consume(self, block=True):
        if self.messages:
            return self.messages.pop()
        else:
            return None

    def commit_offsets(self):
        pass


def validate_thumbnail(img, identifier):
    """ Check that the image was resized. """
    i = Image.open(img)
    width, height = i.size
    assert width <= 640 and height <= 480


class FakeResponse:
    async def read(self):
        with open('test_image.jpg', 'rb') as f:
            return f.read()


class FakeAioSession:
    async def get(self, url):
        return FakeResponse()


def test_poll():
    """ Test message polling and parsing."""
    consumer = FakeConsumer()
    msgs = [
        {
            'url': 'http://example.org',
            'uuid': 'c29b3ccc-ff8e-4c66-a2d2-d9fc886872ca'
        },
        {
            'url': 'https://creativecommons.org/fake.jpg',
            'uuid': '4bbfe191-1cca-4b9e-aff0-1d3044ef3f2d'
        }
    ]
    encoded_msgs = [json.dumps(msg) for msg in msgs]
    for msg in encoded_msgs:
        consumer.insert(msg)
    res = poll_consumer(consumer=consumer, batch_size=2)
    assert len(res) == 2


@pytest.mark.asyncio
async def test_pipeline():
    """ Test that the image processor completes with a fake image. """
    await process_image(
        persister=validate_thumbnail,
        session=FakeAioSession(),
        url='fake_url',
        identifier='4bbfe191-1cca-4b9e-aff0-1d3044ef3f2d'
    )
