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
        # A search holds a pooled DB connection for as long as ES takes to
        # answer, so a generous timeout with retries (previously 12 s × 4
        # attempts) lets a slow cluster exhaust the pool and take the whole
        # task down. Fail the one slow request instead.
        request_timeout=config("ELASTICSEARCH_REQUEST_TIMEOUT", default=8, cast=float),
        max_retries=config("ELASTICSEARCH_MAX_RETRIES", default=1, cast=int),
        retry_on_timeout=config(
            "ELASTICSEARCH_RETRY_ON_TIMEOUT", default=False, cast=bool
        ),
        # The transport keeps a blocking urllib3 pool of this many sockets per
        # node (default 10) and waits for a free one with no deadline, so
        # ``request_timeout`` never covers that wait. With a slow cluster the
        # client-side queue grew to minutes while each queued search held a
        # Django thread and a pooled DB connection. Keep this at least as large
        # as ``DJANGO_DATABASE_POOL_MAX_SIZE`` so the DB pool, which does have
        # a timeout, is the only concurrency limit per task.
        connections_per_node=config(
            "ELASTICSEARCH_CONNECTIONS_PER_NODE", default=32, cast=int
        ),
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
