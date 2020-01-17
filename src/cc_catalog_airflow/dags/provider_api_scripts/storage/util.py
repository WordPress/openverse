"""
This module has a number of public methods which are useful for storage
operations.
"""
import logging
from urllib.parse import urlparse

from storage import constants

logger = logging.getLogger(__name__)

LICENSE_PATH_MAP = constants.LICENSE_PATH_MAP


def prepare_table_field_string(unknown_input, column):
    output_field = None

    if not unknown_input:
        logger.debug('Falsy input {}. Returning None.'.format(unknown_input))
    else:
        output_field = column.prepare_string(unknown_input)

    return output_field


def choose_license_and_version(
        license_url=None, license_=None, license_version=None
):
    derived_license, derived_version = _get_license_from_url(license_url)
    if derived_license and derived_version:
        # We prefer license and version derived from the license_url, when
        # possible, since we have more control over the string
        # (capitalization, etc.)
        logger.debug(
            'Using derived_license {} and derived_version {}'
            .format(derived_license, derived_version)
        )
        license_, license_version = derived_license, derived_version
    else:
        logger.debug(
            'Using given license_ {} and license_version {}'
            .format(license_, license_version)
        )

    return _validate_license_pair(license_, license_version)


def validate_url_string(url_string):
    parse_result = urlparse(url_string)
    if type(url_string) == str and parse_result.scheme and parse_result.netloc:
        return url_string
    else:
        logger.debug('No valid url found in {}'.format(url_string))
        return None


def get_provider_and_source(provider, source, default=None):
    if not provider:
        provider = default
    if not source:
        source = provider

    return provider, source


def enforce_all_arguments_truthy(**kwargs):
    all_truthy = True
    for arg in kwargs:
        if not kwargs[arg]:
            logging.warning('Missing {}'.format(arg))
            all_truthy = False
    return all_truthy


def _get_license_from_url(license_url, path_map=LICENSE_PATH_MAP):
    license_url = validate_url_string(license_url)
    if license_url:
        parsed_license_url = urlparse(license_url)
    else:
        return None, None

    license_, license_version = None, None
    if parsed_license_url.netloc != 'creativecommons.org':
        logger.warning(
            'The license at {} is not issued by Creative Commons.'
            .format(license_url)
        )
    else:
        for valid_path in path_map:
            if valid_path in parsed_license_url.path.lower():
                license_ = path_map[valid_path]['license']
                license_version = path_map[valid_path]['version']

                logger.debug(
                    'Derived license_: {}, Derived license_version: {}'
                    .format(license_, license_version)
                )

    return license_, license_version


def _validate_license_pair(
        license_,
        license_version,
        path_map=LICENSE_PATH_MAP
):
    pairs = ((item['license'], item['version']) for item in path_map.values())
    if (license_, license_version) not in pairs:
        logger.warning(
            '{}, {} is not a valid license, license_version pair'
            .format(license_, license_version)
        )
        license_, license_version = None, None
    return license_, license_version
