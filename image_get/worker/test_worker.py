import json
import pytest
import asyncio
import time
import random
import logging as log
from consumer import poll_consumer, consume
from util import process_image
from PIL import Image
from collections import deque
from enum import Enum, auto
from functools import partial

log.basicConfig(level=log.DEBUG)


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


class FakeImageResponse:
    def __init__(self, status=200):
        self.status = status

    async def read(self):
        # 1024 x 768 sample image
        with open('test_image.jpg', 'rb') as f:
            return f.read()


class FakeAioSession:
    async def get(self, url):
        return FakeImageResponse()


class AioNetworkSimulatingSession:
    """
    It's a FakeAIOSession, but it can simulate network latency, errors,
    and congestion. At 80% of its max load, it will start to slow down and occasionally
    throw an error. At 100%, error rates become very high and response times slow.
    """

    class Load(Enum):
        LOW = auto()
        HIGH = auto()
        OVERLOADED = auto()

    # Under high load, there is a 1/5 chance of an error being returned.
    high_load_status_choices = [403, 200, 200, 200, 200]
    # When overloaded, there's a 4/5 chance of an error being returned.
    overloaded_status_choices = [500, 403, 501, 400, 200]

    def __init__(self, max_requests_per_second=10):
        self.max_requests_per_second = max_requests_per_second
        self.requests_last_second = deque()
        self.load = self.Load.LOW

    def record_request(self):
        """ Record a request and flush out expired records. """
        if self.requests_last_second:
            while self.requests_last_second[0] - time.time() > 1:
                self.requests_last_second.popleft()
        self.requests_last_second.append(time.time())

    def update_load(self):
        load = len(self.requests_last_second) / self.max_requests_per_second
        if load <= 0.8:
            self.load = self.Load.LOW
        elif 0.8 < load < 1:
            self.load = self.Load.HIGH
        else:
            self.load = self.Load.OVERLOADED

    def lag(self):
        """ Determine how long a request should lag based on load. """
        if self.load == self.Load.LOW:
            wait = random.uniform(0.05, 0.15)
        elif self.load == self.Load.HIGH:
            wait = random.uniform(0.15, 0.6)
        # Overloaded
        else:
            wait = random.uniform(2, 5)
        log.debug(f'Lagging {wait}s')
        return wait

    async def get(self, url):
        self.record_request()
        self.update_load()
        await asyncio.sleep(self.lag())
        if self.load == self.Load.HIGH:
            status = random.choice(self.high_load_status_choices)
        elif self.load == self.Load.OVERLOADED:
            status = random.choice(self.overloaded_status_choices)
        else:
            status = 200
        return FakeImageResponse(status)


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
    # validate_thumbnail callback performs the actual assertions
    await process_image(
        persister=validate_thumbnail,
        session=FakeAioSession(),
        url='fake_url',
        identifier='4bbfe191-1cca-4b9e-aff0-1d3044ef3f2d'
    )


async def get_mock_consumer():
    """ Create a mock consumer with a bunch of fake messages in it. """
    consumer = FakeConsumer()
    msgs = [
        {
            'url': 'https://example.gov/hewwo.jpg',
            'uuid': '96136357-6f32-4174-b4ca-ae67e963bc55'
        }
    ]*1000
    encoded_msgs = [json.dumps(msg) for msg in msgs]
    for msg in encoded_msgs:
        consumer.insert(msg)

    aiosession = AioNetworkSimulatingSession()
    image_processor = partial(
        process_image, session=aiosession,
        persister=validate_thumbnail
    )
    return consume(consumer, image_processor, terminate=True)


async def mock_listen():
    consumer = await get_mock_consumer()
    log.debug('Starting consumer')
    await consumer


@pytest.mark.asyncio
async def test_congestion_handling():
    print('----')
    await mock_listen()
