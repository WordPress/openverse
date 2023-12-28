"""This file contains configuration pertaining to Elasticsearch."""

from decouple import config
from elasticsearch import Elasticsearch
from elasticsearch_dsl import connections

from api.constants.media_types import MEDIA_TYPES


def _elasticsearch_connect() -> tuple[Elasticsearch, str]:
    """
    Connect to configured Elasticsearch domain.

    :return: An Elasticsearch connection object.
    """

    es_scheme = config("ELASTICSEARCH_SCHEME", default="http://")
    es_url = config("ELASTICSEARCH_URL", default="localhost")
    es_port = config("ELASTICSEARCH_PORT", default=9200, cast=int)

    es_endpoint = f"{es_scheme}{es_url}:{es_port}"

    _es = Elasticsearch(
        es_endpoint,
        # TODO: Return to default timeout of 10s and 1 retry once
        # TODO: Elasticsearch response time has been stabilized
        request_timeout=12,
        max_retries=3,
        retry_on_timeout=True,
    )
    _es.info()
    _es.cluster.health(wait_for_status="yellow")
    return _es, es_endpoint


SETUP_ES = config("SETUP_ES", default=True, cast=bool)
if SETUP_ES:
    ES, ES_ENDPOINT = _elasticsearch_connect()
    #: Elasticsearch client, also aliased to connection 'default'

    connections.add_connection("default", ES)
else:
    ES, ES_ENDPOINT = None, None

MEDIA_INDEX_MAPPING = {
    media_type: config(f"{media_type.upper()}_INDEX_NAME", default=media_type)
    for media_type in MEDIA_TYPES
}
#: mapping of media types to Elasticsearch index names
