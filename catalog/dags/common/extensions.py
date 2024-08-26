import mimetypes

from common.constants import MEDIA_TYPES as SUPPORTED_TYPES


FILETYPE_EQUIVALENTS = {
    # Image extensions
    "jpeg": "jpg",
    "tif": "tiff",
    # Audio extensions
    "midi": "mid",
}

mimetypes.add_type("audio/midi", ".mid")
mimetypes.add_type("audio/midi", ".midi")
mimetypes.add_type("audio/x-matroska", ".mka")


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


def extract_filetype(url: str) -> tuple[str | None, str | None]:
    """
    Extract the filetype from a media url extension.

    Returns only if the media type guessed is a supported type.
    """
    if mime_type := mimetypes.guess_type(url)[0]:
        media_type, _ = mime_type.split("/")
        filetype = mimetypes.guess_extension(mime_type)
        # Removes the leading dot if there is an extension
        filetype = filetype[1:] if filetype else None
        if media_type in SUPPORTED_TYPES:
            return filetype, media_type
    return None, None
