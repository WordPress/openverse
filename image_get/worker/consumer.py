import settings
import logging as log
import asyncio
import aiohttp
import datetime as dt
import pykafka
import time
from functools import partial
from io import BytesIO
from PIL import Image
from timeit import default_timer as timer


def kafka_connect():
    try:
        client = pykafka.KafkaClient(hosts=settings.KAFKA_HOSTS)
    except pykafka.exceptions.NoBrokersAvailableError:
        log.info('Retrying Kafka connection. . .')
        time.sleep(3)
        return kafka_connect()
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


async def consume(kafka_topic, img_persister):
    """
    Listen for inbound image URLs and process them.

    :param kafka_topic:
    :param img_persister: A function that takes an image as a parameter and
    saves the image to the desired location.
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
        messages = await poll_consumer(consumer, settings.BATCH_SIZE)
        # Schedule resizing tasks
        tasks = []
        start = timer()
        for msg in messages:
            tasks.append(
                process_image(img_persister, session, msg)
            )
        if tasks:
            batch_size = len(tasks)
            log.info(f'Processing image batch of size {batch_size}')
            total += len(tasks)
            await asyncio.gather(*tasks)
            total_time = timer() - start
            log.info(f'resize_rate={batch_size/total_time}/s')
            consumer.commit_offsets()
        else:
            time.sleep(1)


def thumbnail_image(img: Image):
    img.thumbnail(size=settings.TARGET_RESOLUTION, resample=Image.NEAREST)


def save_thumbnail_s3(img):
    pass


def save_thumbnail_local(img):
    pass


async def process_image(persister, session, url):
    """
    Get an image, resize it, and persist it.
    :param persister: The function defining image persistence. It
    should do something like save an image to disk, or upload it to
    S3.
    :param session: An aiohttp client session.
    :param url: The URL of the image.
    :return: None
    """
    loop = asyncio.get_event_loop()
    img_resp = await session.get(url)
    buffer = BytesIO(await img_resp.read())
    img = await loop.run_in_executor(None, partial(Image.open, buffer))
    await loop.run_in_executor(
        None, partial(thumbnail_image, img)
    )
    await loop.run_in_executor(None, partial(persister, img))


if __name__ == '__main__':
    log.basicConfig(level=log.DEBUG)
    kafka_client = kafka_connect()
    inbound_images = kafka_client.topics['inbound_images']
    main = consume(
        kafka_topic=inbound_images,
        img_persister=save_thumbnail_local
    )
    asyncio.run(main)
