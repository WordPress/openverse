"""
This module has a number of public methods which are useful for working
with licenses.
"""
import logging
from collections import namedtuple
from functools import cache, lru_cache
from typing import Optional, Tuple
from urllib.parse import urlparse

from common import urls
from common.licenses import constants


logger = logging.getLogger(__name__)

LICENSE_PATH_MAP = constants.get_license_path_map()
REVERSE_LICENSE_PATH_MAP = constants.get_reverse_license_path_map()


class InvalidLicenseURLException(Exception):
    pass


LicenseInfo = namedtuple("LicenseInfo", ["license", "version", "url", "raw_url"])


@lru_cache(maxsize=1024)
def get_license_info(license_url=None, license_=None, license_version=None):
    """
    Returns a valid license, version, license URL tuple if possible.

    Three optional arguments:
    license_url:      String URL to a CC license page.
    license_:         String representing a CC license.
    license_version:  string version of a CC license.  (Casts floats)

    While all three arguments are optional, either a license_url must be
    given, or a valid license_, license_version pair must be given.

    The license URL, if given, will be validated. This function will
    attempt to repair malformed or incorrect license URLs when enough
    information is available.

    If the license URL is not given, or invalid and irreparable, we try
    to construct a license URL from the given license_, license_version
    pair.

    If we're able to derive a valid license URL, we return the namedtuple

        LicenseInfo(license, version, url, raw_url)

    with the validated and corrected values of license, version, url.

    Otherwise, we return

      LicenseInfo(None, None, None, None)
    """
    license_info = _get_license_info_from_url(license_url)
    if license_info[0] is not None:
        logger.debug(
            f"Found derived license {license_info[0]},"
            f" derived version {license_info[1]},"
            f" and license_url {license_info[2]}"
        )
    elif license_ is not None:
        logger.debug(
            f"Falling back to given license_ {license_}"
            f" and license_version {license_version}"
        )
        license_info = get_license_info_from_license_pair(license_, license_version)
        license_info = (*license_info, license_url)
    else:
        logger.debug(
            f"No valid license_info could be derived.  Inputs were"
            f" license_: {license_}"
            f" license_version: {license_version}"
            f" license_url: {license_url}"
        )
        license_info = None, None, None, None
    if len(license_info) == 3:
        license_info = (*license_info, None)
    return LicenseInfo(*license_info)


def _get_license_info_from_url(
    license_url: str, path_map=LICENSE_PATH_MAP
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    We try to extract license info from a given URL.

    Required Arguments:

    license_url:  string from which we'll try to extract license info

    Optional Argument:

    path_map:  dict with keys being string URL paths defining license
               pairs and values being a tuple (str, str) with the pair
               defined by the URL path.  See common.licenses.constants
               for examples.  The default should be all canonical
               license path stems.

    We first validate that the URL is a valid creativecommons.org URL,
    then use the paths from the path_map to determine the
    (license_, license_version) pair corresponding to the URL.

    We return the validated license info if possible,
    else None, None, None, None.
    """
    raw_url = license_url
    cc_url = _get_valid_cc_url(license_url)
    if cc_url is None:
        return None, None, None, None

    license_, license_version = None, None
    for valid_path in path_map:
        if valid_path in cc_url:
            license_, license_version = path_map[valid_path]
            logger.debug(
                f"Derived license_: {license_},"
                f" Derived license_version: {license_version}"
            )
            break

    if license_ is None:
        logger.warning(
            f"{license_url} could not be split into a valid license pair."
            f"\npath_map: {path_map}"
        )
        cc_url = None
        raw_url = None
    return license_, license_version, cc_url, raw_url


def _get_valid_cc_url(license_url) -> Optional[str]:
    """
    Try to get a valid creativecommons.org URL from a given URL.

    Required Argument:

    license_url:  string with a URL to be validated or fixed

    This function enforces:
      - string type
      - https scheme
      - parses into a urllib.parse.ParseResult with
        netloc=creativecommons.org

    After that, we rewrite the URL to whatever we get redirected to when
    we make a request using it.

    If all of these validations and the rewriting succeed, we return the
    rewritten URL. Otherwise, we return None
    """
    logger.debug(f"Checking license URL {license_url}")
    if type(license_url) != str:
        logger.debug(f"License URL is not a string. Type is {type(license_url)}")
        return

    https_url = urls.add_url_scheme(license_url.lower(), "https")
    parsed_url = urlparse(https_url)

    if parsed_url.netloc != "creativecommons.org":
        logger.info(f"The license at {license_url} is not issued by Creative Commons.")
        return

    rewritten_url = urls.rewrite_redirected_url(https_url)

    if rewritten_url is not None and (
        "licenses" in rewritten_url or "publicdomain" in rewritten_url
    ):
        validated_license_url = rewritten_url
        logger.debug(f"Rewritten URL {rewritten_url} is valid")
    else:
        logger.debug(f"Rewritten URL {rewritten_url} is invalid")
        validated_license_url = None

    return validated_license_url


def get_license_info_from_license_pair(
    license_, license_version, pair_map=REVERSE_LICENSE_PATH_MAP
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Validates a given license pair, and derives a license URL from it.

    Returns both the validated pair and the derived license URL.
    """
    string_version = _ensure_license_version_string(license_version)
    license_path = pair_map.get((license_, string_version))
    logger.debug(f"Derived license_path: {license_path}")

    if license_path is not None:
        valid_url = _build_license_url(license_path)
        valid_license, valid_version = license_, string_version
    else:
        valid_license, valid_version, valid_url = None, None, None

    return valid_license, valid_version, valid_url


def _ensure_license_version_string(license_version) -> Optional[str]:
    string_license_version = None
    try:
        if license_version == constants.NO_VERSION:
            string_license_version = license_version
        elif license_version is not None:
            string_license_version = str(float(license_version))
        else:
            logger.debug("license_version is NoneType")
    except (TypeError, ValueError) as e:
        logger.warning(
            f"Could not recover license_version from {license_version}!"
            f" Error was {e}"
        )
    return string_license_version


def _build_license_url(license_path) -> str:
    license_path = license_path.strip().strip("/")
    derived_url = f"https://creativecommons.org/{license_path}/"
    rewritten_license_url = urls.rewrite_redirected_url(derived_url)
    if rewritten_license_url is None:
        raise InvalidLicenseURLException(f"Failed to rewrite URL: {derived_url}")
    return rewritten_license_url


@cache
def is_valid_license_info(license_info: LicenseInfo) -> bool:
    base_path = "https://creativecommons.org/"
    try:
        license_path = license_info.url.replace(base_path, "")
        if license_path[-1] == "/":
            license_path = license_path[:-1]
        license_pair = LICENSE_PATH_MAP.get(license_path)
        return license_pair is not None
    except AttributeError:
        return False
