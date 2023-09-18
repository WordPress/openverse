"""This file contains configuration pertaining to Elasticsearch."""

from aws_requests_auth.aws_auth import AWSRequestsAuth
from decouple import config
from elastic_transport import RequestsHttpNode
from elasticsearch import Elasticsearch
from elasticsearch_dsl import connections

from api.constants.media_types import MEDIA_TYPES
from conf.settings.aws import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


def _elasticsearch_connect() -> tuple[Elasticsearch, str]:
    """
    Connect to configured Elasticsearch domain.

    :return: An Elasticsearch connection object.
    """

    es_scheme = config("ELASTICSEARCH_SCHEME", default="http://")
    es_url = config("ELASTICSEARCH_URL", default="localhost")
    es_port = config("ELASTICSEARCH_PORT", default=9200, cast=int)
    es_aws_region = config("ELASTICSEARCH_AWS_REGION", default="us-east-1")

    es_endpoint = f"{es_scheme}{es_url}:{es_port}"

    auth = AWSRequestsAuth(
        aws_access_key=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_host=es_url,
        aws_region=es_aws_region,
        aws_service="es",
    )
    auth.encode = lambda x: bytes(x.encode("utf-8"))
    _es = Elasticsearch(
        es_endpoint,
        request_timeout=10,
        max_retries=1,
        retry_on_timeout=True,
        basic_auth=auth,
        node_class=RequestsHttpNode,
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
