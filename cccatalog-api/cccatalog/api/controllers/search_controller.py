from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.exceptions import AuthenticationException, \
    AuthorizationException
from elasticsearch_dsl import Q, Search, connections
from elasticsearch_dsl.response import Response
from cccatalog import settings
from django.core.cache import cache
from cccatalog.api.models import ContentProvider

import logging as log

ELASTICSEARCH_MAX_RESULT_WINDOW = 10000
CACHE_TIMEOUT = 10


def search(search_params, index, page_size, page=1) -> Response:
    """
    Given a set of keywords and an optional set of filters, perform a ranked
    paginated search.

    :param search_params: Search parameters. See
     :class: `~cccatalog.api.search_serializers.SearchQueryStringSerializer`.
    :param index: The Elasticsearch index to search (e.g. 'image')
    :param page_size: The number of results to return per page.
    :param page: The results page number.
    :return: An Elasticsearch Response object.
    """
    s = Search(index=index)

    # Paginate search query.
    start_slice = page_size * (page - 1)
    end_slice = page_size * page
    if start_slice + end_slice > ELASTICSEARCH_MAX_RESULT_WINDOW:
        raise ValueError("Deep pagination is not allowed.")
    s = s[start_slice:end_slice]

    # If any filters are specified, add them to the query.
    if 'li' in search_params.data or 'lt' in search_params.data:
        license_field = 'li' if 'li' in search_params.data else 'lt'
        license_filters = []
        for _license in search_params.data[license_field].split(','):
            license_filters.append(Q("term", license__keyword=_license))
        s = s.filter('bool', should=license_filters, minimum_should_match=1)
    if 'provider' in search_params.data:
        provider_filters = []
        for provider in search_params.data['provider'].split(','):
            provider_filters.append(Q("term", provider=provider))
        s = s.filter('bool', should=provider_filters, minimum_should_match=1)
    if 'creator' in search_params.data:
        creator_filter = Q("term", creator=search_params.data['creator'])
        s = s.filter('bool', should=creator_filter, minimum_should_match=1)

    # It is sometimes desirable to hide content providers from the catalog
    # without scrubbing them from the database or reindexing.
    filter_cache_key = 'filtered_providers'
    filtered_providers = cache.get(key=filter_cache_key)
    if not filtered_providers:
        filtered_providers = ContentProvider.objects\
            .filter(filter_content=True)\
            .values('provider_identifier')
        cache.set(
            key=filter_cache_key,
            timeout=CACHE_TIMEOUT,
            value=filtered_providers
        )
    for filtered in filtered_providers:
        s = s.exclude("match", provider=filtered['provider_identifier'])

    # Search for keywords.
    keywords = ' '.join(search_params.data['q'].lower().split(','))
    s = s.query("constant_score", filter=Q("multi_match",
                query=keywords,
                fields=['legacy_tags', 'tags.name', 'title'],
                operator='AND'))
    s.extra(track_scores=True)
    search_response = s.execute()
    return search_response


def get_providers(index):
    """
    Given an index, find all available data providers and return their counts.

    :param index: An Elasticsearch index, such as `'image'`.
    :return: A dictionary mapping providers to the count of their images.`
    """
    provider_cache_name = 'providers-' + index
    providers = cache.get(key=provider_cache_name)
    if type(providers) == list:
        # Invalidate old provider format.
        cache.delete(key=provider_cache_name)
    if not providers:
        elasticsearch_maxint = 2147483647
        agg_body = {
            'aggs': {
                'unique_providers': {
                    'terms': {
                        'field': 'provider.keyword',
                                 'size': elasticsearch_maxint,
                        "order": {
                            "_key": "desc"
                        }
                    }
                }
            }
        }
        s = Search.from_dict(agg_body)
        s = s.index(index)
        results = s.execute().aggregations['unique_providers']['buckets']
        providers = {result['key']: result['doc_count'] for result in results}
        cache.set(
            key=provider_cache_name,
            timeout=CACHE_TIMEOUT,
            value=providers
        )
    return providers


def _elasticsearch_connect():
    """
    Connect to configured Elasticsearch domain.

    :return: An Elasticsearch connection object.
    """
    try:
        log.info('Trying to connect to Elasticsearch without authentication...')
        # Try to connect to Elasticsearch without credentials.
        _es = Elasticsearch(
            host=settings.ELASTICSEARCH_URL,
            port=settings.ELASTICSEARCH_PORT,
            connection_class=RequestsHttpConnection,
            timeout=10,
            max_retries=99,
            wait_for_status='yellow'
        )
        log.info(str(_es.info()))
        log.info('Connected to Elasticsearch without authentication.')
    except (AuthenticationException, AuthorizationException):
        # If that fails, supply AWS authentication object and try again.
        log.info(
            'Connecting to %s %s with AWS auth', settings.ELASTICSEARCH_URL,
            settings.ELASTICSEARCH_PORT)
        auth = AWSRequestsAuth(
            aws_access_key=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_host=settings.ELASTICSEARCH_URL,
            aws_region=settings.ELASTICSEARCH_AWS_REGION,
            aws_service='es'
        )
        auth.encode = lambda x: bytes(x.encode('utf-8'))
        _es = Elasticsearch(
            host=settings.ELASTICSEARCH_URL,
            port=settings.ELASTICSEARCH_PORT,
            connection_class=RequestsHttpConnection,
            timeout=10,
            max_retries=99,
            retry_on_timeout=True,
            http_auth=auth,
            wait_for_status='yellow'
        )
        _es.info()
    return _es


es = _elasticsearch_connect()
connections.connections.add_connection('default', es)
