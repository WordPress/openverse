NO_VERSION = "N/A"

_SIMPLE_LICENSE_PATHS = [
    # This list holds recognized license URL path snippets that split
    # correctly into license_ and license_version, and for which we can
    # recover the path from a valid license_, license_version pair.
    "licenses/by/1.0",
    "licenses/by/2.0",
    "licenses/by/2.5",
    "licenses/by/3.0",
    "licenses/by/4.0",
    "licenses/by-nc/1.0",
    "licenses/by-nc/2.0",
    "licenses/by-nc/2.5",
    "licenses/by-nc/3.0",
    "licenses/by-nc/4.0",
    "licenses/by-nc-nd/2.0",
    "licenses/by-nc-nd/2.5",
    "licenses/by-nc-nd/3.0",
    "licenses/by-nc-nd/4.0",
    "licenses/by-nc-sa/1.0",
    "licenses/by-nc-sa/2.0",
    "licenses/by-nc-sa/2.5",
    "licenses/by-nc-sa/3.0",
    "licenses/by-nc-sa/4.0",
    "licenses/by-nd/1.0",
    "licenses/by-nd/2.0",
    "licenses/by-nd/2.5",
    "licenses/by-nd/3.0",
    "licenses/by-nd/4.0",
    "licenses/by-sa/1.0",
    "licenses/by-sa/2.0",
    "licenses/by-sa/2.5",
    "licenses/by-sa/3.0",
    "licenses/by-sa/4.0",
    "licenses/devnations/2.0",
    "licenses/nc/1.0",
    "licenses/nc/2.0/jp",
    "licenses/nc-sa/1.0",
    "licenses/nc-sa/2.0/jp",
    "licenses/nc-sampling+/1.0",
    "licenses/nd/1.0",
    "licenses/nd/2.0/jp",
    "licenses/nd-nc/1.0",
    "licenses/nd-nc/2.0/jp",
    "licenses/sa/1.0",
    "licenses/sa/2.0/jp",
    "licenses/sampling+/1.0",
    "licenses/sampling/1.0",
]

_SIMPLE_IRREVERSIBLE_LICENSE_PATHS = [
    # This list holds recognized license URL path snippets that split
    # correctly into license_ and license_version, but cannot be
    # recovered from a license_, license_version pair, because
    # jurisdiction info is required to know which path should be used.
    "licenses/by/2.1/au",
    "licenses/by/2.1/es",
    "licenses/by/2.1/jp",
    "licenses/by-nc/2.1/au",
    "licenses/by-nc/2.1/es",
    "licenses/by-nc/2.1/jp",
    "licenses/by-nc-nd/2.1/au",
    "licenses/by-nc-nd/2.1/es",
    "licenses/by-nc-nd/2.1/jp",
    "licenses/by-nc-sa/2.1/au",
    "licenses/by-nc-sa/2.1/es",
    "licenses/by-nc-sa/2.1/jp",
    "licenses/by-nd/2.1/au",
    "licenses/by-nd/2.1/es",
    "licenses/by-nd/2.1/jp",
    "licenses/by-sa/2.1/au",
    "licenses/by-sa/2.1/es",
    "licenses/by-sa/2.1/jp",
]

_SPECIAL_CASE_LICENSE_PATHS = {
    # This dictionary holds recognized path snippets for which we must
    # set the license and/or version manually, and for which we can
    # recover the path from a valid license_, license_version pair.
    "licenses/by-nd-nc/1.0": ("by-nc-nd", "1.0"),
    "licenses/publicdomain": ("publicdomain", NO_VERSION),
    "publicdomain/mark/1.0": ("pdm", "1.0"),
    "publicdomain/zero/1.0": ("cc0", "1.0"),
}

_SPECIAL_CASE_IRREVERSIBLE_LICENSE_PATHS = {
    # This dictionary holds recognized path snippets for which we must
    # set the license and/or version manually, and for which the license
    # path cannot be recovered from the license_, license_version pair.
    "licenses/mark/1.0": ("pdm", "1.0"),
}


_SPECIAL_REVERSE_ONLY_PATHS = {
    # This dictionary describes mappings from version 2.1 licenses
    # without jurisdiction info (which is needed to define a version 2.1
    # license) to unported version 2.0 licenses
    (license_, "2.1"): f"licenses/{license_}/2.0"
    for license_ in ["by", "by-nc", "by-nc-nd", "by-nc-sa", "by-nd", "by-sa"]
}


def _get_license_version_pair_from_path(path: str) -> tuple[str, str]:
    return path.split("/")[1], path.split("/")[2]


def get_license_path_map() -> dict[str, tuple[str, str]]:
    license_path_map = {
        path: _get_license_version_pair_from_path(path)
        for path in _SIMPLE_LICENSE_PATHS + _SIMPLE_IRREVERSIBLE_LICENSE_PATHS
    }
    license_path_map.update(_SPECIAL_CASE_LICENSE_PATHS)
    license_path_map.update(_SPECIAL_CASE_IRREVERSIBLE_LICENSE_PATHS)
    return license_path_map


def get_reverse_license_path_map() -> dict[tuple[str, str], str]:
    reverse_map = {
        _get_license_version_pair_from_path(path): path
        for path in _SIMPLE_LICENSE_PATHS
    }
    reverse_map.update(
        {pair: path for path, pair in _SPECIAL_CASE_LICENSE_PATHS.items()}
    )
    reverse_map.update(_SPECIAL_REVERSE_ONLY_PATHS)
    return reverse_map
