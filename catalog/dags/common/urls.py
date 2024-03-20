"""
This module has a number of public methods which are useful for
verifying and cleaning URLs.
"""

import logging
import re
from functools import lru_cache
from urllib.parse import urlparse

import tldextract

# This import is aliased for easier test mocking
from requests import get as requests_get
from requests.exceptions import RequestException


logger = logging.getLogger(__name__)


class SpaceInUrlError(Exception):
    pass


def validate_url_string(url_string, strip_slash: bool = True):
    """
    Determine whether the given `url_string` is a valid URL with an https scheme.

    If not, attempts to mangle the URL scheme into the desired form,
    falling back to an http scheme in the event TLS is not supported.

    If all attempts to save the input string fail, returns None

    Required Arguments:
    url_string:  URL (string) which will be validated and/or repaired.

    Optional Arguments:
    strip_slash: Flag (bool) decides whether to strip slashes in URL or not,
    Default value is `True`
    """

    logger.debug(f"Validating_url {url_string}")
    if not isinstance(url_string, str) or not url_string:
        return

    if url_string and " " in url_string:
        raise SpaceInUrlError(f"space is present in URL: {url_string}")

    upgraded_url = _add_best_scheme(url_string, strip_slash)

    parse_result = urlparse(upgraded_url)
    tld = tldextract.extract(upgraded_url)

    logger.debug(f"parse_result.scheme: {parse_result.scheme}")
    logger.debug(f"tld.domain: {tld.domain}")
    logger.debug(f"tld.suffix: {tld.suffix}")

    if tld.domain and tld.suffix and parse_result.scheme:
        return upgraded_url
    elif tld.ipv4 and parse_result.scheme:
        logger.debug(f"Using IP address as URL: {upgraded_url}")
        return upgraded_url
    else:
        logger.info(
            f"Invalid url {url_string}, attempted upgrade: {upgraded_url}"
            " Returning None"
        )
        return None


@lru_cache(maxsize=2048)
def rewrite_redirected_url(url_string):
    """
    Request the given url and rewrite it to the final URL after any redirects.

    Caches the result to avoid repetitive network requests.
    """
    try:
        response = requests_get(url_string)
        if response.ok:
            rewritten_url = response.url
            if rewritten_url != url_string:
                logger.info(f"{url_string} was rewritten to {rewritten_url}")
        else:
            logger.warning(
                f"URL {url_string} could not be rewritten."
                f" Response Code: {response.status_code}"
            )
            rewritten_url = None
    except RequestException as e:
        logger.warning(f"URL {url_string} could not be rewritten. Error: {e}")
        rewritten_url = None
    return rewritten_url


def add_url_scheme(url_string, scheme="http", strip_slash: bool = True):
    """
    Replace the scheme of `url_string` with `scheme` or adds the `scheme` if necessary.

    Only strip the leading/trailing slash of url if flag is True.
    """
    logger.debug(f"Adding or changing scheme of {url_string} to {scheme}")
    stripped_url = url_string.strip()
    scheme_pattern = re.compile("https*:/*")
    scheme_match = scheme_pattern.match(stripped_url)
    if scheme_match is not None:
        url_no_scheme = stripped_url[scheme_match.end() :]
    else:
        url_no_scheme = stripped_url

    url_no_scheme = url_no_scheme.strip("/") if strip_slash else url_no_scheme

    url_with_scheme = f"{scheme}://{url_no_scheme}"
    logger.debug(f"URL with scheme: {url_with_scheme}")
    return url_with_scheme


def _add_best_scheme(url_string, strip_slash: bool = True):
    domain_key = tldextract.extract(url_string).fqdn
    if not domain_key:
        domain_key = tldextract.extract(url_string).ipv4

    if _test_domain_for_tls_support(domain_key):
        upgraded_url = add_url_scheme(
            url_string, scheme="https", strip_slash=strip_slash
        )
    else:
        upgraded_url = add_url_scheme(
            url_string, scheme="http", strip_slash=strip_slash
        )

    return upgraded_url


@lru_cache(maxsize=1024)
def _test_domain_for_tls_support(domain):
    logger.info(f"Testing {domain} for TLS support")
    tls_supported = False
    try:
        requests_get(f"https://{domain}", timeout=2)
        logger.info(f"{domain} supports TLS.")
        tls_supported = True
    except RequestException as e:
        logger.info(f"Could not verify TLS support for {domain}. Error was\n{e}")
    return tls_supported
