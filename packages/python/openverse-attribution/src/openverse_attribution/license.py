import re
from dataclasses import dataclass

from openverse_attribution.data.all_licenses import all_licenses
from openverse_attribution.license_name import LicenseName


KNOWN_ALIASES = {
    "zero": "cc0",
    "mark": "pdm",
}


@dataclass
class License:
    name: LicenseName
    ver: str | None
    jur: str | None

    def __init__(
        self,
        slug: str,
        version: str | None = None,
        jurisdiction: str | None = None,
    ):
        """
        Create an instance of ``License``.

        This function validates the license, version and jurisdiction. If some
        fields are not provided, it makes an attempt to deduce them.

        The only exception is 'publicdomain' for which the version and
        jurisdiction fields are ignored.

        Use an empty string as ``jur`` to specify a generic, universal or
        unported form of the license.

        :param slug: the slug for the license, from the ``LicenseName`` enum
        :param version: the version of the license
        :param jurisdiction: the jurisdiction of the license
        """

        # Shorten long variable names
        ver = version
        jur = jurisdiction

        # Handle known aliases.
        slug = KNOWN_ALIASES.get(slug, slug)

        self.slug = slug

        # Encapsulates internal enum validation.
        self.name = LicenseName(slug)

        self.fallback_ver = None
        self.fallback_jur = None

        if self.name is LicenseName.PUBLICDOMAIN:
            self.ver = None
            self.jur = None
            return

        # Validate version against known versions.
        if ver:
            if ver not in all_licenses.keys():
                raise ValueError(f"Version `{ver}` does not exist.")

        # Validate jurisdiction against known jurisdictions.
        if jur is not None:
            if all(jur not in item for item in all_licenses.values()):
                raise ValueError(f"Jurisdiction `{jur}` does not exist.")

            if ver:
                if jur not in all_licenses[ver].keys():
                    raise ValueError(
                        f"Jurisdiction `{jur}` does not exist for version `{ver}`."
                    )

        # Validation (with autocompletion)
        if not ver and jur is None:
            self.ver, self.jur = self._deduce_ver_jur() or (None, None)
        elif not ver and jur is not None:
            self.jur = jur
            self.ver = self._deduce_ver()
        elif ver and jur is None:
            self.ver = ver
            self.jur = self._deduce_jur()
        else:  # ver and jur is not None
            self.ver = ver
            self.jur = jur
            if (ver, jur) not in self.name.allowed_versions_jurisdictions:
                raise ValueError(
                    f"License `{slug}` does not accept version `{ver}` and jurisdiction `{jur}`."
                )

    def _deduce_ver(self) -> str | None:
        """
        Deduce version from slug and jurisdiction.

        This function sets ``fallback_ver`` to latest allowed version if it
        cannot be determined for certain.

        :return: the certain value of the version
        :raise ValueError: if no version matches slug and jurisdiction
        """

        allowed_ver_jur = self.name.allowed_versions_jurisdictions
        allowed_vers = [v for v, j in allowed_ver_jur if j == self.jur]
        if len(allowed_vers) > 1:
            self.fallback_ver = allowed_vers[0]  # latest
        elif len(allowed_vers) == 1:
            return allowed_vers.pop()
        else:
            raise ValueError(
                f"No version matches slug `{self.slug}` and jurisdiction `{self.jur}`."
            )

    def _deduce_jur(self) -> str | None:
        """
        Deduce jurisdiction from slug and version.

        This function sets ``fallback_jur`` to generic jurisdiction if it cannot
        be determined for certain and generic is an option.

        :return: the certain value of the jurisdiction
        :raise ValueError: if jurisdiction is required or no jurisdiction
            matches slug and version
        """

        allowed_ver_jur = self.name.allowed_versions_jurisdictions
        allowed_jurs = {j for v, j in allowed_ver_jur if v == self.ver}
        if len(allowed_jurs) > 1:
            if "" in allowed_jurs:
                # We can only assume generic jurisdiction as fallback.
                self.fallback_jur = ""
            else:
                raise ValueError(
                    f"Jurisdiction is required for slug `{self.slug}` and version `{self.ver}`."
                )
        elif len(allowed_jurs) == 1:
            return allowed_jurs.pop()
        else:
            raise ValueError(
                f"No jurisdiction matches slug `{self.slug}` and version `{self.ver}`."
            )

    def _deduce_ver_jur(self) -> tuple[str, str] | None:
        """
        Deduce version and jurisdiction from slug.

        This function sets ``fallback_ver`` and ``fallback_jur`` to the latest
        allowed version and generic jurisdiction respectively if they cannot be
        determined for certain.

        :return: the certain values of the version and jurisdiction
        """

        allowed_ver_jur = self.name.allowed_versions_jurisdictions
        if len(allowed_ver_jur) == 1:
            return allowed_ver_jur[0]

        allowed_ver_jur = [(v, j) for (v, j) in allowed_ver_jur if j == ""]
        if len(allowed_ver_jur) >= 1:
            # We can only assume generic jurisdiction as fallback.
            self.fallback_ver, self.fallback_jur = allowed_ver_jur[0]
        else:
            raise ValueError(f"No version and jurisdiction match slug `{self.slug}`.")

    @property
    def full_name(self) -> str:
        """
        Get the full name of the license.

        This function does not use the fallback version and jurisdiction because
        the license name is valid without them.

        :return: the full name of the license
        """

        name = self.name.display_name
        if self.ver:
            name = f"{name} {self.ver}"
        if self.jur:
            name = f"{name} {self.jur.upper()}"
        return name

    @property
    def url(self) -> str:
        """
        Get the URL to the deed of this license.

        This function uses the fallback version and jurisdiction as they are
        part of the URL and URL cannot be generated without them.

        :return: the URL to the deed of the license
        """

        ver = self.ver if self.ver is not None else self.fallback_ver
        jur = self.jur if self.jur is not None else self.fallback_jur

        if self.name is LicenseName.PUBLICDOMAIN:
            return "https://en.wikipedia.org/wiki/Public_domain"

        if self.name is LicenseName.CC0:
            fragment = f"publicdomain/zero/{ver}/{jur}"
        elif self.name is LicenseName.PDM:
            fragment = f"publicdomain/mark/{ver}/{jur}"
        elif self.name is LicenseName.CERTIFICATION:
            fragment = f"publicdomain/certification/{ver}/{jur}"
        else:
            fragment = f"licenses/{self.name}/{ver}/{jur}"

        if not fragment.endswith("/"):
            fragment = f"{fragment}/"

        return f"https://creativecommons.org/{fragment}"

    def get_attribution_text(
        self,
        title: str | None = None,
        creator: str | None = None,
        url: str | bool | None = None,
    ):
        """
        Get the attribution text for a media item. This function only renders
        the attribution in plain-text format for the English language.

        Note that this is not a perfect attribution as it does not include
        hyperlinks for the work or the creator. Also see the CC `wiki`_ to learn
        best practices for attribution.

        .. _wiki: https://wiki.creativecommons.org/wiki/Best_practices_for_attribution

        To remove the sentence for viewing the legal text, set the ``url``
        parameter to ``False``.

        :param title: the name of the work, if known
        :param creator: the name of the work's creator, if known
        :param url: the URL to the license, to override the default
        :return: the plain-text English language attribution
        """

        title = f'"{title}"' if title else "This work"

        attribution_template = (
            "{title} {creator} {marked-licensed} {license}. {view-legal}"
        )
        attribution_parts = {
            "title": title,
            "marked-licensed": "is marked with"
            if self.name.is_pd
            else "is licensed under",
            "license": self.full_name,
            "view-legal": "",
            "creator": "",
        }

        if url is not False:
            license_url = url or self.url
            view_legal_template = "To view {terms-copy}, visit {url}."
            view_legal_parts = {
                "terms-copy": "the terms"
                if self.name.is_pd
                else "a copy of this license",
                "url": license_url,
            }
            attribution_parts["view-legal"] = view_legal_template.format(
                **view_legal_parts
            )

        if creator:
            creator_template = "by {creator-name}"
            creator_parts = {"creator-name": creator}
            attribution_parts["creator"] = creator_template.format(**creator_parts)

        attribution = attribution_template.format(**attribution_parts)

        return re.sub(r"\s{2,}", " ", attribution).strip()
