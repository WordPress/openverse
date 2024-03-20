"""
This module highly mirrors the JavaScript code present in the frontend repository.

For any changes made here, please make the corresponding changes in the
frontend, or open an issue to track it.
"""

from api.constants.licenses import (
    ALL_CC_LICENSES,
    DEPRECATED_CC_LICENSES,
    PUBLIC_DOMAIN_MARKS,
)


def get_license_url(_license: str, license_version: str | None) -> str:
    """
    Get the URL to the deed of the license.

    :param _license: the slug of the license
    :param license_version: the version number of the license
    :return: the URL to the license deed
    """

    if _license == "cc0":
        fragment = "publicdomain/zero/1.0"
    elif _license == "pdm":
        fragment = "publicdomain/mark/1.0/"
    elif is_deprecated(_license):
        fragment = f"licenses/{_license}/1.0"
    else:
        fragment = f"licenses/{_license}/{license_version or '4.0'}"
    return f"https://creativecommons.org/{fragment}/"


def get_full_license_name(_license: str, license_version: str | None) -> str:
    """
    Get the readable full name of the license from the license slug and version.

    :param _license: the slug of the license
    :param license_version: the version number of the license
    :return: the full name of the license
    """

    license_name: str
    if _license == "pdm":
        license_name = "Public Domain Mark"
    else:
        license_name = _license.upper().replace("SAMPLING", "Sampling")
    if license_version:
        license_name = f"{license_name} {license_version}"
    if not is_public_domain(_license):
        license_name = f"CC {license_name}"
    return license_name.strip()


def is_public_domain(_license: str) -> bool:
    """
    Check if the given name belongs to a public-domain mark and is not a license.

    CC licenses have different legal status from the public domain marks
    such as CC0 and PDM, and need different wording.

    :param _license: the license slug to check
    :return: ``True`` if the license is a public domain mark, ``False`` otherwise
    """

    return _license in PUBLIC_DOMAIN_MARKS


def is_cc(_license: str) -> bool:
    """
    Check if the given name belongs to a CC license, active or deprecated.

    This includes CC0, which although not technically a license, is offered by CC.

    :param _license: the license slug to check
    :return: ``True`` if the license is a CC license, ``False`` otherwise
    """

    return _license in ALL_CC_LICENSES


def is_deprecated(_license: str) -> bool:
    """
    Check if the given name belongs to a deprecated CC license.

    The full list of deprecated licenses can be found on the
    [Retired Legal Tools page](https://creativecommons.org/retiredlicenses/) on
    the CC.org site.

    :param _license: the license slug to check
    :return: ``True`` if the license is a deprecated CC license, ``False`` otherwise
    """

    return _license in DEPRECATED_CC_LICENSES
