import settings
import logging as log
import asyncio
import aiohttp
import boto3
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
    last_msg_time = timer()
    msg_count = 0
    while msg_count < batch_size and elapsed_time < max_wait_seconds:
        message = consumer.consume(block=False)
        if message:
            parsed = _parse_message(message)
            batch.append(parsed)
            last_msg_time = timer()
            msg_count += 1
        elapsed_time = timer() - last_msg_time
    return batch


async def consume(consumer, image_processor):
    """
    Listen for inbound image URLs and process them.
    :param consumer: A Kafka consumer listening to the inbound images topic.
    :param image_processor: A partial function that handles an image.
    """
    session = aiohttp.ClientSession()
    total = 0
    while True:
        messages = await poll_consumer(consumer, settings.BATCH_SIZE)
        # Schedule resizing tasks
        tasks = []
        start = timer()
        for msg in messages:
            tasks.append(
                image_processor(session=session, url=msg)
            )
        if tasks:
            batch_size = len(tasks)
            log.info(f'batch_size={batch_size}')
            total += batch_size
            await asyncio.gather(*tasks)
            total_time = timer() - start
            log.info(f'resize_rate={batch_size/total_time}/s')
            log.info(f'batch_time={total_time}s')
            consumer.commit_offsets()
        else:
            time.sleep(1)


def thumbnail_image(img: Image):
    img.thumbnail(size=settings.TARGET_RESOLUTION, resample=Image.NEAREST)
    output = BytesIO()
    img.save(output, format="JPEG")
    output.seek(0)
    return output


def save_thumbnail_s3(s3_client, img: BytesIO, identifier):
    s3_client\
        .Bucket('cc-image-analysis')\
        .put_object(Key=f'{identifier}.jpg', Body=img)


def save_thumbnail_local(img: BytesIO):
    pass


async def process_image(persister, session, url, s3=None):
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
    thumb = await loop.run_in_executor(
        None, partial(thumbnail_image, img)
    )
    await loop.run_in_executor(None, partial(persister, s3, thumb))


if __name__ == '__main__':
    log.basicConfig(level=log.INFO)
    kafka_client = kafka_connect()
    session = boto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    s3 = session.resource('s3')
    inbound_images = kafka_client.topics['inbound_images']
    consumer = inbound_images.get_balanced_consumer(
        consumer_group='image_resizers',
        auto_commit_enable=True,
        zookeeper_connect=settings.ZOOKEEPER_HOST
    )
    image_processor = partial(
        process_image,
        persister=save_thumbnail_s3,
        s3=s3
    )
    main = consume(consumer, image_processor)
    asyncio.run(main)
