"""
This module has a number of public methods which are useful for
verifying and cleaning URLs.
"""
from functools import lru_cache
import logging
import requests
from urllib.parse import urlparse

import tldextract

from common.licenses import constants

logger = logging.getLogger(__name__)

LICENSE_PATH_MAP = constants.LICENSE_PATH_MAP


def validate_url_string(url_string):
    """
    Checks given `url_string` can be parsed into a URL with scheme and
    domain

    If not, returns None
    """
    if not type(url_string) == str:
        return
    else:
        upgraded_url = add_best_scheme(url_string)

    parse_result = urlparse(upgraded_url)
    tld = tldextract.extract(upgraded_url)

    if tld.domain and tld.suffix and parse_result.scheme:
        return upgraded_url
    else:
        logger.debug(f'Invalid url {url_string}, upgraded to {upgraded_url}')
        return None


def add_best_scheme(url_string):
    fqdn = tldextract.extract(url_string).fqdn

    if _test_tls_for_fully_qualified_domain_name(fqdn):
        upgraded_url = add_url_scheme(url_string, scheme='https')
    else:
        upgraded_url = add_url_scheme(url_string, scheme='http')

    return upgraded_url


def add_url_scheme(url_string, scheme='http'):
    url_no_scheme = (
        url_string
        .strip()
        .strip('http://')
        .strip('https://')
        .strip('/')
    )
    return f'{scheme}://{url_no_scheme}'


@lru_cache(maxsize=1024)
def _test_tls_for_fully_qualified_domain_name(fqdn):
    logger.info(f'Testing {fqdn} for TLS support')
    tls_supported = False
    try:
        requests.get(f'https://{fqdn}', timeout=2)
        logger.info(f'{fqdn} supports TLS.')
        tls_supported = True
    except Exception as e:
        logger.info(f'Could not verify TLS support for {fqdn}. Error was\n{e}')
    return tls_supported


@lru_cache(maxsize=1024)
def _rewrite_url_string(url_string):
    try:
        response = requests.get(url_string)
        rewritten_url = response.url
        logger.info(f'{url_string} was rewritten to {rewritten_url}')
    except Exception as e:
        logger.warning(f'URL {url_string} could not be rewritten. Error: {e}')
        rewritten_url = None
    return rewritten_url
