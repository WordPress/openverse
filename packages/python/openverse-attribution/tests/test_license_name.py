import pytest
from openverse_attribution.license_name import LicenseName


@pytest.mark.parametrize(
    "slug, display_name",
    [
        ("by", "CC BY"),
        ("sampling", "CC Sampling"),
        ("devnations", "CC DevNations"),
        ("cc0", "CC0"),
        ("pdm", "Public Domain Mark"),
        ("certification", "Public Domain Certification"),
    ],
)
def test_gets_display_name(slug: str, display_name: str):
    lic = LicenseName(slug)
    assert lic.display_name == display_name


@pytest.mark.parametrize(
    "slug, is_cc",
    [
        ("cc0", True),
        ("by", True),
        ("certification", False),
        ("pdm", False),
    ],
)
def test_identifies_licenses_as_cc(slug: str, is_cc: bool):
    lic = LicenseName(slug)
    assert lic.is_cc == is_cc


@pytest.mark.parametrize(
    "slug, is_dep",
    [
        ("sa", True),
        ("sampling+", True),
        ("nc-sampling+", True),
        ("by", False),
    ],
)
def test_identifies_licenses_as_deprecated(slug: str, is_dep: bool):
    lic = LicenseName(slug)
    assert lic.is_deprecated == is_dep


@pytest.mark.parametrize(
    "slug, is_pd",
    [
        ("cc0", True),
        ("certification", True),
        ("pdm", True),
        ("by", False),
    ],
)
def test_identifies_licenses_as_pd(slug: str, is_pd: bool):
    lic = LicenseName(slug)
    assert lic.is_pd == is_pd


@pytest.mark.parametrize(
    "slug, ver_jur",
    [
        ("sampling", [("1.0", "")]),
        ("sampling+", [("1.0", ""), ("1.0", "de")]),
        ("cc0", [("1.0", "")]),
        ("certification", [("1.0", "us")]),
        ("pdm", [("1.0", "")]),
    ],
)
def test_identifies_allowed_versions_and_jurisdictions(
    slug: str,
    ver_jur: list[tuple[str, str]],
):
    lic = LicenseName(slug)
    assert lic.allowed_ver_jur == ver_jur
