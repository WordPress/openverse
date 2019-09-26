from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.exceptions import AuthenticationException, \
    AuthorizationException, NotFoundError
from elasticsearch_dsl import Q, Search, connections
from elasticsearch_dsl.response import Response
from cccatalog import settings
from django.core.cache import cache
from cccatalog.api.models import ContentProvider
from rest_framework import serializers
from cccatalog.api.utils.validate_images import validate_images
import logging as log
import time

ELASTICSEARCH_MAX_RESULT_WINDOW = 10000
CACHE_TIMEOUT = 10


def _paginate_search(s: Search, page_size: int, page: int):
    """
    Select the start and end of the search results for this query.
    """
    # Paginate search query.
    start_slice = page_size * (page - 1)
    end_slice = page_size * page
    if start_slice + end_slice > ELASTICSEARCH_MAX_RESULT_WINDOW:
        raise ValueError("Deep pagination is not allowed.")
    s = s[start_slice:end_slice]
    return s


def _filter_licenses(s: Search, licenses):
    """
    Filter out all licenses except for those provided in the `licenses`
    parameter.
    """
    if not licenses:
        return s
    license_filters = []
    for _license in licenses.split(','):
        license_filters.append(Q('term', license__keyword=_license))
    s = s.filter('bool', should=license_filters, minimum_should_match=1)
    return s


def _quote_escape(query_string):
    """
    If there are any unmatched quotes in the query supplied by the user, ignore
    them.
    """
    num_quotes = query_string.count('"')
    if num_quotes % 2 == 1:
        return query_string.replace('"', '\\"')
    else:
        return query_string


def _get_dead_items(s: Search, start_page, page_size):
    """
    Given a search object, look ahead several pages and check that the links
    are still valid. Return a list of broken links.

    :param s:
    :return: A list of UUIDs with broken links.
    """
    start_slice = page_size * (start_page - 1)
    end_slice = start_slice + (page_size * 3)
    _s = s[start_slice:end_slice]
    _s = _s.extra(_source={"includes": ["identifier", "url"]})
    unfiltered_links = _s.execute()
    image_urls = [res.url for res in unfiltered_links]
    image_ids = [res.identifier for res in unfiltered_links]
    broken_ids = validate_images(image_urls, image_ids)
    return broken_ids


def _exclude_id_list(s: Search, identifiers: list):
    """
    Exclude a list of identifiers from a search query.
    """
    if len(identifiers) == 0:
        return s
    log.info('Excluding from search: {}'.format(identifiers))
    s = s.exclude('terms', identifier__keyword=identifiers)
    return s


def _exclude_dead(s: Search, start_page, page_size):
    """
    Given a search query, filter out the dead links.
    """
    start_time = time.time()
    dead = _get_dead_items(s, start_page, page_size)
    s = _exclude_id_list(s, dead)
    total_time = time.time() - start_time
    log.info('Excluded dead links in {}'.format(total_time))
    return s


def search(search_params, index, page_size, ip, filter_rot, page=1) -> Response:
    """
    Given a set of keywords and an optional set of filters, perform a ranked
    paginated search.

    :param search_params: Search parameters. See
     :class: `~cccatalog.api.search_serializers.SearchQueryStringSerializer`.
    :param index: The Elasticsearch index to search (e.g. 'image')
    :param page_size: The number of results to return per page.
    :param page: The results page number.
    :param ip: The user's hashed IP. Hashed IPs are used to anonymously but
    uniquely identify users exclusively for ensuring query consistency across
    Elasticsearch shards.
    :param filter_rot: Whether to filter dead links
    :return: An Elasticsearch Response object.
    """
    s = Search(index=index)
    s = _paginate_search(s, page_size, page)
    # Add requested filters.
    if 'li' in search_params.data:
        s = _filter_licenses(s, search_params.data['li'])
    elif 'lt' in search_params.data:
        s = _filter_licenses(s, search_params.data['lt'])

    if 'provider' in search_params.data:
        provider_filters = []
        for provider in search_params.data['provider'].split(','):
            provider_filters.append(Q('term', provider=provider))
        s = s.filter('bool', should=provider_filters, minimum_should_match=1)
    if 'extension' in search_params.data:
        extension = search_params.data['extension']
        extension_filter = Q('term', extension=extension)
        s = s.filter('bool', should=extension_filter, minimum_should_match=1)

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
        s = s.exclude('match', provider=filtered['provider_identifier'])

    # Search either by generic multimatch or by "advanced search" with
    # individual field-level queries specified.
    search_fields = ['tags.name', 'title', 'description']
    if 'q' in search_params.data:
        query = _quote_escape(search_params.data['q'])
        s = s.query(
            'query_string',
            query=query,
            fields=search_fields,
            type='most_fields'
        )
    else:
        if 'creator' in search_params.data:
            creator = _quote_escape(search_params.data['creator'])
            s = s.query(
                'query_string', query=creator, default_field='creator'
            )
        if 'title' in search_params.data:
            title = _quote_escape(search_params.data['title'])
            s = s.query(
                'query_string', query=title, default_field='title'
            )
        if 'tags' in search_params.data:
            tags = _quote_escape(search_params.data['tags'])
            s = s.query(
                'query_string',
                default_field='tags.name',
                query=tags
            )

    # Use highlighting to determine which fields contribute to the selection of
    # top results.
    s = s.highlight(*search_fields)
    s = s.highlight_options(order='score')
    s.extra(track_scores=True)
    # Route users to the same Elasticsearch worker node to reduce
    # pagination inconsistencies and increase cache hits.
    s = s.params(preference=str(ip))
    if filter_rot:
        s = _exclude_dead(s, page, page_size)
    search_response = s.execute()
    return search_response


def _validate_provider(input_provider):
    allowed_providers = list(get_providers('image').keys())
    lowercase_providers = [x.lower() for x in allowed_providers]
    if input_provider.lower() not in lowercase_providers:
        raise serializers.ValidationError(
            "Provider \'{}\' does not exist.".format(input_provider)
        )
    return input_provider.lower()


def related_images(uuid, index):
    """
    Given a UUID, find related search results.
    """
    # Convert UUID to sequential ID.
    item = Search(index=index)
    item = item.query(
        'match',
        identifier=uuid
    )
    _id = item.execute().hits[0].id

    s = Search(index=index)
    s = s.query(
        'more_like_this',
        fields=['tags.name', 'title', 'creator'],
        like={
            '_index': index,
            '_id': _id
        },
        min_term_freq=1,
        max_query_terms=50
    )
    s = _exclude_dead(s, 1, 20)
    response = s.execute()

    return response


def browse_by_provider(
        provider, index, page_size, ip, filter_rot, page=1, lt=None, li=None):
    """
    Allow users to browse image collections without entering a search query.
    """
    _validate_provider(provider)
    s = Search(index=index)
    s = _paginate_search(s, page_size, page)
    s = s.params(preference=str(ip))
    provider_filter = Q('term', provider=provider.lower())
    s = s.filter('bool', should=provider_filter, minimum_should_match=1)
    licenses = lt if lt else li
    s = _filter_licenses(s, licenses)
    if filter_rot:
        s = _exclude_dead(s, page, page_size)
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
        try:
            results = s.execute().aggregations['unique_providers']['buckets']
        except NotFoundError:
            results = [{'key': 'none_found', 'doc_count': 0}]
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
