import re

from openverse_attribution.license import License


def get_attribution_text(
    license_slug: str,
    title: str | None = None,
    creator: str | None = None,
    license_version: str | None = None,
    license_url: str | bool | None = None,
):
    """
    Get the attribution text for a media item. This function only renders the
    attribution in plain-text format for the English language.
    Note that this is not a perfect attribution as it does not include
    hyperlinks for the work or the creator. Also see the CC `wiki`_ to learn
    best practices for attribution.

    .. _wiki: https://wiki.creativecommons.org/wiki/Best_practices_for_attribution

    To remove the sentence for viewing the legal text, set the ``license_url``
    parameter to ``False``.

    :param title: the name of the work, if known
    :param creator: the name of the work's creator, if known
    :param license_slug:
    :param license_version: the version of the license, if known
    :param license_url: the URL to the license, to override the default
    :return: the plain-text English language attribution
    """

    lic = License(license_slug)

    title = f'"{title}"' if title else "This work"

    attribution_template = "{title} {creator} {marked-licensed} {license}. {view-legal}"
    attribution_parts = {
        "title": title,
        "marked-licensed": "is marked with" if lic.is_pd else "is licensed under",
        "license": lic.name(license_version),
        "view-legal": "",
        "creator": "",
    }

    if license_url is not False:
        license_url = license_url or lic.url(license_version)
        view_legal_template = "To view {terms-copy}, visit {url}."
        view_legal_parts = {
            "terms-copy": "the terms" if lic.is_pd else "a copy of this license",
            "url": license_url,
        }
        attribution_parts["view-legal"] = view_legal_template.format(**view_legal_parts)

    if creator:
        creator_template = "by {creator-name}"
        creator_parts = {"creator-name": creator}
        attribution_parts["creator"] = creator_template.format(**creator_parts)

    attribution = attribution_template.format(**attribution_parts)

    return re.sub(r"\s{2,}", " ", attribution).strip()
