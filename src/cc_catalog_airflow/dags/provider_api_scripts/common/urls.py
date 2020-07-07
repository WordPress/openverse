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
    logger.debug(f'Validating_url {url_string}')
    if not type(url_string) == str or not url_string:
        return
    else:
        upgraded_url = _add_best_scheme(url_string)

    parse_result = urlparse(upgraded_url)
    tld = tldextract.extract(upgraded_url)

    logger.debug(f'parse_result.scheme: {parse_result.scheme}')
    logger.debug(f'tld.domain: {tld.domain}')
    logger.debug(f'tld.suffix: {tld.suffix}')

    if tld.domain and tld.suffix and parse_result.scheme:
        return upgraded_url
    elif tld.ipv4 and parse_result.scheme:
        logger.debug(f'Using IP address as URL: {upgraded_url}')
        return upgraded_url
    else:
        logger.debug(
            f'Invalid url {url_string}, attempted upgrade: {upgraded_url}.'
            ' Returning None'
        )
        return None


@lru_cache(maxsize=1024)
def rewrite_redirected_url(url_string):
    try:
        response = requests.get(url_string)
        rewritten_url = response.url
        logger.info(f'{url_string} was rewritten to {rewritten_url}')
    except Exception as e:
        logger.warning(f'URL {url_string} could not be rewritten. Error: {e}')
        rewritten_url = None
    return rewritten_url


def add_url_scheme(url_string, scheme='http'):
    url_no_scheme = (
        url_string
        .strip()
        .strip('http://')
        .strip('https://')
        .strip('/')
    )
    return f'{scheme}://{url_no_scheme}'


def _add_best_scheme(url_string):
    domain_key = tldextract.extract(url_string).fqdn
    if not domain_key:
        domain_key = tldextract.extract(url_string).ipv4

    if _test_domain_for_tls_support(domain_key):
        upgraded_url = add_url_scheme(url_string, scheme='https')
    else:
        upgraded_url = add_url_scheme(url_string, scheme='http')

    return upgraded_url


@lru_cache(maxsize=1024)
def _test_domain_for_tls_support(domain):
    logger.info(f'Testing {domain} for TLS support')
    tls_supported = False
    try:
        requests.get(f'https://{domain}', timeout=2)
        logger.info(f'{domain} supports TLS.')
        tls_supported = True
    except Exception as e:
        logger.info(
            f'Could not verify TLS support for {domain}. Error was\n{e}'
        )
    return tls_supported
