from aws_requests_auth.aws_auth import AWSRequestsAuth
from cccatalog.api.licenses import LICENSE_GROUPS
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.exceptions import AuthenticationException, \
    AuthorizationException
from elasticsearch_dsl import Q, Search, connections
from cccatalog import settings
import logging as log
import pdb


def search(search_params, index):
    """
    Given a set of keywords and an optional set of filters, perform a search.

    :param search_params: Search parameters. See
     :func: `~cccatalog.api.search_controller.parse_search_query` for the
     assumed format.
    :param index: The Elasticsearch index to search (e.g. 'image')
    :return: A paginated list of results.
    """

    # Build the Elasticsearch query.
    s = Search(index=index)

    if 'filters' in search_params:
        filters = search_params['filters']
        if 'licenses' in filters:
            licenses = [_license.lower() for _license in filters['licenses']]
            license_queries = []
            for _license in licenses:
                license_queries.append(Q("term", license=_license))
            s = s.filter('bool', should=license_queries, minimum_should_match=1)

    keywords = ' '.join(search_params['keywords'])
    s = s.query("multi_match",
                query=keywords,
                fields=['title', 'tag', 'creator'])

    s.extra(track_scores=True)
    search_response = s.execute()
    print('Hits:', search_response.hits.total)


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
                licenses: ["CC0", "CC-BY"]
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
            errors.append('License \'{}\' does not exist.'.format(_license))
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
        es = Elasticsearch(
            host=settings.ELASTICSEARCH_URL,
            port=settings.ELASTICSEARCH_PORT,
            connection_class=RequestsHttpConnection,
            timeout=10,
            max_retries=10,
            wait_for_status='yellow'
        )
        log.info(str(es.info()))
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
        es = Elasticsearch(
            host=settings.ELASTICSEARCH_URL,
            port=settings.ELASTICSEARCH_PORT,
            connection_class=RequestsHttpConnection,
            timeout=10,
            max_retries=10,
            retry_on_timeout=True,
            http_auth=auth,
            wait_for_status='yellow'
        )
        es.info()
    return es


es = _elasticsearch_connect()
connections.connections.add_connection('default', es)
