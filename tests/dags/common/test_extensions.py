import pytest
from common import extensions


@pytest.mark.parametrize(
    "url, media_type, filetype",
    [
        ("https://example.com/test.jpg", "image", "jpg"),
        ("https://example.com/test.m4b", "audio", "m4b"),
    ],
)
def test_extract_filetype_returns_filetype_for_media_type(url, media_type, filetype):
    expected_extension = extensions.extract_filetype(url, media_type)
    assert expected_extension == filetype


@pytest.mark.parametrize(
    "url, media_type",
    [
        ("https://example.com/test.jpg.image", "image"),
        ("https://example.com/test123", "audio"),
    ],
)
def test_extract_filetype_returns_None_if_no_extension_in_url(url, media_type):
    expected_extension = extensions.extract_filetype(url, media_type)
    assert expected_extension is None


@pytest.mark.parametrize(
    "url, wrong_media_type, correct_media_type, filetype",
    [
        ("https://example.com/test.jpg", "audio", "image", "jpg"),
        ("https://example.com/test.mp3", "image", "audio", "mp3"),
    ],
)
def test_extract_filetype_returns_only_corresponding_mediatype_filetype(
    url, wrong_media_type, correct_media_type, filetype
):
    """
    We check that the filetype exists for other media types, but returns None
    for the specific media type we are testing.
    """
    expected_extension = extensions.extract_filetype(url, wrong_media_type)
    assert expected_extension is None
    assert extensions.extract_filetype(url, correct_media_type) == filetype


def test_extract_filetype_returns_None_for_invalid_media_type():
    """
    This test specifically adds valid extensions for the media types we plan to add.
    It is expected that this test will fail if we add more media types.
    """
    assert extensions.extract_filetype("https://example.com/test.mp4", "video") is None
    assert (
        extensions.extract_filetype("https://example.com/test.stl", "model_3D") is None
    )
    assert (
        extensions.extract_filetype("https://example.com/test.sdd", "nomedia") is None
    )
