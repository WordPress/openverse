import settings
import logging as log
import asyncio
import aiohttp
from functools import partial
from pykafka import KafkaClient
from io import BytesIO
from PIL import Image


def kafka_connect():
    client = KafkaClient(hosts=settings.KAFKA_HOSTS)
    return client


def _parse_message(message):
    log.debug(f'Received {message}')
    return str(message.value, 'utf-8')


async def poll_consumer(consumer, batch_size):
    """
    Poll the Kafka consumer for a batch of messages and parse them.
    :param consumer:
    :param batch_size:
    :return:
    """
    batch = []
    for idx, message in enumerate(consumer):
        parsed = _parse_message(message)
        batch.append(parsed)
        if idx >= batch_size:
            break
    return batch


async def consume(kafka_topic):
    """
    Listen for inbound image URLs.
    :return:
    """
    consumer = kafka_topic.get_balanced_consumer(
        consumer_group='image_spiders',
        auto_commit_enable=True,
        zookeeper_connect=settings.ZOOKEEPER_HOST
    )
    session = aiohttp.ClientSession()
    while True:
        messages = await poll_consumer(consumer, settings.BATCH_SIZE)
        # Schedule resizing tasks
        tasks = []
        for msg in messages:
            tasks.append(process_image(session, msg))
        await asyncio.gather(*tasks)


def thumbnail_image(img: Image):
    img.thumbnail(size=settings.TARGET_RESOLUTION, resample=Image.NEAREST)


async def process_image(session, url):
    """Get an image, resize it, and upload it to S3."""
    loop = asyncio.get_event_loop()
    img_resp = await session.get(url)
    img = Image.open(BytesIO(img_resp.content))
    await loop.run_in_executor(None, partial(thumbnail_image, img))


if __name__ == '__main__':
    kafka_client = kafka_connect()
    inbound_images = kafka_client.topics['inbound_images']
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume(kafka_topic=inbound_images))

