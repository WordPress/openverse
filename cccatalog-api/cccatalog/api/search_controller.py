from aws_requests_auth.aws_auth import AWSRequestsAuth
from cccatalog.api.licenses import LICENSE_GROUPS
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.exceptions import AuthenticationException, \
    AuthorizationException
from elasticsearch_dsl import Q, Search, connections
from elasticsearch_dsl.response import Response
from cccatalog import settings
import logging as log


def search(search_params, index, page_size, page=1) -> Response:
    """
    Given a set of keywords and an optional set of filters, perform a search.
    Only up to 10,000 results will be returned.

    :param search_params: Search parameters. See
     :func: `~cccatalog.api.search_controller.parse_search_query` for the
     assumed format.
    :param index: The Elasticsearch index to search (e.g. 'image')
    :param page_size: The number of results to return per page.
    :param page: The results page number.
    :return: An Elasticsearch Response object.
    """
    s = Search(index=index)

    # Paginate search query.
    start_slice = page_size * (page - 1)
    end_slice = page_size * page
    s = s[start_slice:end_slice]

    # If any filters are specified, add them to the query.
    if 'filters' in search_params:
        filters = search_params['filters']
        if 'licenses' in filters:
            licenses = [_license.lower() for _license in filters['licenses']]
            license_queries = []
            for _license in licenses:
                license_queries.append(Q("term", license=_license))
            s = s.filter('bool', should=license_queries, minimum_should_match=1)

    # Search by keyword.
    keywords = ' '.join(search_params['keywords'])
    s = s.query("multi_match",
                query=keywords,
                fields=['title', 'tag', 'creator'])

    s.extra(track_scores=True)
    search_response = s.execute()
    return search_response


def parse_search_query(query_params):
    """
    Parse and validate a query for a search.

    :param query_params: A Django Rest Framework request.query_params object.

    :return: The response includes a dictionary of the parsed query and a list
    of any errors that occurred.

    The query dictionary specifying keywords and, optionally,
    a set of filters to apply to the search. Example:

        result = {
            "keywords": ["cat", "running"]
        }

    Another valid example:
        result = {
            "keywords": ["test", "search"],
            "filters": {
                licenses: ["CC0", "BY"]
            }
        }

    If any errors occurred, the caller should reject the query.
    """
    # TODO: Parsing and validation of query strings should be cleanly separated
    # from validation of licensing requirements.
    # FIXME
    field_length_limit = 100
    errors = []

    raw_keywords = query_params.get('q')
    raw_license_type = query_params.get('lt')
    raw_licenses = query_params.get('li')

    keywords = None
    if not raw_keywords:
        errors.append('No keywords specified.')
    else:
        keywords = raw_keywords.split(',')

    licenses = set()
    if raw_license_type and raw_licenses:
        errors.append('Only license type (e.g. \'commercial\' or license '
                      '(\'CC-BY\') can be defined, not both.')
    if raw_license_type:
        try:
            license_types = [x.lower() for x in raw_license_type.split(',')]
            for _type in license_types:
                group = LICENSE_GROUPS[_type]
                for _license in group:
                    licenses.add(_license)
        except KeyError:
            errors.append('License type does not exist. Valid options: '
                          + str(list(LICENSE_GROUPS.keys())))
    elif raw_licenses:
        licenses = [x.upper() for x in raw_licenses.split(',')]

    for _license in licenses:
        if _license not in LICENSE_GROUPS['all']:
            errors.append('License \'{}\' does not exist. Valid options: {}'
                          .format(_license, LICENSE_GROUPS['all']))
    result = {
        'keywords': keywords,
    }
    if len(licenses) > 0:
        result['filters'] = {}
        result['filters']['licenses'] = licenses

    return result, errors


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
            max_retries=10,
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
            max_retries=10,
            retry_on_timeout=True,
            http_auth=auth,
            wait_for_status='yellow'
        )
        _es.info()
    return _es


es = _elasticsearch_connect()
connections.connections.add_connection('default', es)
