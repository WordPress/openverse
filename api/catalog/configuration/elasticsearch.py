"""
This file contains configuration pertaining to Elasticsearch.
"""

from django.conf import settings

from aws_requests_auth.aws_auth import AWSRequestsAuth
from decouple import config
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch_dsl import connections

from catalog.api.constants.media_types import MEDIA_TYPES


def _elasticsearch_connect():
    """
    Connect to configured Elasticsearch domain.

    :return: An Elasticsearch connection object.
    """

    es_url = config("ELASTICSEARCH_URL", default="localhost")
    es_port = config("ELASTICSEARCH_PORT", default=9200, cast=int)
    es_aws_region = config("ELASTICSEARCH_AWS_REGION", default="us-east-1")

    auth = AWSRequestsAuth(
        aws_access_key=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        aws_host=es_url,
        aws_region=es_aws_region,
        aws_service="es",
    )
    auth.encode = lambda x: bytes(x.encode("utf-8"))
    _es = Elasticsearch(
        host=es_url,
        port=es_port,
        connection_class=RequestsHttpConnection,
        timeout=10,
        max_retries=1,
        retry_on_timeout=True,
        http_auth=auth,
        wait_for_status="yellow",
    )
    _es.info()
    return _es


ES = _elasticsearch_connect()
#: Elasticsearch client, also aliased to connection 'default'

connections.add_connection("default", ES)

MEDIA_INDEX_MAPPING = {
    media_type: config(f"{media_type.upper()}_INDEX_NAME", default=media_type)
    for media_type in MEDIA_TYPES
}
#: mapping of media types to Elasticsearch index names
