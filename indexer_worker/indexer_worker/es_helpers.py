import logging as log
import time

from decouple import config
from elasticsearch import ConnectionError as EsConnectionError
from elasticsearch import Elasticsearch


def elasticsearch_connect(timeout: int = 300) -> Elasticsearch:
    """
    Repeatedly try to connect to Elasticsearch until successful.

    :param timeout: the amount of time in seconds to wait for a successful connection
    :return: an Elasticsearch client.
    """

    while timeout > 0:
        try:
            return _elasticsearch_connect()
        except EsConnectionError as err:
            log.exception(err)
            log.error("Reconnecting to Elasticsearch in 5 seconds...")
            timeout -= 5
            time.sleep(5)
            continue


def _elasticsearch_connect() -> Elasticsearch:
    """
    Connect to an Elasticsearch indices at the configured domain.

    This method also handles AWS authentication using the AWS access key ID and the
    secret access key.

    :return: an Elasticsearch client
    """

    es_scheme = config("ELASTICSEARCH_SCHEME", default="http://")
    es_url = config("ELASTICSEARCH_URL", default="localhost")
    es_port = config("ELASTICSEARCH_PORT", default=9200, cast=int)

    es_endpoint = f"{es_scheme}{es_url}:{es_port}"

    timeout = 12  # hours

    es = Elasticsearch(
        es_endpoint,
        timeout=timeout * 3600,  # seconds
    )
    es.info()
    return es
