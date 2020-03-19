import settings
import logging as log
import asyncio
import aiohttp
import datetime as dt
from functools import partial
from pykafka import KafkaClient
from io import BytesIO
from PIL import Image


def kafka_connect():
    client = KafkaClient(hosts=settings.KAFKA_HOSTS)
    return client


def _parse_message(message):
    decoded = str(message.value, 'utf-8')
    return decoded


async def poll_consumer(consumer, batch_size):
    """
    Poll the Kafka consumer for a batch of messages and parse them.
    :param consumer:
    :param batch_size: The number of events to return from the queue.
    :return:
    """
    batch = []
    # Consume messages until either batch_size has been reached or the max
    # wait time has occurred.
    max_wait_seconds = 3
    elapsed_time = 0
    last_msg_time = dt.datetime.now()
    msg_count = 0
    while msg_count < batch_size and elapsed_time < max_wait_seconds:
        message = consumer.consume(block=False)
        if message:
            parsed = _parse_message(message)
            batch.append(parsed)
            last_msg_time = dt.datetime.now()
            msg_count += 1
        elapsed_time = (dt.datetime.now() - last_msg_time).total_seconds()
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
    total = 0
    while True:
        start = dt.datetime.now()
        messages = await poll_consumer(consumer, settings.BATCH_SIZE)
        # Schedule resizing tasks
        tasks = []
        for msg in messages:
            tasks.append(process_image(session, msg))
        if tasks:
            log.info('Processing image batch of size {}'.format(len(tasks)))
            total += len(tasks)
            total_time = (dt.datetime.now() - start).total_seconds()
            log.info(f'Last batch took {total_time}s. Total resized so far:'
                     f' {total}')
        await asyncio.gather(*tasks)
        consumer.commit_offsets()


def thumbnail_image(img: Image):
    img.thumbnail(size=settings.TARGET_RESOLUTION, resample=Image.NEAREST)


def save_thumbnail(img):
    pass


async def process_image(session, url):
    """Get an image, resize it, and upload it to S3."""
    loop = asyncio.get_event_loop()
    img_resp = await session.get(url)
    buffer = BytesIO(await img_resp.read())
    img = Image.open(buffer)
    await loop.run_in_executor(None, partial(thumbnail_image, img))
    await loop.run_in_executor(None, partial(save_thumbnail, img))
    log.debug(f'Successfully resized image {url}')


if __name__ == '__main__':
    log.basicConfig(level=log.DEBUG)
    kafka_client = kafka_connect()
    inbound_images = kafka_client.topics['inbound_images']
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume(kafka_topic=inbound_images))

