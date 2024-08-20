import pytest

from common import extensions


@pytest.mark.parametrize(
    "url, expected_media_type, expected_filetype",
    [
        # Valid images
        ("https://example.com/test.jpg", "image", "jpg"),
        ("https://example.com/image.aPng", "image", "apng"),
        ("https://example.com/image.Png", "image", "png"),
        ("https://example.com/image.GIF", "image", "gif"),
        ("https://example.com/image.tif", "image", "tiff"),
        ("https://example.com/image.tiFF", "image", "tiff"),
        # Valid audio
        ("https://example.com/audio.midi", "audio", "mid"),
        ("https://example.com/audio.mp3", "audio", "mp3"),
        ("https://example.com/audio.ogg", "audio", "oga"),
        ("https://example.com/audio.opus", "audio", "oga"),
        ("https://example.com/audio.WAV", "audio", "wav"),
        ("https://example.com/audio.mid", "audio", "mid"),
        # Invalid cases
        ("https://example.com/image.ogv", None, None),
        ("https://example.com/test.jpg.image", None, None),
        ("https://example.com/doc.pdf", None, None),
        ("https://example.com/image.xyz", None, None),
        ("https://example.com/test.stl", None, None),
        ("https://example.com/test123", None, None),
    ],
)
def test_extract_filetype_returns_for_supported_media_type(
    url, expected_media_type, expected_filetype
):
    actual_filetype, actual_media_type = extensions.extract_filetype(url)
    assert actual_filetype == expected_filetype
    assert actual_media_type == expected_media_type
