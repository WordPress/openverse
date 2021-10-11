"""
Content Provider:       Jamendo

ETL Process:            Use the API to identify all CC-licensed audio.

Output:                 TSV file containing the audio meta-data.

Notes:                  https://api.jamendo.com/v3.0/tracks/
                        35,000 requests per month for non-commercial apps
                        Jamendo Music has more than 500,000 tracks shared by
                        40,000 artists from over 150 countries all over
                        the world.
                        Audio quality: uploaded as WAV/ FLAC/ AIFF
                        bit depth: 16/24
                        sample rate: 44.1 or 48 kHz
                        channels: 1/2
"""
import logging
import os
from functools import lru_cache
from typing import Optional
from urllib.parse import parse_qs, urlencode, urlsplit

import common
from common.licenses.licenses import get_license_info
from common.requester import DelayedRequester
from common.urls import rewrite_redirected_url
from storage.audio import AudioStore
from util.loader import provider_details as prov


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
logging.getLogger(common.urls.__name__).setLevel(logging.WARNING)

LIMIT = 200  # number of items per page in API response
DELAY = 1  # in seconds
RETRIES = 3

HOST = "jamendo.com"
ENDPOINT = f"https://api.{HOST}/v3.0/tracks"
PROVIDER = prov.JAMENDO_DEFAULT_PROVIDER
APP_KEY = os.getenv("JAMENDO_APP_KEY", "not_set")

HEADERS = {
    "Accept": "application/json",
}
DEFAULT_QUERY_PARAMS = {
    # jsonpretty can have invalid characters in json:
    # \u0009 tab breaks the json
    "format": "json",
    "client_id": APP_KEY,
    "include": "musicinfo licenses stats lyrics",
    "imagesize": 200,
    "limit": LIMIT,
    "audioformat": "mp32",
}

delayed_requester = DelayedRequester(DELAY)
audio_store = AudioStore(provider=PROVIDER)


def main():
    """
    This script pulls the data for a given date from the Jamendo,
    and writes it into a .TSV file to be eventually read
    into our DB.
    """

    logger.info("Begin: Jamendo script")
    audio_count = _get_items()
    audio_store.commit()
    logger.info(f"Total audio pulled: {audio_count}")
    logger.info("Terminated!")


def _get_query_params(
    offset,
    default_query_params=None,
):
    if default_query_params is None:
        default_query_params = DEFAULT_QUERY_PARAMS
    query_params = default_query_params.copy()
    query_params["offset"] = offset
    return query_params


def _get_items():
    item_count = 0
    should_continue = True
    offset = 0
    while should_continue:
        query_params = _get_query_params(offset=offset)
        batch_data = _get_batch_json(query_params=query_params)
        if isinstance(batch_data, list) and len(batch_data) > 0:
            item_count = _process_item_batch(batch_data)
            offset += LIMIT
        else:
            should_continue = False
    return item_count


def _get_batch_json(
    endpoint=ENDPOINT, headers=None, retries=RETRIES, query_params=None
):
    if headers is None:
        headers = HEADERS
    response_json = delayed_requester.get_response_json(
        endpoint, retries, query_params, headers=headers
    )
    if response_json is None:
        return None
    else:
        results = response_json.get("results")
        return results


def _process_item_batch(items_batch):
    for item in items_batch:
        item_meta_data = _extract_audio_data(item)
        if item_meta_data is None:
            continue
        audio_store.add_item(**item_meta_data)
    return audio_store.total_items


def _extract_audio_data(media_data):
    try:
        foreign_landing_url = media_data["shareurl"]
    except (TypeError, KeyError, AttributeError):
        return None
    audio_url, duration, download_url = _get_audio_info(media_data)
    if audio_url is None:
        return None
    item_license = _get_license(media_data)
    if item_license is None:
        return None
    foreign_identifier = _get_foreign_identifier(media_data)
    title = _get_title(media_data)
    creator, creator_url = _get_creator_data(media_data)
    thumbnail = _get_thumbnail_url(media_data)
    metadata = _get_metadata(media_data)
    tags = _get_tags(media_data)
    # Jamendo has only music
    category = "music"
    # We request mp32 (VBR) files
    filetype = "mp32"
    genres = _get_genres(media_data)
    (
        set_foreign_id,
        audio_set,
        position,
        url,
        set_thumbnail,
    ) = _get_audio_set_info(media_data)
    return {
        "title": title,
        "creator": creator,
        "creator_url": creator_url,
        "foreign_identifier": foreign_identifier,
        "foreign_landing_url": foreign_landing_url,
        "audio_url": audio_url,
        "duration": duration,
        "filetype": filetype,
        "thumbnail_url": thumbnail,
        "license_info": item_license,
        "meta_data": metadata,
        "raw_tags": tags,
        "category": category,
        "genres": genres,
        "set_foreign_id": set_foreign_id,
        "audio_set": audio_set,
        "set_position": position,
        "set_url": url,
        "set_thumbnail": set_thumbnail,
    }


