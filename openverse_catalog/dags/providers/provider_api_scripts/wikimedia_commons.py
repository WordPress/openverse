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

import lxml.html as html
from common.constants import AUDIO, IMAGE
from common.licenses import get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)

# The 10000 is a bit arbitrary, but needs to be larger than the mean
# number of uses per file (globally) in the response_json, or we will
# fail without a continuation token.  The largest example seen so far
# had a little over 1000 uses
MEAN_GLOBAL_USAGE_LIMIT = 10000
HOST = "commons.wikimedia.org"
PAGES_PATH = ["query", "pages"]

IMAGE_MEDIATYPES = {"BITMAP", "DRAWING"}
AUDIO_MEDIATYPES = {"AUDIO"}
# Other types available in the API are OFFICE for pdfs and VIDEO


class WikimediaCommonsDataIngester(ProviderDataIngester):
    providers = {
        "image": prov.WIKIMEDIA_DEFAULT_PROVIDER,
        "audio": prov.WIKIMEDIA_AUDIO_PROVIDER,
    }
    endpoint = f"https://{HOST}/w/api.php"
    headers = {"User-Agent": prov.UA_STRING}

    # The batch_limit applies to the number of pages received by the API, rather
    # than the number of individual records. This means that for Wikimedia Commons
    # setting a global `INGESTION_LIMIT` will still limit the number of records, but
    # the exact limit may not be respected.
    batch_limit = 250

    def __init__(self, conf: dict = None, date: str | None = None):
        self.start_timestamp, self.end_timestamp = self.derive_timestamp_pair(date)
        self.continue_token = {}

        super().__init__(conf, date)

    def get_next_query_params(self, prev_query_params, **kwargs):
        return {
            "action": "query",
            "generator": "allimages",
            "gaisort": "timestamp",
            "gaidir": "newer",
            "gailimit": self.batch_limit,
            "prop": "imageinfo|globalusage",
            "iiprop": "url|user|dimensions|extmetadata|mediatype|size|metadata",
            "gulimit": self.batch_limit,
            "gunamespace": 0,
            "format": "json",
            "gaistart": self.start_timestamp,
            "gaiend": self.end_timestamp,
            **self.continue_token,
        }

    def get_media_type(self, record):
        """Get the media_type of a parsed Record"""
        return record["media_type"]

    def get_response_json(self, query_params):
        """
        Overrides the parent function to make multiple requests until
        we see "batchcomplete", rather than a single request to the
        endpoint. This ensures that global usage data used for calculating
        popularity is tabulated correctly.
        """
        batch_json = None

        for _ in range(MEAN_GLOBAL_USAGE_LIMIT):
            response_json = super().get_response_json(
                query_params,
                timeout=60,
            )

            if response_json is None:
                break
            else:
                # Update continue token for the next request
                self.continue_token = response_json.pop("continue", {})
                query_params.update(self.continue_token)
                logger.info(f"New continue token: {self.continue_token}")

                # Merge this response into the batch
                batch_json = self.merge_response_jsons(batch_json, response_json)

            if "batchcomplete" in response_json:
                logger.info("Found batchcomplete")
                break
        return batch_json

    def get_should_continue(self, response_json):
        # Should not continue if continue_token is Falsy
        return self.continue_token

    def get_batch_data(self, response_json):
        image_pages = self.get_media_pages(response_json)
        if image_pages is not None:
            return image_pages.values()
        return None

    def get_media_pages(self, response_json):
        if response_json is not None:
            image_pages = response_json.get("query", {}).get("pages")
            if image_pages is not None:
                logger.info(f"Got {len(image_pages)} pages")
                return image_pages

        logger.warning(f"No pages in the image batch: {response_json}")
        return None

    def get_record_data(self, record):
        foreign_id = record.get("pageid")
        logger.debug(f"Processing page ID: {foreign_id}")

        media_info = self.extract_media_info_dict(record)

        valid_media_type = self.extract_media_type(media_info)
        if not valid_media_type:
            # Do not process unsupported media types, like Video
            return None

        license_info = self.extract_license_info(media_info)
        if license_info.url is None:
            return None

        media_url = media_info.get("url")
        if media_url is None:
            return None

        creator, creator_url = self.extract_creator_info(media_info)
        title = self.extract_title(media_info)
        filesize = media_info.get("size", 0)  # in bytes
        filetype = self.extract_file_type(media_info)
        meta_data = self.create_meta_data_dict(record)

        record_data = {
            "media_url": media_url,
            "foreign_landing_url": media_info.get("descriptionshorturl"),
            "foreign_identifier": foreign_id,
            "license_info": license_info,
            "creator": creator,
            "creator_url": creator_url,
            "title": title,
            "filetype": filetype,
            "filesize": filesize,
            "meta_data": meta_data,
            "media_type": valid_media_type,
        }

        # Extend record_data with media-type specific fields
        funcs = {
            IMAGE: self.get_image_record_data,
            AUDIO: self.get_audio_record_data,
        }
        return funcs[valid_media_type](record_data, media_info)

    def get_image_record_data(self, record_data, media_info):
        """Extend record_data with image-specific fields"""
        record_data["image_url"] = record_data.pop("media_url")
        if record_data["filetype"] == "svg":
            record_data["category"] = "illustration"

        return {
            **record_data,
            "width": media_info.get("width"),
            "height": media_info.get("height"),
        }

    def get_audio_record_data(self, record_data, media_info):
        """Extend record_data with audio-specific fields"""
        record_data["audio_url"] = record_data.pop("media_url")

        duration = int(float(media_info.get("duration", 0)) * 1000)
        record_data["duration"] = duration
        record_data["category"] = self.extract_audio_category(record_data)

        file_metadata = self.parse_audio_file_meta_data(media_info)
        if sample_rate := self.get_value_by_names(
            file_metadata, ["audio_sample_rate", "sample_rate"]
        ):
            record_data["sample_rate"] = sample_rate
        if bit_rate := self.get_value_by_names(
            file_metadata, ["bitrate_nominal", "bitrate"]
        ):
            record_data["bit_rate"] = bit_rate if bit_rate <= 2147483647 else None
        if channels := self.get_value_by_names(
            file_metadata, ["audio_channels", "channels"]
        ):
            record_data["meta_data"]["channels"] = channels

        return record_data

    def parse_audio_file_meta_data(self, media_info):
        """Parse out audio file metadata"""
        metadata = media_info.get("metadata", [])

        streams = self.get_value_by_name(metadata, "streams")
        if not streams:
            audio = self.get_value_by_name(metadata, "audio")
            streams = self.get_value_by_name(audio, "streams")

        if streams:
            streams_data = streams[0].get("value", [])
            file_data = self.get_value_by_name(streams_data, "header")
            # Fall back to streams_data
            return file_data or streams_data

        return []

    @staticmethod
    def extract_media_info_dict(media_data):
        media_info_list = media_data.get("imageinfo")
        if media_info_list:
            media_info = media_info_list[0]
        else:
            media_info = {}
        return media_info

    @staticmethod
    def get_value_by_name(key_value_list: list, prop_name: str):
        """Gets the first value for the given `prop_name` in a list of
        key value pairs."""
        if key_value_list is None:
            key_value_list = []

        prop_list = [
            key_value_pair
            for key_value_pair in key_value_list
            if key_value_pair["name"] == prop_name
        ]
        if prop_list:
            return prop_list[0].get("value")

    @staticmethod
    def get_value_by_names(key_value_list: list, prop_names: list):
        """Gets the first available value for one of the `prop_names`
        property names"""
        for prop_name in prop_names:
            if val := WikimediaCommonsDataIngester.get_value_by_name(
                key_value_list, prop_name
            ):
                return val

    @staticmethod
    def extract_media_type(media_info):
        media_type = media_info.get("mediatype")

        if media_type in IMAGE_MEDIATYPES:
            return IMAGE
        elif media_type in AUDIO_MEDIATYPES:
            return AUDIO

        logger.info(
            f"Incorrect mediatype: {media_type} not in "
            f"valid mediatypes ({IMAGE_MEDIATYPES}, {AUDIO_MEDIATYPES})"
        )
        return None

    @staticmethod
    def extract_audio_category(parsed_data):
        """Set category to "pronunciation" for any audio with
        pronunciation of a word or a phrase"""
        for category in parsed_data["meta_data"].get("categories", []):
            if "pronunciation" in category.lower():
                return "pronunciation"

    @staticmethod
    def extract_ext_value(media_info: dict, ext_key: str) -> str | None:
        return media_info.get("extmetadata", {}).get(ext_key, {}).get("value")

    @staticmethod
    def extract_title(media_info):
        # Titles often have 'File:filename.jpg' form
        # We remove the 'File:' and extension from title
        title = WikimediaCommonsDataIngester.extract_ext_value(media_info, "ObjectName")
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

    @staticmethod
    def extract_date_info(media_info):
        date_originally_created = WikimediaCommonsDataIngester.extract_ext_value(
            media_info, "DateTimeOriginal"
        )
        last_modified_at_source = WikimediaCommonsDataIngester.extract_ext_value(
            media_info, "DateTime"
        )
        return date_originally_created, last_modified_at_source

    @staticmethod
    def extract_creator_info(media_info):
        artist_string = WikimediaCommonsDataIngester.extract_ext_value(
            media_info, "Artist"
        )

        if not artist_string:
            return None, None

        artist_elem = html.fromstring(artist_string)
        # We take all text to replicate what is shown on Wikimedia Commons
        artist_text = "".join(artist_elem.xpath("//text()")).strip()
        url_list = list(artist_elem.iterlinks())
        artist_url = url_list[0][2] if url_list else None
        return artist_text, artist_url

    @staticmethod
    def extract_category_info(media_info):
        categories_string = (
            WikimediaCommonsDataIngester.extract_ext_value(media_info, "Categories")
            or ""
        )

        categories_list = categories_string.split("|")
        return categories_list

    @staticmethod
    def extract_file_type(media_info):
        filetype = media_info.get("url", "").split(".")[-1]
        return None if filetype == "" else filetype

    @staticmethod
    def extract_license_info(media_info):
        license_url = (
            WikimediaCommonsDataIngester.extract_ext_value(media_info, "LicenseUrl")
            or ""
        )
        # TODO Add public domain items
        # if license_url == "":
        #     license_name = extract_ext_value(media_info, "LicenseShortName") or ""
        #     if license_name.lower() in {"public_domain", "pdm-owner"}:
        #         pass

        license_info = get_license_info(license_url=license_url.strip())
        return license_info

    @staticmethod
    def extract_geo_data(media_data):
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

    def create_meta_data_dict(self, media_data):
        global_usage_length = len(media_data.get("globalusage", []))
        media_info = self.extract_media_info_dict(media_data)
        date_originally_created, last_modified_at_source = self.extract_date_info(
            media_info
        )
        categories_list = self.extract_category_info(media_info)
        description = self.extract_ext_value(media_info, "ImageDescription")
        meta_data = {
            "global_usage_count": global_usage_length,
            "date_originally_created": date_originally_created,
            "last_modified_at_source": last_modified_at_source,
            "categories": categories_list,
            **self.extract_geo_data(media_data),
        }
        if description:
            description_text = " ".join(
                html.fromstring(description).xpath("//text()")
            ).strip()
            meta_data["description"] = description_text
        return meta_data

    def merge_response_jsons(self, left_json, right_json):
        # Note that we will keep the continue value from the right json in
        # the merged output!  This is because we assume the right json is
        # the later one in the sequence of responses.
        if left_json is None:
            return right_json

        left_pages = self.get_media_pages(left_json)
        right_pages = self.get_media_pages(right_json)

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
            merged_pages = self.get_media_pages(merged_json)
            merged_pages.update(
                {
                    k: self.merge_media_pages(left_pages[k], right_pages[k])
                    for k in left_pages
                }
            )

        return merged_json

    def merge_media_pages(self, left_page, right_page):
        merged_page = deepcopy(left_page)
        merged_globalusage = left_page.get("globalusage", []) + right_page.get(
            "globalusage", []
        )
        merged_page.update(right_page)
        merged_page["globalusage"] = merged_globalusage

        return merged_page

    def derive_timestamp_pair(self, date):
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        utc_date = date_obj.replace(tzinfo=timezone.utc)
        start_timestamp = str(int(utc_date.timestamp()))
        end_timestamp = str(int((utc_date + timedelta(days=1)).timestamp()))
        return start_timestamp, end_timestamp


def main(date):
    logger.info(f"Begin: Wikimedia Commons data ingestion for {date}")
    ingester = WikimediaCommonsDataIngester(date)
    ingester.ingest_records()


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
