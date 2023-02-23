"""
Content Provider:       Flickr

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the images and the
                        respective meta-data.

Notes:                  https://www.flickr.com/help/terms/api
                        Rate limit: 3600 requests per hour.
"""

import argparse
import logging
from datetime import datetime, timedelta

import lxml.html as html
from airflow.exceptions import AirflowException
from airflow.models import Variable
from common import constants
from common.licenses import get_license_info
from common.loader import provider_details as prov
from common.loader.provider_details import ImageCategory
from providers.provider_api_scripts.time_delineated_provider_data_ingester import (
    TimeDelineatedProviderDataIngester,
)


logger = logging.getLogger(__name__)

LICENSE_INFO = {
    "1": ("by-nc-sa", "2.0"),
    "2": ("by-nc", "2.0"),
    "3": ("by-nc-nd", "2.0"),
    "4": ("by", "2.0"),
    "5": ("by-sa", "2.0"),
    "6": ("by-nd", "2.0"),
    "9": ("cc0", "1.0"),
    "10": ("pdm", "1.0"),
}


class FlickrDataIngester(TimeDelineatedProviderDataIngester):
    provider_string = prov.FLICKR_DEFAULT_PROVIDER
    sub_providers = prov.FLICKR_SUB_PROVIDERS
    photo_url_base = prov.FLICKR_PHOTO_URL_BASE

    providers = {"image": provider_string}
    endpoint = "https://api.flickr.com/services/rest"
    batch_limit = 500
    retries = 5

    max_records = 4_000
    division_threshold = 20_000
    min_divisions = 12
    max_divisions = 60
    # When we pull more records than the API reports, we don't want to raise an error
    # and halt ingestion. Instead, this DAG adds its own separate handling to cut off
    # ingestion when max_records is reached, and continue to the next time interval. See
    # https://github.com/WordPress/openverse-catalog/pull/995
    should_raise_error = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Because `ingest_records` is called multiple times, default query params
        # are built multiple times. Fetch keys and build parameters here so it
        # is done only once.
        self.api_key = Variable.get("API_KEY_FLICKR")
        self.license_param = ",".join(LICENSE_INFO.keys())

        # Keeps track of number of requests made, so we can see how close we are
        # to hitting rate limits.
        self.requests_count = 0

    def get_next_query_params(self, prev_query_params, **kwargs):
        if not prev_query_params:
            # Initial request, return default params
            start_timestamp = kwargs.get("start_ts")
            end_timestamp = kwargs.get("end_ts")

            return {
                "min_upload_date": start_timestamp,
                "max_upload_date": end_timestamp,
                "page": 0,
                "api_key": self.api_key,
                "license": self.license_param,
                "per_page": self.batch_limit,
                "method": "flickr.photos.search",
                "media": "photos",
                "safe_search": 1,  # Restrict to 'safe'
                "extras": ",".join(
                    [
                        "description",
                        "license",
                        "date_upload",
                        "date_taken",
                        "owner_name",
                        "tags",
                        "o_dims",
                        "url_t",
                        "url_s",
                        "url_m",
                        "url_l",
                        "views",
                        "content_type",
                    ]
                ),
                "format": "json",
                "nojsoncallback": 1,
            }
        else:
            # Increment the page number on subsequent requests
            return {**prev_query_params, "page": prev_query_params["page"] + 1}

    def get_media_type(self, record):
        # We only ingest images from Flickr
        return constants.IMAGE

    def get_batch_data(self, response_json):
        # Keep track of the number of requests we've made, and log every 100
        self.requests_count += 1
        if self.requests_count % 100 == 0:
            logger.debug(f"{self.requests_count} requests have been made.")

        if response_json is None or response_json.get("stat") != "ok":
            return None
        return response_json.get("photos", {}).get("photo")

    def get_record_count_from_response(self, response_json) -> int:
        if response_json:
            count = response_json.get("photos", {}).get("total", 0)
            return int(count)
        return 0

    def get_record_data(self, data):
        if (license_info := self._get_license_info(data)) is None:
            return None

        image_size = self._get_largest_image_size(data)
        if (image_url := data.get(f"url_{image_size}")) is None:
            return None

        if (foreign_id := data.get("id")) is None:
            return None

        if (owner := data.get("owner")) is None:
            # Owner is needed to construct the foreign_landing_url, which is
            # a required field
            return None

        creator_url = self._url_join(self.photo_url_base, owner.strip())
        foreign_landing_url = self._url_join(creator_url, foreign_id)

        # Optional fields
        height = data.get(f"height_{image_size}")
        width = data.get(f"width_{image_size}")
        title = data.get("title")
        creator = data.get("ownername")
        category = self._get_category(data)
        meta_data = self._create_meta_data_dict(data)
        raw_tags = self._create_tags_list(data)
        # Flickr includes a collection of sub-providers which are available to a wide
        # audience. If this record belongs to a known sub-provider, we should indicate
        # that as the source. If not we fall back to the default provider.
        source = next(
            (s for s in self.sub_providers if owner in self.sub_providers[s]),
            self.provider_string,
        )

        return {
            "foreign_landing_url": foreign_landing_url,
            "image_url": image_url,
            "license_info": license_info,
            "foreign_identifier": foreign_id,
            "width": width,
            "height": height,
            "creator": creator,
            "creator_url": creator_url,
            "title": title,
            "meta_data": meta_data,
            "raw_tags": raw_tags,
            "source": source,
            "category": category,
        }

    def _url_join(self, *args):
        return "/".join([s.strip("/") for s in args])

    @staticmethod
    def _get_largest_image_size(image_data):
        """Return the key for the largest image size available."""
        for size in ["l", "m", "s"]:
            if f"url_{size}" in image_data:
                return size

        logger.warning("No image detected!")
        return None

    @staticmethod
    def _get_license_info(image_data):
        license_id = str(image_data.get("license"))
        if license_id not in LICENSE_INFO:
            logger.warning(f"Unknown license ID: {license_id}")
            return None

        license_, license_version = LICENSE_INFO.get(license_id)
        return get_license_info(license_=license_, license_version=license_version)

    @staticmethod
    def _create_meta_data_dict(image_data, max_description_length=2000):
        meta_data = {
            "pub_date": image_data.get("dateupload"),
            "date_taken": image_data.get("datetaken"),
            "views": image_data.get("views"),
        }
        description = image_data.get("description", {}).get("_content", "")
        if description.strip():
            try:
                description_text = " ".join(
                    html.fromstring(description).xpath("//text()")
                ).strip()[:max_description_length]
                meta_data["description"] = description_text
            except (TypeError, ValueError, IndexError) as e:
                logger.warning(f"Could not parse description {description}!\n{e}")

        return {k: v for k, v in meta_data.items() if v is not None}

    @staticmethod
    def _create_tags_list(image_data, max_tag_string_length=2000):
        raw_tags = None
        # We limit the input tag string length, not the number of tags,
        # since tags could otherwise be arbitrarily long, resulting in
        # arbitrarily large data in the DB.
        raw_tag_string = image_data.get("tags", "").strip()[:max_tag_string_length]
        if raw_tag_string:
            # We sort for further consistency between runs, saving on
            # inserts into the DB later.
            raw_tags = sorted(list(set(raw_tag_string.split())))
        return raw_tags

    @staticmethod
    def _get_category(image_data):
        """
        Get the category.

        Flickr has three types:
            0 for photos
            1 for screenshots
            3 for other
        Treating everything different from photos as unknown.
        """
        if "content_type" in image_data and image_data["content_type"] == "0":
            return ImageCategory.PHOTOGRAPH
        return None

    def get_should_continue(self, response_json):
        # Call the parent method in order to update the fetched_count
        should_continue = super().get_should_continue(response_json)

        # Return early if more than the max_records have been ingested.
        # This could happen if we did not break the ingestion down into
        # small enough divisions.
        if self.fetched_count > self.max_records:
            raise AirflowException(
                f"{self.fetched_count} records retrieved, but there is a"
                f" limit of {self.max_records}. Consider increasing the"
                " number of divisions."
            )

        return should_continue


def main(date):
    ingester = FlickrDataIngester(date=date)
    ingester.ingest_records()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flickr API Job", add_help=True)
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
