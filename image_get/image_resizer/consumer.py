import settings
from pykafka import KafkaClient
import logging as log
import asyncio
import time


def kafka_connect():
    client = KafkaClient(hosts=settings.KAFKA_HOSTS)
    return client


async def poll_topic():
    pass


async def consume(kafka_topic):
    """
    Listen for inbound image URLs.
    :return:
    """

    topic = kafka_client.topics['inbound_images']
    consumer = topic.get_balanced_consumer(
        consumer_group='image_spiders',
        auto_commit_enable=True,
        zookeeper_connect=settings.ZOOKEEPER_HOST
    )

    urls = []
    while True:
        while len(urls) <= settings.BATCH_SIZE:
            for message in consumer:
                url = str(message.value, 'utf-8')
                urls.append(url)
        process_images(urls)
        urls = []
        time.sleep(0.01)


def process_images(urls):
    tasks = []
    for url in urls:
        tasks.append(process_image(url))


async def process_image(url):
    """ Download and resize an image. """
    pass


if __name__ == '__main__':
    kafka_client = kafka_connect()
    inbound_images = kafka_client.topics['inbound_images']
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume(kafka_topic=inbound_images))

