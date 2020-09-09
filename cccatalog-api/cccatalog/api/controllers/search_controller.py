import cccatalog.api.models as models
import logging as log
import json
import pprint
from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.exceptions import NotFoundError, RequestError
from elasticsearch_dsl import Q, Search, connections
from elasticsearch_dsl.response import Response, Hit
from elasticsearch_dsl.query import Query
from cccatalog import settings
from django.core.cache import cache
from rest_framework import serializers
from cccatalog.api.utils.validate_images import validate_images
from cccatalog.api.utils.dead_link_mask import get_query_mask, get_query_hash
from itertools import accumulate
from typing import Tuple, List, Optional
from math import ceil

ELASTICSEARCH_MAX_RESULT_WINDOW = 10000
SOURCE_CACHE_TIMEOUT = 60 * 20
FILTER_CACHE_TIMEOUT = 30
DEAD_LINK_RATIO = 1 / 2
THUMBNAIL = 'thumbnail'
URL = 'url'
PROVIDER = 'provider'
DEEP_PAGINATION_ERROR = 'Deep pagination is not allowed.'
QUERY_SPECIAL_CHARACTER_ERROR = 'Unescaped special characters are not allowed.'


class RankFeature(Query):
    name = 'rank_feature'


def _paginate_with_dead_link_mask(s: Search, page_size: int,
                                  page: int) -> Tuple[int, int]:
    """
    Given a query, a page and page_size, return the start and end
    of the slice of results.

    :param s: The elasticsearch Search object
    :param page_size: How big the page should be.
    :param page: The page number.
    :return: Tuple of start and end.
    """
    query_hash = get_query_hash(s)
    query_mask = get_query_mask(query_hash)
    if not query_mask:
        start = 0
        end = ceil(page_size * page / (1 - DEAD_LINK_RATIO))
    elif page_size * (page - 1) > sum(query_mask):
        start = len(query_mask)
        end = ceil(page_size * page / (1 - DEAD_LINK_RATIO))
    else:
        accu_query_mask = list(accumulate(query_mask))
        start = 0
        if page > 1:
            try:
                start = accu_query_mask.index(page_size * (page - 1) + 1)
            except ValueError:
                start = accu_query_mask.index(page_size * (page - 1)) + 1
        if page_size * page > sum(query_mask):
            end = ceil(page_size * page / (1 - DEAD_LINK_RATIO))
        else:
            end = accu_query_mask.index(page_size * page) + 1
    return start, end


def _get_query_slice(s: Search, page_size: int, page: int,
                     filter_dead: Optional[bool] = False) -> Tuple[int, int]:
    """
    Select the start and end of the search results for this query.
    """
    if filter_dead:
        start_slice, end_slice = \
            _paginate_with_dead_link_mask(s, page_size, page)
    else:
        # Paginate search query.
        start_slice = page_size * (page - 1)
        end_slice = page_size * page
    if start_slice + end_slice > ELASTICSEARCH_MAX_RESULT_WINDOW:
        raise ValueError(DEEP_PAGINATION_ERROR)
    return start_slice, end_slice


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


def _post_process_results(s, start, end, page_size, search_results,
                          request, filter_dead) -> List[Hit]:
    """
    After fetching the search results from the back end, iterate through the
    results, perform image validation, and route certain thumbnails through our
    proxy.

    :param s: The Elasticsearch Search object.
    :param start: The start of the result slice.
    :param end: The end of the result slice.
    :param search_results: The Elasticsearch response object containing search
    results.
    :param request: The Django request object, used to build a "reversed" URL
    to detail pages.
    :param filter_dead: Whether images should be validated.
    :return: List of results.
    """
    results = []
    to_validate = []
    for res in search_results:
        if hasattr(res.meta, 'highlight'):
            res.fields_matched = dir(res.meta.highlight)
        to_validate.append(res.url)
        results.append(res)

    if filter_dead:
        query_hash = get_query_hash(s)
        validate_images(query_hash, start, results, to_validate)

        if len(results) < page_size:
            end += int(end / 2)
            if start + end > ELASTICSEARCH_MAX_RESULT_WINDOW:
                return results

            s = s[start:end]
            search_response = s.execute()

            return _post_process_results(
                s,
                start,
                end,
                page_size,
                search_response,
                request,
                filter_dead
            )
    return results[:page_size]


