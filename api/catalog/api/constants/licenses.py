# This differs from the frontend which does not consider CC0 as a CC license
CC_LICENSES = {"by", "by-sa", "by-nd", "by-nc", "by-nc-sa", "by-nc-nd", "cc0"}

DEPRECATED_CC_LICENSES = {"sampling+", "nc-sampling+"}

PUBLIC_DOMAIN_MARKS = {"cc0", "pdm"}

ALL_CC_LICENSES = CC_LICENSES | DEPRECATED_CC_LICENSES

ACTIVE_LICENSES = PUBLIC_DOMAIN_MARKS | CC_LICENSES

ALL_LICENSES = ACTIVE_LICENSES | DEPRECATED_CC_LICENSES

LICENSE_GROUPS = {
    # All available licenses and marks
    "all": ALL_LICENSES,
    # All CC licenses
    "all-cc": ALL_CC_LICENSES,
    # All licenses allowing commercial use
    "commercial": {_license for _license in ALL_LICENSES if "nc" not in _license},
    # All licenses allowing creation of derivative works
    "modification": {_license for _license in ALL_LICENSES if "nd" not in _license},
}
