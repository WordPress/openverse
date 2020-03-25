import json
from pykafka import KafkaClient
from itertools import cycle, islice

"""
This is a sample image resize event producer.
"""


msgs = [
    {
        'url': 'https://live.staticflickr.com/7454/8728178381_00be690ebc_b.jpg',
        'uuid': 'cdbc3b4a-9b32-4f80-b772-1430251e0fd4'
    },
    {
        'url': 'https://farm4.staticflickr.com/3289/3103459782_1a2041a696_b.jpg',
        'uuid': '3989f25b-21f7-4fce-874f-8a2a6f956a1d'
    },
    {
        'url': 'https://farm9.staticflickr.com/8116/8606654389_e56c706e2c_b.jpg',
        'uuid': 'c29b3ccc-ff8e-4c66-a2d2-d9fc886872ca'
    }
]

encoded_msgs = [json.dumps(msg) for msg in msgs]

client = KafkaClient(hosts='kafka:9092')
topic = client.topics['inbound_images']
with topic.get_sync_producer() as producer:
    for msg in islice(cycle(encoded_msgs), 5000):
        producer.produce(bytes(msg, 'utf-8'))
