import asyncio
import json
import logging as log
import time
from functools import partial
from io import BytesIO

import pykafka
from PIL import Image

import settings


def kafka_connect():
    try:
        client = pykafka.KafkaClient(hosts=settings.KAFKA_HOSTS)
    except pykafka.exceptions.NoBrokersAvailableError:
        log.info('Retrying Kafka connection. . .')
        time.sleep(3)
        return kafka_connect()
    return client


def parse_message(message):
    decoded = json.loads(str(message.value, 'utf-8'))
    return decoded


def thumbnail_image(img: Image):
    img.thumbnail(size=settings.TARGET_RESOLUTION, resample=Image.NEAREST)
    output = BytesIO()
    img.save(output, format="JPEG", quality=30)
    output.seek(0)
    return output


def save_thumbnail_s3(s3_client, img: BytesIO, identifier):
    s3_client.put_object(
        Bucket='cc-image-analysis',
        Key=f'{identifier}.jpg',
        Body=img
    )


def save_thumbnail_local(img: BytesIO):
    pass


async def process_image(persister, session, url, identifier):
    """
    Get an image, resize it, and persist it.
    :param persister: The function defining image persistence. It
    should do something like save an image to disk, or upload it to
    S3.
    :param session: An aiohttp client session.
    :param url: The URL of the image.
    """
    loop = asyncio.get_event_loop()
    img_resp = await session.get(url)
    buffer = BytesIO(await img_resp.read())
    img = await loop.run_in_executor(None, partial(Image.open, buffer))
    thumb = await loop.run_in_executor(
        None, partial(thumbnail_image, img)
    )
    await loop.run_in_executor(
        None, partial(persister, img=thumb, identifier=identifier)
    )