def _get_foreign_identifier(media_data):
    try:
        return media_data["id"]
    except (TypeError, IndexError, KeyError):
        return None


def _get_audio_info(media_data):
    """Parses audio URL, audio download URL, audio duration
    If the audio does not allow download, we save the 'streaming'
    URL as the `audio_url`
    :return: Tuple with main audio file information:
    - audio_url
    - download_url
    - duration (in milliseconds)
    """
    audio_url = media_data.get("audio")
    download_url = None
    if media_data.get("audiodownload_allowed") and media_data.get("audiodownload"):
        audio_url = media_data.get("audiodownload")
        download_url = media_data.get("audiodownload")
    duration = media_data.get("duration")
    if duration:
        duration = int(duration) * 1000
    return audio_url, duration, download_url


def _remove_trackid(thumbnail_url: Optional[str]):
    """
    ``audio_set`` data is used to create a separate database table in the API.
    To make sure that any given ``audio_set`` appears in that table only once,
    all the fields for that ``audio_set`` need to have the same values. In
    Jamendo, the ``audio_set`` thumbnail has a ``trackid`` query parameter,
    which breaks this rule.

    This function removes the ``trackid`` query parameter from the URL to make
    all thumbnail values identical for an audio set.
    >>> base_url = "https://usercontent.jamendo.com"
    >>> url = f"{base_url}?type=album&id=119&width=200&trackid=732"
    >>> _remove_trackid(url)
    'https://usercontent.jamendo.com?type=album&id=119&width=200'
    """
    if thumbnail_url is None:
        return
    parsed_url = urlsplit(thumbnail_url)
    query = parse_qs(parsed_url.query)
    query.pop("trackid", None)
    return parsed_url._replace(query=urlencode(query, doseq=True)).geturl()


def _get_audio_set_info(media_data):
    url = None
    base_url = "https://www.jamendo.com/album/"
    audio_set = media_data.get("album_name")
    position = media_data.get("position")
    thumbnail = _remove_trackid(media_data.get("album_image"))
    set_id = media_data.get("album_id")
    if set_id and audio_set:
        set_slug = (
            audio_set.lower().replace(" ", "-").replace("/", "-").replace("--", "")
        )
        url = _cleanse_url(f"{base_url}{set_id}/{set_slug}")
    return set_id, audio_set, position, url, thumbnail


def _get_thumbnail_url(media_data):
    return media_data.get("image")


def _get_creator_data(item):
    base_url = "https://www.jamendo.com/artist/"
    creator_name = item.get("artist_name")
    if creator_name is None:
        return None, None
    creator_id = item.get("artist_id")
    creator_idstr = item.get("artist_idstr")
    if creator_id is not None and creator_idstr is not None:
        creator_url = f"{base_url}{creator_id}/{creator_idstr}"
    else:
        creator_url = None
    return creator_name.strip(), creator_url


def _get_title(item):
    return item.get("name")


def _get_metadata(item):
    metadata = {}
    lyrics = item.get("lyrics")
    if lyrics:
        metadata["lyrics"] = lyrics
    downloads_count = item.get("stats", {}).get("rate_download_total", 0)
    listens_count = item.get("stats", {}).get("rate_listened_total", 0)
    playlists_count = item.get("stats", {}).get("rate_playlisted_total", 0)
    release_date = item.get("releasedate")
    if release_date is not None:
        metadata["release_date"] = release_date
    metadata["downloads"] = downloads_count
    metadata["listens"] = listens_count
    metadata["playlists"] = playlists_count
    return metadata


def _get_tags(item):
    # vocal/instrumental
    # genre
    # instruments
    tags = []
    musicinfo = item.get("musicinfo")
    if musicinfo:
        music_type = musicinfo.get("vocalinstrumental")
        if music_type:
            tags.append(music_type)
        music_gender = musicinfo.get("gender")
        if music_gender:
            tags.append(music_gender)
        music_speed = musicinfo.get("speed")
        if music_speed:
            tags.append(f"speed_{music_speed}")
        for tag_name in ["instruments", "vartags"]:
            tag_value = musicinfo.get("tags", {}).get(tag_name)
            if tag_value:
                tag_value = [_ for _ in tag_value if _ != "undefined"]
                tags.extend(tag_value)
    return tags


def _get_genres(item):
    genres = item.get("musicinfo", {}).get("tags", {}).get("genres", None)
    return genres


def _get_license(item):
    item_license_url = item.get("license_ccurl")
    item_license = get_license_info(license_url=item_license_url)
    if item_license.license is None:
        return None
    return item_license


@lru_cache(maxsize=1024)
def _cleanse_url(url_string):
    """
    Check to make sure that a url is valid, and prepend a protocol if needed
    Used to create correct album url by getting a redirect for urls
    with special characters, eg `/album/139/nés-funky`
    """
    return rewrite_redirected_url(url_string)


if __name__ == "__main__":
    main()
