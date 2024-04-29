from enum import StrEnum


class License(StrEnum):
    """
    Represent all licenses that are handled by Openverse. This uses a very loose
    interpretation of the term "license" as it includes licenses (both active
    and deprecated), dedications and marks.
    """

    # CC licenses
    BY = "by"
    BY_SA = "by-sa"
    BY_NC = "by-nc"
    BY_ND = "by-nd"
    BY_NC_SA = "by-nc-sa"
    BY_NC_ND = "by-nc-nd"

    # Deprecated CC licenses
    SA = "sa"
    SAMPLING = "sampling+"
    NC_SAMPLING = "nc-sampling+"

    # Public domain dedication
    CC0 = "cc0"

    # Public domain mark
    PDM = "pdm"

    def name(self, version: str | None = None) -> str:
        """
        Get the full name of the license.
        The ``version`` parameter is disregarded and the version is always 1.0
        for CC0, PDM and deprecated licenses. If not provided, the version is
        omitted for all other licenses.

        :param version: the version number of the license
        :return: the full name of the license
        """

        if self is License.PDM:
            name = "Public Domain Mark"
        else:
            name = self.value.upper().replace("SAMPLING", "Sampling")
        if self.is_cc and self is not License.CC0:
            name = f"CC {name}"
        if self.is_pd or self.is_deprecated:
            version = "1.0"
        if version:
            name = f"{name} {version}"
        return name.strip()

    def url(self, version: str | None = None) -> str:
        """
        Get the URL to the legal deed of this license.
        The ``version`` parameter is disregarded and the version is always 1.0
        for CC0, PDM and deprecated licenses. If not provided, the version is
        assumed to be 4.0 for all other licenses.

        :param version: the version number of the license
        :return: the URL to the legal text of this license
        """

        if self is License.CC0:
            fragment = "publicdomain/zero/1.0"
        elif self is License.PDM:
            fragment = "publicdomain/mark/1.0"
        elif self.is_deprecated:
            fragment = f"licenses/{self}/1.0"
        else:
            fragment = f"licenses/{self}/{version or '4.0'}"
        return f"https://creativecommons.org/{fragment}/"

    @property
    def is_deprecated(self) -> bool:
        """
        Determine if this license has been deprecated. These licenses are no
        longer maintained as only have a version 1.0.

        :return: whether this license has been deprecated
        """

        return self in {License.SAMPLING, License.NC_SAMPLING, License.SA}

    @property
    def is_pd(self) -> bool:
        """
        Determine whether a work with this license is in the public domain. This
        function also differentiates a license from a mark or dedication.

        :return: whether a work with this license is in the public domain
        """

        return self in {License.PDM, License.CC0}

    @property
    def is_cc(self) -> bool:
        """
        Determine whether this license was created by Creative Commons. Note
        that this includes CC0 which was created by CC.

        :return: whether this license was created by Creative Commons
        """

        # Works because other than PDM, we only have CC licenses.
        return self is not License.PDM
