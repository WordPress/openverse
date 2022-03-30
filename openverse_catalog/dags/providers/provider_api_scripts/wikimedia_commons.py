"""
Content Provider:       Wikimedia Commons

ETL Process:            Use the API to identify all CC-licensed images.

Output:                 TSV file containing the image, the respective
                        meta-data.

Notes:                  https://commons.wikimedia.org/wiki/API:Main_page
                        No rate limit specified.
"""

import argparse
import logging
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlparse

import lxml.html as html
from common.constants import AUDIO, IMAGE
from common.licenses import get_license_info
from common.loader import provider_details as prov
from common.requester import DelayedRequester
from common.storage.audio import AudioStore
from common.storage.image import ImageStore


logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)

LIMIT = 250
# The 10000 is a bit arbitrary, but needs to be larger than the mean
# number of uses per file (globally) in the response_json, or we will
# fail without a continuation token.  The largest example seen so far
# had a little over 1000 uses
MEAN_GLOBAL_USAGE_LIMIT = 10000
DELAY = 1
HOST = "commons.wikimedia.org"
ENDPOINT = f"https://{HOST}/w/api.php"
PROVIDER = prov.WIKIMEDIA_DEFAULT_PROVIDER
AUDIO_PROVIDER = prov.WIKIMEDIA_AUDIO_PROVIDER
DEFAULT_REQUEST_HEADERS = {"User-Agent": prov.UA_STRING}
DEFAULT_QUERY_PARAMS = {
    "action": "query",
    "generator": "allimages",
    "gaisort": "timestamp",
    "gaidir": "newer",
    "gailimit": LIMIT,
    "prop": "imageinfo|globalusage",
    "iiprop": "url|user|dimensions|extmetadata|mediatype|size|metadata",
    "gulimit": LIMIT,
    "gunamespace": 0,
    "format": "json",
}
PAGES_PATH = ["query", "pages"]
IMAGE_MEDIATYPES = {"BITMAP", "DRAWING"}
AUDIO_MEDIATYPES = {"AUDIO"}
# Other types available in the API are OFFICE for pdfs and VIDEO

delayed_requester = DelayedRequester(DELAY)
audio_store = AudioStore(provider=AUDIO_PROVIDER)
image_store = ImageStore(provider=PROVIDER)


def main(date):
    """
    This script pulls the data for a given date from the Wikimedia
    Commons API, and writes it into a .TSV file to be eventually read
    into our DB.

    Required Arguments:

    date:  Date String in the form YYYY-MM-DD.  This is the date for
           which running the script will pull data.
    """

    logger.info(f"Processing Wikimedia Commons API for date: {date}")

    continue_token = {}
    total_audio = 0
    total_images = 0
    start_timestamp, end_timestamp = _derive_timestamp_pair(date)

    while True:
        media_batch, continue_token = _get_media_batch(
            start_timestamp, end_timestamp, continue_token=continue_token
        )
        logger.info(f"Continue Token: {continue_token}")
        image_pages = _get_image_pages(media_batch)
        if image_pages:
            _process_image_pages(image_pages)
            total_images = image_store.total_items
            total_audio = audio_store.total_items
        logger.info(f"Total: {total_images} images and {total_audio} audio so far")
        if not continue_token:
            break

    audio_store.commit()
    image_store.commit()
    logger.info(f"Total images: {image_store.total_items}")
    logger.info(f"Total audios: {audio_store.total_items}")
    logger.info("Terminated!")


def _derive_timestamp_pair(date):
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    utc_date = date_obj.replace(tzinfo=timezone.utc)
    start_timestamp = str(int(utc_date.timestamp()))
    end_timestamp = str(int((utc_date + timedelta(days=1)).timestamp()))
    return start_timestamp, end_timestamp


def _get_media_batch(start_timestamp, end_timestamp, continue_token=None, retries=5):
    if continue_token is None:
        continue_token = {}
    query_params = _build_query_params(
        start_timestamp, end_timestamp, continue_token=continue_token
    )
    image_batch = None
    new_continue_token = None
    for _ in range(MEAN_GLOBAL_USAGE_LIMIT):
        response_json = delayed_requester.get_response_json(
            ENDPOINT,
            retries=retries,
            query_params=query_params,
            headers=DEFAULT_REQUEST_HEADERS,
            timeout=60,
        )

        if response_json is None:
            break
        else:
            new_continue_token = response_json.pop("continue", {})
            logger.debug(f"new_continue_token: {new_continue_token}")
            query_params.update(new_continue_token)
            image_batch = _merge_response_jsons(image_batch, response_json)

        if "batchcomplete" in response_json:
            logger.debug("Found batchcomplete")
            break

    return image_batch, new_continue_token


def _get_image_pages(image_batch):
    image_pages = None

    if image_batch is not None:
        image_pages = image_batch.get("query", {}).get("pages")

    if image_pages is None:
        logger.warning(f"No pages in the image_batch: {image_batch}")
    else:
        logger.info(f"Got {len(image_pages)} pages")

    return image_pages


def _process_image_pages(image_pages):
    for i in image_pages.values():
        _process_media_data(i)


