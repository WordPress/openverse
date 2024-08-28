import mimetypes

from common.constants import MEDIA_TYPES as SUPPORTED_TYPES


FILETYPE_EQUIVALENTS = {
    # Image extensions
    "jpeg": "jpg",
    "tif": "tiff",
    # Audio extensions
    "midi": "mid",
}

# Partially taken from Wikimedia aliases
# https://doc.wikimedia.org/mediawiki-core/master/php/MimeMap_8php_source.html
MIME_TYPE_ALIASES = {
    # Image aliases
    "image/x-bmp": "image/bmp",
    "image/x-ms-bmp": "image/bmp",
    "image/x-png": "image/png",
    "image/pjpeg": "image/jpeg",
    "image/x-ico": "image/vnd.microsoft.icon",
    "image/x-icon": "image/vnd.microsoft.icon",
    "image/svg": "image/svg+xml",
    # "image/x.djvu": "image/vnd.djvu",
    # "image/x-djvu": "image/vnd.djvu",
    "image/jpeg2000": "image/jp2",
    "image/jpeg200-image": "image/jp2",
    "image/x-jpeg200-image": "image/jp2",
    # Audio aliases
    "audio/mp3": "audio/mpeg",
    "audio/mpeg3": "audio/mpeg",
    "audio/x-flac": "audio/flac",
    "audio/mid": "audio/midi",
    "audio/wav": "audio/x-wav",
    "audio/wave": "audio/x-wav",
}


mimetypes.add_type("audio/midi", ".mid")
mimetypes.add_type("audio/midi", ".midi")
mimetypes.add_type("audio/x-matroska", ".mka")
mimetypes.add_type("audio/wav", ".wav")


class InvalidFiletypeError(Exception):
    def __init__(self, actual_filetype: str, expected_filetype: str, message: str = ""):
        self.actual_filetype = actual_filetype
        self.expected_filetype = expected_filetype
        if not message:
            message = (
                f"Extracted media type `{self.actual_filetype}` does not match "
                f"expected media type `{self.expected_filetype}`."
            )
        super().__init__(message)


def get_extension_from_mimetype(mime_type: str | None) -> str | None:
    if not mime_type:
        return
    mime_type = MIME_TYPE_ALIASES.get(mime_type, mime_type)
    ext = mimetypes.guess_extension(mime_type)
    # Removes the leading dot if there is an extension
    return ext[1:] if ext else None


def extract_filetype(url: str) -> tuple[str | None, str | None]:
    """
    Extract the filetype from a media url extension.

    Returns only if the media type guessed is a supported type.
    """
    if mime_type := mimetypes.guess_type(url)[0]:
        media_type, _ = mime_type.split("/")
        if media_type in SUPPORTED_TYPES:
            filetype = get_extension_from_mimetype(mime_type)
            return filetype, media_type
    return None, None