def _apply_filter(s: Search, search_params, param_name, renamed_param=None):
    """
    Parse and apply a filter from the search parameters serializer. The
    parameter key is assumed to have the same name as the corresponding
    Elasticsearch property. Each parameter value is assumed to be a comma
    separated list encoded as a string.

    :param s: The Search object to apply the filter to.
    :param search_params: A serializer containing user input.
    :param param_name: The name of the parameter in search_params.
    :param renamed_param: In some cases, the param name in the backend is not
    the same as the param we want to expose to the outside world. Use this to
    set the corresponding parameter name in Elasticsearch.
    :return: A Search object with the filter applied.
    """
    if param_name in search_params.data:
        filters = []
        for arg in search_params.data[param_name].split(','):
            _param = renamed_param if renamed_param else param_name
            args = {
                'name_or_query': 'term',
                _param: arg
            }
            filters.append(Q(**args))
        return s.filter('bool', should=filters)
    else:
        return s


def _exclude_filtered(s: Search):
    """
    Hide data sources from the catalog dynamically.
    """
    filter_cache_key = 'filtered_providers'
    filtered_providers = cache.get(key=filter_cache_key)
    if not filtered_providers:
        filtered_providers = models.ContentProvider.objects\
            .filter(filter_content=True)\
            .values('provider_identifier')
        cache.set(
            key=filter_cache_key,
            timeout=FILTER_CACHE_TIMEOUT,
            value=filtered_providers
        )
    to_exclude = [f['provider_identifier'] for f in filtered_providers]
    s = s.exclude('terms', provider=to_exclude)
    return s


def _exclude_mature_by_param(s: Search, search_params):
    if not search_params.data['mature']:
        s = s.exclude('term', mature=True)
    return s


def search(search_params, index, page_size, ip, request,
           filter_dead, page=1) -> Tuple[List[Hit], int, int]:
    """
    Given a set of keywords and an optional set of filters, perform a ranked
    paginated search.

    :param search_params: Search parameters. See
     :class: `ImageSearchQueryStringSerializer`.
    :param index: The Elasticsearch index to search (e.g. 'image')
    :param page_size: The number of results to return per page.
    :param ip: The user's hashed IP. Hashed IPs are used to anonymously but
    uniquely identify users exclusively for ensuring query consistency across
    Elasticsearch shards.
    :param request: Django's request object.
    :param filter_dead: Whether dead links should be removed.
    :param page: The results page number.
    :return: Tuple with a List of Hits from elasticsearch, the total count of
    pages, and number of results.
    """
    s = Search(index=index)
    # Apply term filters. Each tuple pairs a filter's parameter name in the API
    # with its corresponding field in Elasticsearch. "None" means that the
    # names are identical.
    filters = [
        ('extension', None),
        ('categories', None),
        ('aspect_ratio', None),
        ('size', None),
        ('source', None),
        ('license', 'license__keyword'),
        ('license_type', 'license__keyword')
    ]
    for tup in filters:
        api_field, elasticsearch_field = tup
        s = _apply_filter(s, search_params, api_field, elasticsearch_field)

    # Exclude mature content and disabled sources
    s = _exclude_mature_by_param(s, search_params)
    s = _exclude_filtered(s)

    # Search either by generic multimatch or by "advanced search" with
    # individual field-level queries specified.
    search_fields = ['tags.name', 'title', 'description']
    if 'q' in search_params.data:
        query = _quote_escape(search_params.data['q'])
        s = s.query(
            'simple_query_string',
            query=query,
            fields=search_fields,
            default_operator='AND'
        )
        # Boost exact matches
        quotes_stripped = query.replace('"', '')
        exact_match_boost = Q(
            'simple_query_string',
            fields=['title'],
            query=f"\"{quotes_stripped}\"",
            boost=10000
        )
        s = Search().query(
            Q(
                'bool',
                must=s.query,
                should=exact_match_boost
            )
        )
    else:
        if 'creator' in search_params.data:
            creator = _quote_escape(search_params.data['creator'])
            s = s.query(
                'simple_query_string', query=creator, fields=['creator']
            )
        if 'title' in search_params.data:
            title = _quote_escape(search_params.data['title'])
            s = s.query(
                'simple_query_string', query=title, fields=['title']
            )
        if 'tags' in search_params.data:
            tags = _quote_escape(search_params.data['tags'])
            s = s.query(
                'simple_query_string',
                fields=['tags.name'],
                query=tags
            )

    if settings.USE_RANK_FEATURES:
        feature_boost = {
            'standardized_popularity': 10000
        }
        rank_queries = []
        for field, boost in feature_boost.items():
            rank_queries.append(Q('rank_feature', field=field, boost=boost))
        s = Search().query(
            Q(
                'bool',
                must=s.query,
                should=rank_queries
            )
        )

    # Use highlighting to determine which fields contribute to the selection of
    # top results.
    s = s.highlight(*search_fields)
    s = s.highlight_options(order='score')
    s.extra(track_scores=True)
    # Route users to the same Elasticsearch worker node to reduce
    # pagination inconsistencies and increase cache hits.
    s = s.params(preference=str(ip), request_timeout=7)
    # Paginate
    start, end = _get_query_slice(s, page_size, page, filter_dead)
    s = s[start:end]
    try:
        if settings.VERBOSE_ES_RESPONSE:
            log.info(pprint.pprint(s.to_dict()))
        search_response = s.execute()
        log.info(f'query={json.dumps(s.to_dict())},'
                 f' es_took_ms={search_response.took}')
        if settings.VERBOSE_ES_RESPONSE:
            log.info(pprint.pprint(search_response.to_dict()))
    except RequestError as e:
        raise ValueError(e)
    results = _post_process_results(
        s,
        start,
        end,
        page_size,
        search_response,
        request,
        filter_dead
    )

    result_count, page_count = _get_result_and_page_count(
        search_response,
        results,
        page_size
    )
    return results, page_count, result_count


