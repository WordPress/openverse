import analytics.settings as settings
import json
import logging as log
import urllib.parse as urlparse
from urllib.parse import parse_qs
from uuid import UUID
from models import AttributionReferrerEvent
from sqlalchemy import create_engine
from sqlalachemy.orm import sessionmaker
from confluent_kafka import Consumer


def parse_identifier(resource):
    identifier = None
    parsed_url = urlparse.urlparse(resource)
    query = parsed_url.query
    if query:
        try:
            query_parsed = parse_qs(query)
            image_id = query_parsed['image_id'][0]
            identifier = str(UUID(image_id))
        except (KeyError, ValueError, TypeError):
            pass
    return identifier


def parse_message(msg):
    try:
        decoded = json.loads(msg)
        resource = decoded['request'].split(' ')[1]
        _id = parse_identifier(resource)
        parsed = {
            'http_referer': decoded['http_referer'],
            'resource': decoded['request'].split(' ')[1],
            'identifier': _id
        }
    except (json.JSONDecodeError, KeyError):
        log.error(f'Failed to parse {msg}. Reason: ', exc_info=True)
        parsed = None
    return parsed


def save_message(validated_msg: dict, session):
    event = AttributionReferrerEvent(
        image_uuid=validated_msg['identifier'],
        full_referer=validated_msg['http_referer'],
        referer_domain=urlparse.urlparse(validated_msg['http_referer']).netloc,
        resource=validated_msg['resource']
    )
    session.add(event)
    session.commit()


def is_valid(parsed_msg: dict):
    """
    We are only interested in attribution image logs for images that are
    embedded in domains not owned by Creative Commons. We also want to make
    sure that we're only tracking hits on embedded content.
    """
    try:
        referer = parsed_msg['http_referer']
        resource = parsed_msg['resource']
        valid = 'creativecommons.org' not in referer and '.svg' in resource
    except KeyError:
        valid = False
    return valid


def listen(consumer, database):
    while True:
        msg = consumer.poll(timeout=0.1)
        parsed_msg = parse_message(str(msg.value(), 'utf-8'))
        if is_valid(parsed_msg):
            save_message(msg, database)


if __name__ == '__main__':
    consumer_settings = {
        'bootstrap.servers': settings.KAFKA_HOSTS,
        'group.id': 'attribution_streamer',
        'auto.offset.reset': 'earliest'
    }
    c = Consumer(consumer_settings)
    engine = create_engine(settings.DATABASE_CONNECTION)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    listen(c, session)
