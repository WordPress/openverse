from enum import StrEnum

from openverse_attribution.data.all_licenses import all_licenses


NON_CC_SLUGS = {"pdm", "publicdomain", "certification"}
DEPRECATED_SLUGS = {
    "sa",
    "nc",
    "nd",
    "nc-sa",
    "nd-nc",
    "sampling",
    "sampling+",
    "nc-sampling+",
    "devnations",
    "certification",
}
PUBLIC_DOMAIN_SLUGS = NON_CC_SLUGS | {"cc0"}


class LicenseName(StrEnum):
    """
    Represents all existing CC "licenses".

    This uses a very loose interpretation of the term "license" as it includes
    licenses (both active and deprecated), dedications and marks.
    """

    # CC licenses
    BY = "by"
    BY_SA = "by-sa"
    BY_NC = "by-nc"
    BY_ND = "by-nd"
    BY_NC_SA = "by-nc-sa"
    BY_NC_ND = "by-nc-nd"

    # Retired CC licenses
    SA = "sa"
    NC = "nc"
    ND = "nd"
    NC_SA = "nc-sa"
    ND_NC = "nd-nc"
    BY_ND_NC = "by-nd-nc"  # later renamed to BY_NC_ND

    SAMPLING = "sampling"
    SAMPLING_PLUS = "sampling+"
    NC_SAMPLING_PLUS = "nc-sampling+"
    DEVNATIONS = "devnations"

    # Public domain
    CC0 = "cc0"
    CERTIFICATION = "certification"
    PDM = "pdm"
    PUBLICDOMAIN = "publicdomain"

    @property
    def display_name(self) -> str:
        """
        Get the name of the license as supposed to be displayed to a reader.

        :return: the display name of the license
        """

        if self is LicenseName.PDM:
            return "Public Domain Mark"
        if self is LicenseName.CERTIFICATION:
            return "Public Domain Certification"
        if self is LicenseName.PUBLICDOMAIN:
            return "Public Domain"

        name = self.value.upper()
        if self is LicenseName.CC0:
            return name

        name = name.replace("SAMPLING", "Sampling").replace("DEVNATIONS", "DevNations")
        return f"CC {name}"

    @property
    def is_cc(self) -> bool:
        """
        Determine whether this license was created by Creative Commons. Note
        that this includes CC0 which was created by CC.

        :return: whether this license was created by Creative Commons
        """

        return self.value not in NON_CC_SLUGS

    @property
    def is_deprecated(self) -> bool:
        """
        Determine if this license has been deprecated. These licenses are no
        longer maintained and have a disclaimer on their legal page recommending
        against their usage.

        :return: whether this license has been deprecated
        """

        return self in DEPRECATED_SLUGS

    @property
    def is_pd(self) -> bool:
        """
        Determine whether a work with this license is in the public domain. This
        function also differentiates a license from a mark or dedication.

        :return: whether a work with this license is in the public domain
        """

        return self in PUBLIC_DOMAIN_SLUGS

    @property
    def allowed_ver_jur(self) -> list[tuple[str, str]]:
        """
        Get a list of versions and jurisdictions where this license is valid.

        :return: a list of allowed versions and jurisdictions
        """

        return [
            (ver, jur)
            for ver in all_licenses.keys()
            for jur in all_licenses[ver].keys()
            if self.value in all_licenses[ver][jur]
        ]
