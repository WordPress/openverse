import analytics.settings as settings
import json
import logging as log
import urllib.parse as urlparse
from urllib.parse import parse_qs
from uuid import UUID
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


def save_message(msg, database):
    pass


def is_valid(parsed_msg: dict):
    """
    We are only interested in attribution image logs for images that are
    embedded in domains not owned by Creative Commons.
    """
    try:
        referer = parsed_msg['http_referer']
        resource = parsed_msg['resource']
        if 'creativecommons.org' not in referer and '.svg' in resource:
            valid = True
        else:
            valid = False
    except KeyError:
        valid = False

    return valid

def listen(consumer, database):
    msg = consumer.poll(timeout=0.1)
    parsed_msg = parse_message(str(msg.value(), 'utf-8'))
    if is_valid(parsed_msg):
        save_message(msg, database)


if __name__ == '__main__':
    consumer_settings = {
        'bootstrap.servers': settings.KAFKA_HOSTS,
        'group.id': 'image_handlers',
        'auto.offset.reset': 'earliest'
    }
    c = Consumer(consumer_settings)
    listen(c, database_conn)
