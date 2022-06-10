EXTENSIONS = {
    "image": {"jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff", "tif", "svg"},
    "audio": {"mp3", "ogg", "wav", "aiff", "flac", "wma", "mp4", "aac", "m4a", "m4b"},
}


def extract_filetype(url: str, media_type: str) -> str | None:
    """
    Extracts the filetype from a media url extension.
    """
    possible_filetype = url.split(".")[-1]
    if possible_filetype in EXTENSIONS.get(media_type, {}):
        return possible_filetype
    return None
