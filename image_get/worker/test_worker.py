from consumer import poll_consumer
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
    res = poll_consumer(consumer=consumer, batch_size=500)
    assert len(res) == 2