def _build_query_params(
    start_date,
    end_date,
    continue_token=None,
    default_query_params=None,
):
    if continue_token is None:
        continue_token = {}
    if default_query_params is None:
        default_query_params = DEFAULT_QUERY_PARAMS
    query_params = default_query_params.copy()
    query_params.update(
        gaistart=start_date,
        gaiend=end_date,
    )
    query_params.update(continue_token)
    return query_params


def _merge_response_jsons(left_json, right_json):
    # Note that we will keep the continue value from the right json in
    # the merged output!  This is because we assume the right json is
    # the later one in the sequence of responses.
    if left_json is None:
        return right_json

    left_pages = _get_image_pages(left_json)
    right_pages = _get_image_pages(right_json)

    if (
        left_pages is None
        or right_pages is None
        or left_pages.keys() != right_pages.keys()
    ):
        logger.warning("Cannot merge responses with different pages!")
        merged_json = None
    else:
        merged_json = deepcopy(left_json)
        merged_json.update(right_json)
        merged_pages = _get_image_pages(merged_json)
        merged_pages.update(
            {k: _merge_image_pages(left_pages[k], right_pages[k]) for k in left_pages}
        )

    return merged_json


def _merge_image_pages(left_page, right_page):
    merged_page = deepcopy(left_page)
    merged_globalusage = left_page.get("globalusage", []) + right_page.get(
        "globalusage", []
    )
    merged_page.update(right_page)
    merged_page["globalusage"] = merged_globalusage

    return merged_page


def _extract_file_type(media_info):
    filetype = media_info.get("url", "").split(".")[-1]
    return None if filetype == "" else filetype


def _process_media_data(media_data):
    foreign_id = media_data.get("pageid")
    logger.debug(f"Processing page ID: {foreign_id}")
    media_info = _get_image_info_dict(media_data)
    valid_mediatype = _check_mediatype(media_info)
    if not valid_mediatype:
        return None
    license_info = _get_license_info(media_info)
    if license_info.url is None:
        return None
    media_url = media_info.get("url")
    if media_url is None:
        return None
    creator, creator_url = _extract_creator_info(media_info)
    title = _extract_title(media_info)
    filesize = media_info.get("size", 0)  # in bytes
    filetype = _extract_file_type(media_info)
    parsed_data = {
        "media_url": media_url,
        "foreign_landing_url": media_info.get("descriptionshorturl"),
        "foreign_identifier": foreign_id,
        "license_info": license_info,
        "creator": creator,
        "creator_url": creator_url,
        "title": title,
        "filetype": filetype,
        "filesize": filesize,
    }

    funcs = {
        IMAGE: _add_image,
        AUDIO: _add_audio,
    }
    funcs[valid_mediatype](parsed_data, media_data, media_info)


def _get_value_by_name(key_value_list: list, prop_name: str):
    prop_list = [
        key_value_pair
        for key_value_pair in key_value_list
        if key_value_pair["name"] == prop_name
    ]
    if prop_list:
        return prop_list[0].get("value")


def _get_value_by_names(key_value_list: list, prop_names: list):
    """Gets the first available value for one of the `prop_names`
    property names"""
    for prop_name in prop_names:
        if val := _get_value_by_name(key_value_list, prop_name):
            return val


def _parse_audio_file_data(parsed_data: dict, file_metadata: list) -> dict:
    streams = _get_value_by_name(file_metadata, "streams")
    try:
        if not streams:
            audio = _get_value_by_name(file_metadata, "audio")
            streams = _get_value_by_name(audio, "streams")
        streams_data = [stream["value"] for stream in streams][0]
        file_data = _get_value_by_name(streams_data, "header")
        if not file_data:
            file_data = streams_data
    except (IndexError, TypeError):
        file_data = []
    if sample_rate := _get_value_by_names(
        file_data, ["audio_sample_rate", "sample_rate"]
    ):
        parsed_data["sample_rate"] = sample_rate
    if bit_rate := _get_value_by_names(file_data, ["bitrate_nominal", "bitrate"]):
        parsed_data["bit_rate"] = bit_rate
    if channels := _get_value_by_names(file_data, ["audio_channels", "channels"]):
        parsed_data["meta_data"]["channels"] = channels
    return parsed_data


def _extract_audio_category(parsed_data):
    """Set category to "pronunciation" for any audio with
    pronunciation of a word or a phrase"""
    for category in parsed_data["meta_data"].get("categories", []):
        if "pronunciation" in category.lower():
            return "pronunciation"


def _add_audio(parsed_data, media_data, media_info):
    # Converting duration into milliseconds
    duration = int(float(media_info.get("duration", 0)) * 1000)
    parsed_data["audio_url"] = parsed_data.pop("media_url")
    parsed_data["duration"] = duration
    parsed_data["meta_data"] = _create_meta_data_dict(media_data)
    if not parsed_data.get("category"):
        parsed_data["category"] = _extract_audio_category(parsed_data)
    file_metadata: list = media_info.get("metadata", [])
    parsed_data = _parse_audio_file_data(parsed_data, file_metadata)
    audio_store.add_item(**parsed_data)


