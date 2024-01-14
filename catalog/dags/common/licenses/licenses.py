"""
This module has a number of public methods which are useful for working
with licenses.
"""
import logging
from functools import lru_cache
from typing import NamedTuple
from urllib.parse import urlparse

from common import urls
from common.licenses import constants


logger = logging.getLogger(__name__)

LICENSE_PATH_MAP = constants.get_license_path_map()
REVERSE_LICENSE_PATH_MAP = constants.get_reverse_license_path_map()
CC_BASE_URL = "https://creativecommons.org/"
LICENSE_URLS = {f"{CC_BASE_URL}{l}/" for l in LICENSE_PATH_MAP.keys()}  # noqa: E741


class InvalidLicenseURLException(Exception):
    pass


class LicenseInfo(NamedTuple):
    license: str
    version: str
    url: str
    raw_url: str | None = None


# SMK sometimes uses incorrect URL for licenses
special_cases = {
    "https://creativecommons.org/share-your-work/public-domain/cc0/": "https://creativecommons.org/publicdomain/zero/1.0/",
    "https://creativecommons.org/share-your-work/public-domain/pdm/": "https://creativecommons.org/publicdomain/mark/1.0/",
}


@lru_cache(maxsize=1024)
def get_license_info(
    license_url: str | None = None,
    license_: str | None = None,
    license_version: str | int | float | None = None,
) -> LicenseInfo | None:
    """
    Return a valid license, version, license URL tuple if possible.

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

    Otherwise, we return None.
    """
    license_info = _get_license_info_from_url(license_url)
    if license_info:
        logger.debug(
            f"Found derived license {license_info[0]},"
            f" derived version {license_info[1]},"
            f" and license_url {license_info[2]}"
        )
        return license_info
    if license_ is None:
        logger.debug(
            f"No valid license_info could be derived. Inputs were"
            f" license_: {license_}"
            f" license_version: {license_version}"
            f" license_url: {license_url}"
        )
        return None

    logger.debug(
        f"Trying to get the license using given license_ {license_}"
        f" and license_version {license_version}"
    )
    validated_license_info = get_license_info_from_license_pair(
        license_, license_version
    )
    if not validated_license_info:
        logger.debug(
            f"No valid license_info could be derived. Inputs were"
            f" license_: {license_}"
            f" license_version: {license_version}"
            f" license_url: {license_url}"
        )
        return None
    else:
        logger.debug(
            f"Falling back to given license_ {license_}"
            f" and license_version {license_version}"
        )
        return LicenseInfo(*validated_license_info, license_url)


def _get_license_info_from_url(
    license_url: str, path_map: dict[str, tuple[str, str]] | None = None
) -> LicenseInfo | None:
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

    We return the validated LicenseInfo if possible,
    else None.
    """
    path_map = path_map or LICENSE_PATH_MAP
    raw_url = license_url
    cc_url = _get_valid_cc_url(license_url)
    if cc_url is None:
        return None

    license_: str | None = None
    license_version: str | None = None
    for valid_path, (license_, license_version) in path_map.items():
        if valid_path in cc_url:
            logger.debug(
                f"Derived license_: {license_},"
                f" Derived license_version: {license_version}"
            )
            break

    if license_ is None or license_version is None:
        logger.warning(
            f"{license_url} could not be split into a valid license pair."
            f"\npath_map: {path_map}"
        )
        return None
    return LicenseInfo(license_, license_version, cc_url, raw_url)


def _get_valid_cc_url(license_url) -> str | None:
    """
    Try to get a valid creativecommons.org URL from a given URL.

    Required Argument:

    license_url:  string with a URL to be validated or fixed

    This function enforces:
      - string type
      - https scheme
      - trailing slash

    If the resulting URL is in the `LICENSE_URLS` set, we return it.
    Otherwise, we parse URL into a urllib.parse.ParseResult, ensuring
    that its netloc=creativecommons.org

    After that, we rewrite the URL to whatever we get redirected to when
    we make a request using it.

    If all of these validations and the rewriting succeed, we return the
    rewritten URL. Otherwise, we return None.
    """
    logger.debug(f"Checking license URL {license_url}")
    if not isinstance(license_url, str):
        logger.debug(f"License URL is not a string. Type is {type(license_url)}")
        return

    https_url = urls.add_url_scheme(license_url.lower(), "https")
    if not https_url.endswith("/"):
        https_url += "/"
    if https_url in LICENSE_URLS:
        return https_url

    parsed_url = urlparse(https_url)

    if parsed_url.netloc != "creativecommons.org":
        logger.info(f"The license at {license_url} is not issued by Creative Commons.")
        return None

    rewritten_url = urls.rewrite_redirected_url(https_url)

    if rewritten_url is not None and (
        "licenses" in rewritten_url or "publicdomain" in rewritten_url
    ):
        validated_license_url = rewritten_url
        logger.debug(f"Rewritten URL {rewritten_url} is valid")
    elif rewritten_url is not None and rewritten_url in special_cases:
        validated_license_url = special_cases[rewritten_url]
        logger.debug(
            f"Rewritten URL {validated_license_url} is valid, "
            f"and uses non-standard URL {rewritten_url}"
        )
    else:
        logger.debug(f"Rewritten URL {rewritten_url} is invalid")
        validated_license_url = None

    return validated_license_url


def get_license_info_from_license_pair(
    license_: str | None,
    license_version: str | int | float | None,
    pair_map: dict[tuple[str, str], str] = None,
) -> tuple[str, str, str] | None:
    """
    Validate a given license pair, and derive a license URL from it.

    Returns both the validated pair and the derived license URL.
    """
    pair_map = pair_map or REVERSE_LICENSE_PATH_MAP
    string_version = _ensure_license_version_is_valid(license_version)
    if string_version is None:
        return None
    license_path = pair_map.get((license_, string_version))
    logger.debug(f"Derived license_path: {license_path}")

    if license_path is None:
        return None

    valid_url = _build_license_url(license_path)
    valid_license, valid_version = license_, string_version

    return valid_license, valid_version, valid_url


def _ensure_license_version_is_valid(
    license_version: str | int | float | None,
) -> str | None:
    """
    Ensure that a given license version is valid, i.e. is a string of a
    float like "4.0" or "N/A" for "publicdomain".
    """
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


def _build_license_url(license_path: str) -> str:
    license_path = license_path.strip().strip("/")
    derived_url = f"https://creativecommons.org/{license_path}/"
    rewritten_license_url = urls.rewrite_redirected_url(derived_url)
    if rewritten_license_url is None:
        raise InvalidLicenseURLException(f"Failed to rewrite URL: {derived_url}")
    return rewritten_license_url
