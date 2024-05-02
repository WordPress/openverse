import pytest
import requests
from openverse_attribution.license import License
from openverse_attribution.license_name import LicenseName


@pytest.mark.parametrize(
    "slug, expected",
    [
        ("zero", "cc0"),
        ("mark", "pdm"),
    ],
)
def test_license_handles_aliases(slug: str, expected: str):
    assert License(slug).slug == expected


@pytest.mark.parametrize(
    "slug, version, jurisdiction, attr, val",
    [
        ("certification", None, None, "ver", "1.0"),  # infers version with surety
        ("certification", None, None, "jur", "us"),  # infers jurisdiction with surety
        (
            "by",
            None,
            None,
            "fallback_ver",
            "4.0",
        ),  # cannot infer version, falls back to latest
        (
            "by",
            None,
            None,
            "fallback_jur",
            "",
        ),  # cannot infer jurisdiction, falls back to generic
        ("nc", "2.0", None, "jur", "jp"),  # infers jurisdiction with surety
        ("by-nc", "4.0", None, "jur", ""),  # infers jurisdiction with surety
        ("by", None, "pe", "ver", "2.5"),  # infers version with surety
    ],
)
def test_license_validation_autocompletes_missing_info(
    slug: str,
    version: str | None,
    jurisdiction: str | None,
    attr: str,
    val: str,
):
    lic = License(slug, version, jurisdiction)
    assert getattr(lic, attr) == val


@pytest.mark.parametrize(
    "slug, version, jurisdiction, msg",
    [
        # raised in ``__init__``
        ("by", "5.0", None, "Version `5.0` does not exist."),
        ("by", None, "done", "Jurisdiction `done` does not exist."),
        ("by", "1.0", "jp", "Jurisdiction `jp` does not exist for version `1.0`."),
        # raised in ``_deduce_ver``
        ("nd", None, "in", "No version matches slug `nd` and jurisdiction `in`."),
        # raised in ``_deduce_jur``
        (
            "by",
            "2.1",
            None,
            "Jurisdiction is required for slug `by` and version `2.1`.",
        ),
        (
            "sampling+",
            "4.0",
            None,
            r"No jurisdiction matches slug `sampling\+` and version `4.0`.",
        ),
        # raised in ``_deduce_ver_jur``
        (
            "sampling",
            "1.0",
            "fi",
            "License `sampling` does not accept version `1.0` and jurisdiction `fi`.",
        ),
    ],
)
def test_license_validation_fails_if_contradictory_info(
    slug: str,
    version: str | None,
    jurisdiction: str | None,
    msg: str,
):
    with pytest.raises(ValueError, match=msg):
        License(slug, version, jurisdiction)


@pytest.mark.parametrize(
    "slug",
    [lic.value for lic in LicenseName],
)
def test_license_validation_never_fails_for_just_name(slug: str):
    assert License(slug)


@pytest.mark.parametrize(
    "slug, version, jurisdiction, full_name",
    [
        ("cc0", None, None, "CC0 1.0"),
        ("pdm", None, None, "Public Domain Mark 1.0"),
        ("certification", None, None, "Public Domain Certification 1.0 US"),
        ("publicdomain", None, None, "Public Domain"),
        ("sa", None, None, "CC SA"),
        ("sa", "2.0", None, "CC SA 2.0 JP"),
        ("sa", "2.0", "jp", "CC SA 2.0 JP"),
        ("sampling+", None, None, "CC Sampling+"),
        ("by", None, None, "CC BY"),
        ("by", "2.0", None, "CC BY 2.0"),
        ("by", "2.5", "scotland", "CC BY 2.5 SCOTLAND"),
        ("devnations", None, None, "CC DevNations 2.0"),
    ],
)
def test_license_generates_name(
    slug: str,
    version: str | None,
    jurisdiction: str | None,
    full_name: str,
):
    lic = License(slug, version, jurisdiction)
    assert lic.full_name == full_name


@pytest.mark.parametrize(
    "slug, version, jurisdiction, path",
    [
        ("cc0", None, None, "publicdomain/zero/1.0/"),
        ("pdm", None, None, "publicdomain/mark/1.0/"),
        ("certification", None, None, "publicdomain/certification/1.0/us/"),
        ("publicdomain", None, None, "wiki/Public_domain"),
        ("sa", None, None, "licenses/sa/1.0/"),
        ("sa", "2.0", None, "licenses/sa/2.0/jp/"),
        ("sa", "2.0", "jp", "licenses/sa/2.0/jp/"),
        ("sampling+", None, None, "licenses/sampling+/1.0/"),
        ("by", None, None, "licenses/by/4.0/"),
        ("by", "2.0", None, "licenses/by/2.0/"),
        ("by", "2.5", "scotland", "licenses/by/2.5/scotland/"),
        ("devnations", None, None, "licenses/devnations/2.0/"),
    ],
)
def test_license_generates_url(
    slug: str,
    version: str | None,
    jurisdiction: str | None,
    path: str,
):
    lic = License(slug, version, jurisdiction)
    assert lic.url.endswith(path)


@pytest.mark.skip(reason="License URLs are broken on creativecommons.org")  # TODO
@pytest.mark.parametrize(
    "lic",
    [
        pytest.param(lic := License(name.value, ver, jur), id=lic.url)
        for name in LicenseName
        for (ver, jur) in name.allowed_ver_jur
    ],
)
def test_all_urls_are_valid(lic: License):
    res = requests.head(lic.url)
    assert res.status_code == 200