def _add_image(parsed_data, media_data, media_info):
    parsed_data["meta_data"] = _create_meta_data_dict(media_data)
    parsed_data["width"] = media_info.get("width")
    parsed_data["height"] = media_info.get("height")
    parsed_data["image_url"] = parsed_data.pop("media_url")
    if parsed_data["filetype"] == "svg":
        parsed_data["category"] = "illustration"
    image_store.add_item(**parsed_data)


def _get_image_info_dict(media_data):
    media_info_list = media_data.get("imageinfo")
    if media_info_list:
        media_info = media_info_list[0]
    else:
        media_info = {}
    return media_info


def _check_mediatype(media_info):
    item_mediatype = media_info.get("mediatype")
    if item_mediatype in IMAGE_MEDIATYPES:
        return IMAGE
    elif item_mediatype in AUDIO_MEDIATYPES:
        return AUDIO
    else:
        logger.debug(
            f"Incorrect mediatype: {item_mediatype} not in "
            f"valid mediatypes ({IMAGE_MEDIATYPES}, {AUDIO_MEDIATYPES})"
        )
        return None


def _extract_title(media_info):
    # Titles often have 'File:filename.jpg' form
    # We remove the 'File:' and extension from title
    title = _get_ext_value(media_info, "ObjectName")
    if title is None:
        title = media_info.get("title")
    if title.startswith("File:"):
        title = title.replace("File:", "", 1)
    last_dot_position = title.rfind(".")
    if last_dot_position > 0:
        possible_extension = title[last_dot_position:]
        if possible_extension.lower() in {".png", ".jpg", ".jpeg", ".ogg", ".wav"}:
            title = title[:last_dot_position]
    return title


def _extract_date_info(media_info):
    date_originally_created = _get_ext_value(media_info, "DateTimeOriginal")
    last_modified_at_source = _get_ext_value(media_info, "DateTime")
    return date_originally_created, last_modified_at_source


def _extract_creator_info(media_info):
    artist_string = _get_ext_value(media_info, "Artist")

    if not artist_string:
        return None, None

    artist_elem = html.fromstring(artist_string)
    # We take all text to replicate what is shown on Wikimedia Commons
    artist_text = "".join(artist_elem.xpath("//text()")).strip()
    url_list = list(artist_elem.iterlinks())
    artist_url = _cleanse_url(url_list[0][2]) if url_list else None
    return artist_text, artist_url


def _extract_category_info(media_info):
    categories_string = _get_ext_value(media_info, "Categories") or ""

    categories_list = categories_string.split("|")
    return categories_list


def _get_license_info(media_info):
    license_url = _get_ext_value(media_info, "LicenseUrl") or ""
    # TODO Add public domain items
    # if license_url == "":
    #     license_name = _get_ext_value(media_info, "LicenseShortName") or ""
    #     if license_name.lower() in {"public_domain", "pdm-owner"}:
    #         pass

    license_info = get_license_info(license_url=license_url.strip())
    return license_info


def _get_geo_data(media_data):
    geo_properties = {
        "latitude": "GPSLatitude",
        "longitude": "GPSLongitude",
        "map_datum": "GPSMapDatum",
    }
    geo_data = {}
    for (key, value) in geo_properties.items():
        key_value = media_data.get(value, {}).get("value")
        if key_value:
            geo_data[key] = key_value
    return geo_data


def _create_meta_data_dict(media_data):
    meta_data = {}
    global_usage_length = len(media_data.get("globalusage", []))
    media_info = _get_image_info_dict(media_data)
    date_originally_created, last_modified_at_source = _extract_date_info(media_info)
    categories_list = _extract_category_info(media_info)
    description = _get_ext_value(media_info, "ImageDescription")
    if description:
        description_text = " ".join(
            html.fromstring(description).xpath("//text()")
        ).strip()
        meta_data["description"] = description_text
    meta_data["global_usage_count"] = global_usage_length
    meta_data["date_originally_created"] = date_originally_created
    meta_data["last_modified_at_source"] = last_modified_at_source
    meta_data["categories"] = categories_list
    meta_data.update(_get_geo_data(media_data))
    return meta_data


def _cleanse_url(url_string):
    """
    Check to make sure that a url is valid, and prepend a protocol if needed
    """

    parse_result = urlparse(url_string)

    if parse_result.netloc == HOST:
        parse_result = urlparse(url_string, scheme="https")
    elif not parse_result.scheme:
        parse_result = urlparse(url_string, scheme="http")

    if parse_result.netloc or parse_result.path:
        return parse_result.geturl()


def _get_ext_value(media_info: dict, ext_key: str) -> Optional[str]:
    return media_info.get("extmetadata", {}).get(ext_key, {}).get("value")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Wikimedia Commons API Job",
        add_help=True,
    )
    parser.add_argument(
        "--date", help="Identify images uploaded on a date (format: YYYY-MM-DD)."
    )
    args = parser.parse_args()
    if args.date:
        date = args.date
    else:
        date_obj = datetime.now() - timedelta(days=2)
        date = datetime.strftime(date_obj, "%Y-%m-%d")

    main(date)
