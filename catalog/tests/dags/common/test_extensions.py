import pytest

from common import extensions


@pytest.mark.parametrize(
    "url, expected_media_type, expected_filetype",
    [
        # Valid images
        ("https://example.com/image.apng", "image", "apng"),
        ("https://example.com/image.avif", "image", "avif"),
        ("https://example.com/image.bmp", "image", "bmp"),
        ("https://example.com/image.djvu", "image", "djvu"),
        ("https://example.com/image.gif", "image", "gif"),
        ("https://example.com/image.ICO", "image", "ico"),
        ("https://example.com/image.jpg", "image", "jpg"),
        ("https://example.com/image.Jpeg", "image", "jpg"),
        ("https://example.com/image.png", "image", "png"),
        ("https://example.com/image.svg", "image", "svg"),
        ("https://example.com/image.tif", "image", "tiff"),
        ("https://example.com/image.tiFF", "image", "tiff"),
        ("https://example.com/image.webp", "image", "webp"),
        # Valid audio
        ("https://example.com/audio.aif", "audio", "aif"),
        ("https://example.com/audio.aiff", "audio", "aif"),
        ("https://example.com/audio.flac", "audio", "flac"),
        ("https://example.com/audio.m4a", "audio", "m4a"),
        ("https://example.com/audio.m3u", "audio", "m3u"),
        ("https://example.com/audio.mid", "audio", "mid"),
        ("https://example.com/audio.midi", "audio", "mid"),
        ("https://example.com/audio.mka", "audio", "mka"),
        ("https://example.com/audio.mp3", "audio", "mp3"),
        ("https://example.com/audio.ogg", "audio", "oga"),
        ("https://example.com/audio.opus", "audio", "oga"),
        ("https://example.com/audio.wav", "audio", "wav"),
        # Invalid cases
        ("https://example.com/test.jpg.image", None, None),
        ("https://example.com/video.ogv", None, None),
        ("https://example.com/doc.pdf", None, None),
        ("https://example.com/test.stl", None, None),
        ("https://example.com/test.xyz", None, None),
        ("https://example.com/test123", None, None),
    ],
)
def test_extract_filetype_returns_for_supported_media_type(
    url, expected_media_type, expected_filetype
):
    actual_filetype, actual_media_type = extensions.extract_filetype(url)
    assert actual_filetype == expected_filetype
    assert actual_media_type == expected_media_type


@pytest.mark.parametrize(
    "input_mime, expected_value",
    [
        (None, None),
        # Image file types
        ("image/gif", "gif"),
        ("image/jpeg", "jpg"),
        ("image/svg+xml", "svg"),
        ("image/x-ico", "ico"),
        ("image/x.djvu", "djvu"),
        ("image/x-djvu", "djvu"),
        # Audio file types
        ("audio/flac", "flac"),
        ("audio/x-flac", "flac"),
        ("audio/midi", "mid"),
        ("audio/mp3", "mp3"),
        ("audio/mpeg3", "mp3"),
        ("audio/ogg", "oga"),
        ("audio/opus", "opus"),
        ("audio/wav", "wav"),
        ("audio/x-wav", "wav"),
        ("audio/x-matroska", "mka"),
    ],
)
def test_get_extension_from_mimetype(input_mime, expected_value):
    assert extensions.get_extension_from_mimetype(input_mime) == expected_value
