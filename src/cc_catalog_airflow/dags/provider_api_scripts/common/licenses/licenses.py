
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


class InvalidLicenseURLException(Exception):
    pass


def get_license_info(
        license_url=None, license_=None, license_version=None
):
    """
    Returns a valid license, version, license URL tuple if possible.
    Prefers returning a tuple derived from an input license URL. If no
    such pair can be found, returns None, None.

    Three optional arguments:
    license_url:      String URL to a CC license page.
    license_:         String representing a CC license.
    license_version:  string URL to a CC license page.  (Will cast floats)
    """
    valid_url = _get_valid_cc_license_url(license_url)
    logger.debug('Valid URL: {valid_url}')

    if valid_url is not None:
        chosen_license, chosen_version = _derive_license_from_url(valid_url)
        logger.debug(
            'Using derived_license {} and derived_version {}'
            .format(chosen_license, chosen_version)
        )
    else:
        logger.debug(
            f'Using given license_ {license_}'
            f' and license_version {license_version}'
        )
        chosen_license, chosen_version = license_, license_version

    valid_license, valid_version = _validate_license_pair(
        chosen_license, chosen_version
    )

    return valid_license, valid_version, valid_url


def _get_valid_cc_license_url(license_url):
    logger.debug(f'Checking license URL {license_url}')
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


def _derive_license_from_url(license_url,  path_map=LICENSE_PATH_MAP):
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

    if not (license_ and license_url):
        # Ending up here indicates either a bug in our CC License URL repairing
        # and validating logic, or a missing valid license path in path_map.
        raise InvalidLicenseURLException(
            f'{license_url} could not be split into a valid license pair.'
            f'\npath_map: {path_map}'
        )

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
