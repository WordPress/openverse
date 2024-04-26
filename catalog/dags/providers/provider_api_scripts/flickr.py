"""
Content Provider:       Flickr

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the images and the
                        respective meta-data.

Notes:                  <https://www.flickr.com/help/terms/api>

Rate limit:             3600 requests per hour.
"""

import argparse
import logging
from datetime import datetime, timedelta

import lxml.html as html
from airflow.models import Variable

from common.licenses import LicenseInfo, get_license_info
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

    # Flickr will return a maximum of 4,000 unique records per query. In practice,
    # we often see more records returned for a query than the given `resultCount`, so
    # we cap `max_records` artificially low to accommodate this.
    max_unique_records = 4_000  # Actual maximum, above which we should raise an error
    max_records = 3_000  # Attempt to break ingestion into time slices of this size
    division_threshold = 10_000
    min_divisions = 6
    max_divisions = 12
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
        self.default_license_param = ",".join(LICENSE_INFO.keys())

        # Keeps track of number of requests made, so we can see how close we are
        # to hitting rate limits.
        self.requests_count = 0

        # Keep track of batches containing more than the max_unique_records
        self.large_batches = []
        # When we encounter a batch containing more than the max_unique_records, we can
        # either return early without attempting to ingest records, or we can ingest up
        # to the max_unique_records count. This flag is used to control this behavior
        # during different stages of the ingestion process.
        self.process_large_batch = False

    def ingest_records(self, **kwargs):
        """
        Ingest records, handling large batches.

        The Flickr API returns a maximum of 4,000 unique records per query; after that,
        it returns only duplicates. Therefore in order to ingest as many unique records
        as possible, we must attempt to break ingestion into queries that contain fewer
        than the max_unique_records each.

        First, we use the TimeDelineatedProviderDataIngester to break queries down into
        smaller intervals of time throughout the ingestion day. However, this only has
        granularity down to about 5 minute intervals. If a 5-minute interval contains
        more than the max unique records, we then try splitting the interval up by
        license, making a separate query for each license type.

        If a 5-minute interval contains more than max_unique_records for a single
        license type, we accept that we cannot produce a query small enough to ingest
        all the unique records over this time period. We will process up to the
        max_unique_records count and then move on to the next batch.
        """
        # Perform full ingestion as normal, splitting requests into time-slices of at most
        # 5 minutes. When a batch is encountered which contains more than
        # max_unique_records, it is skipped and added to the `large_batches` list for
        # later processing.
        super().ingest_records(**kwargs)
        logger.info("Completed initial ingestion.")

        # If we encounter a large batch at this stage of ingestion, we cannot break
        # the batch down any further so we want to attempt to process as much as
        # possible.
        self.process_large_batch = True

        for start_ts, end_ts in self.large_batches:
            # For each large batch, ingest records for that interval one license
            # type at a time.
            for license_ in LICENSE_INFO.keys():
                super()._ingest_records(
                    initial_query_params=None,
                    fixed_query_params={
                        "min_upload_date": start_ts,
                        "max_upload_date": end_ts,
                        "license": license_,
                    },
                )
        logger.info("Completed large batch processing by license type.")

        # Report the final number of requests made. Because the Flickr DAG receives a
        # large amount of data, we can safely assume that we used the maximum of 25
        # additional requests when generating timestamp pairs.
        logger.info(f"Made {self.requests_count + 25} requests to the Flickr API.")

    def get_fixed_query_params(self):
        timestamp_pairs = super().get_fixed_query_params()
        return [
            {"min_upload_date": ts["start_ts"], "max_upload_date": ts["end_ts"]}
            for ts in timestamp_pairs
        ]

    def get_next_query_params(self, prev_query_params, **kwargs):
        if not prev_query_params:
            # Initial request, return default params
            start_timestamp = kwargs.get("start_ts")
            end_timestamp = kwargs.get("end_ts")

            # license will be available in the params if we're dealing
            # with a large batch. If not, fall back to all licenses
            license_ = kwargs.get("license", self.default_license_param)

            return {
                "min_upload_date": start_timestamp,
                "max_upload_date": end_timestamp,
                "page": 0,
                "api_key": self.api_key,
                "license": license_,
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

    def get_batch_data(self, response_json):
        self.requests_count += 1
        if response_json is None or response_json.get("stat") != "ok":
            return None

        # Detect if this batch has more than the max_unique_records.
        detected_count = self.get_record_count_from_response(response_json)
        if detected_count > self.max_unique_records:
            logger.error(
                f"{detected_count} records retrieved, but there is a"
                f" limit of {self.max_unique_records}."
            )

            if not self.process_large_batch:
                # We don't want to attempt to process this batch. Return an empty
                # batch now, and we will try again later, splitting the batch up by
                # license type.
                self.large_batches.append(self.current_timestamp_pair)
                return None

            # If we do want to process large batches, we should only ingest up to
            # the `max_unique_records` and then return early, as all records
            # retrieved afterward will be duplicates.
            page_number = response_json.get("photos", {}).get("page", 1)
            if self.batch_limit * page_number > self.max_unique_records:
                # We have already ingested up to `max_unique_records` for this
                # batch, so we should only be getting duplicates after this.
                return None

        # Return data for this batch
        return response_json.get("photos", {}).get("photo")

    def get_record_count_from_response(self, response_json) -> int:
        if response_json:
            count = response_json.get("photos", {}).get("total", 0)
            return int(count)
        return 0

    def get_record_data(self, data):
        if not (license_info := self._get_license_info(data)):
            return None

        image_size = self._get_largest_image_size(data)
        if not (url := data.get(f"url_{image_size}")):
            return None

        if not (foreign_identifier := data.get("id")):
            return None

        if not (owner := data.get("owner")):
            # Owner is needed to construct the foreign_landing_url, which is
            # a required field
            return None

        creator_url = self._url_join(self.photo_url_base, owner.strip())
        foreign_landing_url = self._url_join(creator_url, foreign_identifier)

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
            "url": url,
            "license_info": license_info,
            "foreign_identifier": foreign_identifier,
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
    def _get_license_info(image_data) -> LicenseInfo | None:
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
            raw_tags = raw_tag_string.split()
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
