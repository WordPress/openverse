import pytest

from templates import create_provider_ingester


@pytest.mark.parametrize(
    "media_types_str, expected_types",
    [
        # Just image
        (["image"], ["image"]),
        # Just audio
        (["audio"], ["audio"]),
        # Multiple valid types
        (["image", "audio"], ["image", "audio"]),
        # Discard only invalid types
        (["image", "blorfl"], ["image"]),
        (["blorfl", "audio", "image"], ["audio", "image"]),
        # Defaults to image when all given types are invalid
        (["blorfl", "wat"], ["image"]),
        # Defaults to image when no types are given at all
        ([""], ["image"]),
        (None, ["image"]),
    ],
)
def test_parse_media_types(media_types_str, expected_types):
    actual_result = create_provider_ingester.parse_media_types(media_types_str)
    assert actual_result == expected_types


@pytest.mark.parametrize(
    "provider, expected_result",
    [
        ("FoobarIndustries", "FoobarIndustries"),
        # Do not remove hyphens or underscores
        ("hello-world_foo", "hello-world_foo"),
        # Replace spaces
        ("Foobar Industries", "Foobar_Industries"),
        # Replace periods
        ("foobar.com", "foobar_com"),
        # Remove trailing whitespace
        ("  hello world  ", "hello_world"),
        # Replace special characters
        ("hello.world-foo*/bar2", "hello_world-foobar2"),
    ],
)
def test_sanitize_provider(provider, expected_result):
    actual_result = create_provider_ingester.sanitize_provider(provider)
    assert actual_result == expected_result


def test_files_created(tmp_path):
    # Make temporary output directories for testing
    dags_path = tmp_path / "catalog" / "dags" / "providers"
    (dags_path / "provider_api_scripts").mkdir(parents=True)
    test_path = tmp_path / "catalog" / "tests"
    (test_path / "dags" / "providers" / "provider_api_scripts").mkdir(parents=True)

    provider = "foobar_industries"
    endpoint = "https://myfakeapi/v1"
    media_types = ["image"]

    expected_provider = dags_path / "provider_api_scripts" / "foobar_industries.py"
    expected_test = (
        test_path
        / "dags"
        / "providers"
        / "provider_api_scripts"
        / "test_foobar_industries.py"
    )
    try:
        create_provider_ingester.fill_template(
            provider,
            endpoint,
            media_types,
            project_path=(tmp_path / "catalog"),
            repo_path=tmp_path,
        )
        assert expected_provider.exists()
        assert expected_test.exists()
    finally:
        # Clean up
        expected_provider.unlink(missing_ok=True)
        expected_test.unlink(missing_ok=True)
