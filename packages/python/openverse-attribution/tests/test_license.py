import pytest
from openverse_attribution.license import License


def test_raises_value_error_on_invalid_license():
    with pytest.raises(ValueError):
        License("invalid")


@pytest.mark.parametrize(
    "slug, version, name",
    [
        ("cc0", None, "CC0 1.0"),
        ("cc0", "2.0", "CC0 1.0"),
        ("pdm", None, "Public Domain Mark 1.0"),
        ("pdm", "2.0", "Public Domain Mark 1.0"),
        ("sa", None, "CC SA 1.0"),
        ("sa", "2.0", "CC SA 1.0"),
        ("sampling+", None, "CC Sampling+ 1.0"),
        ("sampling+", "2.0", "CC Sampling+ 1.0"),
        ("by", None, "CC BY"),
        ("by", "2.0", "CC BY 2.0"),
    ],
)
def test_can_get_name_for_license(slug: str, version: str, name: str):
    lic = License(slug)
    assert lic.name(version) == name


@pytest.mark.parametrize(
    "slug, version, path",
    [
        ("cc0", None, "publicdomain/zero/1.0/"),
        ("cc0", "2.0", "publicdomain/zero/1.0/"),
        ("pdm", None, "publicdomain/mark/1.0/"),
        ("pdm", "2.0", "publicdomain/mark/1.0/"),
        ("sa", None, "licenses/sa/1.0/"),
        ("sa", "2.0", "licenses/sa/1.0/"),
        ("sampling+", None, "licenses/sampling+/1.0/"),
        ("sampling+", "2.0", "licenses/sampling+/1.0/"),
        ("by", None, "licenses/by/4.0/"),
        ("by", "2.0", "licenses/by/2.0/"),
    ],
)
def test_can_get_url_for_license(slug: str, version: str, path: str):
    lic = License(slug)
    assert lic.url(version).endswith(path)


@pytest.mark.parametrize(
    "slug, is_dep",
    [
        ("sa", True),
        ("sampling+", True),
        ("nc-sampling+", True),
        ("by", False),
    ],
)
def test_can_identify_licenses_as_deprecated(slug: str, is_dep: bool):
    lic = License(slug)
    assert lic.is_deprecated == is_dep


@pytest.mark.parametrize(
    "slug, is_pd",
    [
        ("cc0", True),
        ("pdm", True),
        ("by", False),
    ],
)
def test_can_identify_licenses_as_pd(slug: str, is_pd: bool):
    lic = License(slug)
    assert lic.is_pd == is_pd


@pytest.mark.parametrize(
    "slug, is_cc",
    [
        ("cc0", True),
        ("by", True),
        ("pdm", False),
    ],
)
def test_can_identify_licenses_as_cc(slug: str, is_cc: bool):
    lic = License(slug)
    assert lic.is_cc == is_cc
