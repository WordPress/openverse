"""
This module highly mirrors the JavaScript code present in the frontend repository.
For any changes made here, please make the corresponding changes in the
frontend, or open an issue to track it.
"""

from catalog.api.utils.licenses import get_full_license_name, is_public_domain


def get_attribution_text(
    title: str | None,
    creator: str | None,
    _license: str,
    license_version: str | None,
    license_url: str | None,
) -> str:
    """
    Get the attribution text to properly and legally attribute a creative work to its
    creator. This text is only in plain-text English. Refer to the frontend for an
    internationalised implementation with rich-text and HTML variants.

    :param title: the title of the creative work
    :param creator: the name of the owner of the creative work
    :param _license: the license (or mark) associated with the creative work
    :param license_version: the version of the license
    :param license_url: the URL at which the complete license terms can be found
    :return: the full attribution text
    """

    is_pd = is_public_domain(_license)

    title = f'"{title}"' if title else "This work"
    _license = get_full_license_name(_license, license_version)

    attribution = "{title} {creator} {marked-licensed} {license}. {view-legal}"
    attribution_parts = {
        "title": title,
        "marked-licensed": "is marked with" if is_pd else "is licensed under",
        "license": _license,
        "view-legal": "",
        "creator": "",
    }

    if license_url:
        view_legal_temp = "To view {terms-copy}, visit {url}."
        view_legal_parts = {
            "terms-copy": "the terms" if is_pd else "a copy of this license",
            "url": license_url,
        }
        attribution_parts["view-legal"] = view_legal_temp.format(**view_legal_parts)

    if creator:
        creator_temp = "by {creator-name}"
        creator_parts = {"creator-name": creator}
        attribution_parts["creator"] = creator_temp.format(**creator_parts)

    attribution = attribution.format(**attribution_parts)

    return attribution.strip().replace("  ", " ")