def related_images(uuid, index, request, filter_dead):
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
    # Never show mature content in recommendations.
    s = s.exclude('term', mature=True)
    s = _exclude_filtered(s)
    page_size = 10
    page = 1
    start, end = _get_query_slice(s, page_size, page, filter_dead)
    s = s[start:end]
    response = s.execute()
    results = _post_process_results(
        s,
        start,
        end,
        page_size,
        response,
        request,
        filter_dead
    )

    result_count, _ = _get_result_and_page_count(
        response,
        results,
        page_size
    )

    return results, result_count


def get_sources(index):
    """
    Given an index, find all available data sources and return their counts.

    :param index: An Elasticsearch index, such as `'image'`.
    :return: A dictionary mapping sources to the count of their images.`
    """
    source_cache_name = 'sources-' + index
    cache_fetch_failed = False
    try:
        sources = cache.get(key=source_cache_name)
    except ValueError:
        cache_fetch_failed = True
        sources = None
        log.warning('Source cache fetch failed due to corruption')
    if type(sources) == list or cache_fetch_failed:
        # Invalidate old provider format.
        cache.delete(key=source_cache_name)
    if not sources:
        # Don't increase `size` without reading this issue first:
        # https://github.com/elastic/elasticsearch/issues/18838
        size = 100
        agg_body = {
            'aggs': {
                'unique_sources': {
                    'terms': {
                        'field': 'source.keyword',
                        'size': size,
                        "order": {
                            "_key": "desc"
                        }
                    }
                }
            }
        }
        try:
            results = es.search(index=index, body=agg_body, request_cache=True)
            buckets = results['aggregations']['unique_sources']['buckets']
        except NotFoundError:
            buckets = [{'key': 'none_found', 'doc_count': 0}]
        sources = {result['key']: result['doc_count'] for result in buckets}
        cache.set(
            key=source_cache_name,
            timeout=SOURCE_CACHE_TIMEOUT,
            value=sources
        )
    return sources


def _elasticsearch_connect():
    """
    Connect to configured Elasticsearch domain.

    :return: An Elasticsearch connection object.
    """
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
        max_retries=1,
        retry_on_timeout=True,
        http_auth=auth,
        wait_for_status='yellow'
    )
    _es.info()
    return _es


es = _elasticsearch_connect()
connections.connections.add_connection('default', es)


def _get_result_and_page_count(response_obj: Response, results: List[Hit],
                               page_size: int) -> Tuple[int, int]:
    """
    Elasticsearch does not allow deep pagination of ranked queries.
    Adjust returned page count to reflect this.

    :param response_obj: The original Elasticsearch response object.
    :param results: The list of filtered result Hits.
    :return: Result and page count.
    """
    result_count = response_obj.hits.total.value
    natural_page_count = int(result_count / page_size)
    last_allowed_page = int((5000 + page_size / 2) / page_size)
    page_count = min(natural_page_count, last_allowed_page)
    if len(results) < page_size and page_count == 0:
        result_count = len(results)

    return result_count, page_count
