
"""
This module has a number of public methods which are useful for working
with licenses.
"""
from functools import lru_cache
import logging
import requests
from urllib.parse import urlparse

from common import urls
from common.licenses import constants

logger = logging.getLogger(__name__)

LICENSE_PATH_MAP = constants.LICENSE_PATH_MAP


def get_license_info(
        license_url=None, license_=None, license_version=None
):
    """
    Returns a valid license pair, preferring one derived from license_url.

    If no such pair can be found, returns None, None.

    Three optional arguments:
    license_url:      String URL to a CC license page.
    license_:         String representing a CC license.
    license_version:  string URL to a CC license page.  (Will cast floats)
    """
    valid_url, derived_license, derived_version = _get_license_from_url(
        license_url
    )
    if derived_license and derived_version:
        # We prefer license and version derived from the license_url, when
        # possible, since we have more control over the string
        # (capitalization, etc.)
        logger.debug(
            'Using derived_license {} and derived_version {}'
            .format(derived_license, derived_version)
        )
        final_license, final_version = derived_license, derived_version
    else:
        logger.debug(
            'Using given license_ {} and license_version {}'
            .format(license_, license_version)
        )
        final_license, final_version = license_, license_version

    valid_license, valid_version = _validate_license_pair(
        final_license, final_version
    )

    return valid_license, valid_version, valid_url


def _get_license_from_url(license_url):
    validated_license_url = _get_valid_cc_license_url(license_url)
    if validated_license_url is not None:
        license_, license_version = _get_license_from_validated_url(
            validated_license_url
        )
    else:
        logger.debug(f'Could not validate license URL {license_url}')
        license_, license_version = None, None

    if license_ is None or license_version is None:
        validated_license_url = None

    return validated_license_url, license_, license_version


def _get_valid_cc_license_url(license_url):
    logger.debug(f'Validating license URL {license_url}')
    if type(license_url) != str:
        logger.debug(
            f'License URL is not a string. Type is {type(license_url)}'
        )
        return

    https_url = urls.add_url_scheme(license_url.lower(), 'https')
    parsed_url = urlparse(https_url)

    if parsed_url.netloc != 'creativecommons.org':
        logger.warning(
            'The license at {} is not issued by Creative Commons.'
            .format(license_url)
        )
        return

    rewritten_url = urls.rewrite_redirected_url(https_url)

    if (
            rewritten_url is not None
            and (
                'licenses' in rewritten_url
                or 'publicdomain' in rewritten_url
            )
    ):
        validated_license_url = rewritten_url
    else:
        validated_license_url = None

    return validated_license_url


def _get_license_from_validated_url(license_url, path_map=LICENSE_PATH_MAP):
    license_, license_version = None, None
    for valid_path in path_map:
        if valid_path in license_url:
            license_ = path_map[valid_path]['license']
            license_version = path_map[valid_path]['version']

            logger.debug(
                'Derived license_: {}, Derived license_version: {}'
                .format(license_, license_version)
            )
            break

    return license_, license_version


def _validate_license_pair(
        license_,
        license_version,
        path_map=LICENSE_PATH_MAP
):
    if license_ is None or license_version is None:
        return None, None
    pairs = [(item['license'], item['version']) for item in path_map.values()]
    try:
        license_version = str(float(license_version))
    except Exception as e:
        logger.warning(
            'Could not recover license_version from {}!\n{}'
            .format(license_version, e)
        )
        return None, None
    if (license_, license_version) not in pairs:
        logger.warning(
            '{}, {} is not a valid license, license_version pair!\n'
            'Valid pairs are:  {}'
            .format(license_, license_version, pairs)
        )
        license_, license_version = None, None
    return license_, license_version
