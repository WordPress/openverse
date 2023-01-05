"""
Content Provider:       Science Museum

ETL Process:            Use the API to identify all CC-licensed images.

Output:                 TSV file containing the image, the respective
                        meta-data.

Notes:                  https://github.com/TheScienceMuseum/collectionsonline/wiki/Collections-Online-API  # noqa
                        Rate limited, no specific rate given.
"""
import logging
import re
from datetime import date

from common import slack
from common.licenses import get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)

LIMIT = 100

CC0_LICENSE = get_license_info(license_="cc0", license_version="1.0")


class ScienceMuseumDataIngester(ProviderDataIngester):
    providers = {"image": prov.SCIENCE_DEFAULT_PROVIDER}
    endpoint = "https://collection.sciencemuseumgroup.org.uk/search/"
    batch_limit = 1000
    delay = 5
    headers = {"Accept": "application/json"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # instance variable to prevent duplicate records
        self.RECORD_IDS = set()

        # track page number as instance variable so we can more
        # easily detect when the page limit is reached
        self.page_number = 0

    @staticmethod
    def _get_year_ranges(final_year: int) -> list[tuple[int, int]]:
        """
        The Science Museum API currently raises a 400 when attempting to access
        any page number higher than 50
        (https://github.com/TheScienceMuseum/collectionsonline/issues/1470).

        To avoid this, we ingest data for small ranges of years at a time,
        in order to split the data into batches less than 50 pages each.
        Because more recent data is more numerous, the length of the year
        ranges decreases as they get closer to the current day.
        """
        # Start with some very large ranges for old data
        year_ranges = [
            (0, 200),
            (200, 1500),
            (1500, 1750),
        ]
        # Add a range for every 25 years between 1750 and 1825
        year_ranges.extend([(x, x + 25) for x in range(1750, 1825, 25)])
        # Add a range for every 10 years between 1825 and 1925
        year_ranges.extend([(x, x + 10) for x in range(1825, 1925, 10)])
        # Add a range for every 5 years between 1925 and 'next year'
        # relative to when the DAG is being run.
        year_ranges.extend(
            [(x, min(x + 5, final_year)) for x in range(1925, final_year, 5)]
        )
        return year_ranges

    def ingest_records(self, **kwargs):
        next_year = date.today().year + 1
        for year_range in self._get_year_ranges(next_year):
            logger.info(f"==Starting on year range: {year_range}==")
            super().ingest_records(year_range=year_range)

    def get_next_query_params(self, prev_query_params, **kwargs):
        from_, to_ = kwargs["year_range"]
        if not prev_query_params:
            # Reset the page number to 0
            self.page_number = 0
        else:
            # Increment the page number
            self.page_number += 1

        return {
            "has_image": 1,
            "image_license": "CC",
            "page[size]": LIMIT,
            "page[number]": self.page_number,
            "date[from]": from_,
            "date[to]": to_,
        }

    def get_media_type(self, record):
        # This provider only supports Images.
        return "image"

    def get_batch_data(self, response_json):
        if response_json:
            return response_json.get("data")
        return None

    def get_record_data(self, record):
        id_ = record.get("id")
        if id_ in self.RECORD_IDS:
            return None
        self.RECORD_IDS.add(id_)
        foreign_landing_url = record.get("links", {}).get("self")
        if foreign_landing_url is None:
            return None
        attributes = record.get("attributes")
        if attributes is None:
            return None
        title = attributes.get("summary_title")
        creator = self._get_creator_info(attributes)

        metadata = self._get_metadata(attributes)
        multimedia = attributes.get("multimedia")
        if not multimedia:
            return None
        images = []
        for image_data in multimedia:
            foreign_id = image_data.get("admin", {}).get("uid")
            if foreign_id is None:
                continue
            processed = image_data.get("processed")
            (
                image_url,
                height,
                width,
                filetype,
            ) = self._get_image_info(processed)
            if image_url is None:
                continue

            license_pair = self._get_license(image_data)
            if license_pair is None:
                # some items do not return license anywhere, but in the UI
                # they look like CC
                continue
            license_, version = license_pair
            license_info = get_license_info(license_=license_, license_version=version)
            image = {
                "foreign_identifier": foreign_id,
                "foreign_landing_url": foreign_landing_url,
                "image_url": image_url,
                "height": height,
                "width": width,
                "filetype": filetype,
                "license_info": license_info,
                "creator": creator,
                "title": title,
                "meta_data": metadata,
            }
            images.append(image)
        return images

    @staticmethod
    def _get_creator_info(attributes):
        creator_info = None
        if (life_cycle := attributes.get("lifecycle")) is not None:
            creation = life_cycle.get("creation")
            if isinstance(creation, list):
                maker = creation[0].get("maker")
                if isinstance(maker, list):
                    creator_info = maker[0].get("summary_title")
        return creator_info

    @staticmethod
    def check_url(image_url: str | None) -> str | None:
        if not image_url:
            return None
        if image_url.startswith("http"):
            return image_url
        return f"https://coimages.sciencemuseumgroup.org.uk/images/{image_url}"

    @staticmethod
    def _get_dimensions(image_data: dict) -> tuple[int | None, int | None]:
        """
        Returns the height and width of the image from "image_data"."measurements"
        with keys of "dimension", "units", "value".
        """
        size = {}
        dimensions = image_data.get("measurements", {}).get("dimensions")
        if dimensions:
            for dim in dimensions:
                size[dim.get("dimension")] = (
                    dim.get("value") if dim.get("units") == "pixels" else None
                )
        return size.get("height"), size.get("width")

    @staticmethod
    def _get_image_info(
        processed: dict,
    ) -> tuple[str | None, int | None, int | None, str | None]:
        height, width, filetype = None, None, None
        image_data = processed.get("large")
        if image_data is None:
            image_data = processed.get("medium", {})

        image_url = ScienceMuseumDataIngester.check_url(image_data.get("location"))
        if image_url:
            filetype = image_data.get("format")
            height, width = ScienceMuseumDataIngester._get_dimensions(image_data)
        return image_url, height, width, filetype

    @staticmethod
    def _get_first_list_value(key: str, attributes: dict) -> str | None:
        val = attributes.get(key)
        if isinstance(val, list):
            return val[0].get("value")
        return None

    @staticmethod
    def _get_metadata(attributes):
        metadata = {}
        for attr_key, metadata_key in [
            ("identifier", "accession number"),
            ("name", "name"),
            ("categories", "category"),
            ("description", "description"),
        ]:
            val = ScienceMuseumDataIngester._get_first_list_value(attr_key, attributes)
            if val is not None:
                metadata[metadata_key] = val

        creditline = attributes.get("legal")
        if isinstance(creditline, dict):
            line = creditline.get("credit_line")
            if line is not None:
                metadata["creditline"] = line

        return metadata

    @staticmethod
    def _get_license(image_data) -> None | tuple[str, str]:
        rights = image_data.get("source", {}).get("legal", {}).get("rights")
        if isinstance(rights, list):
            license_name = rights[0].get("usage_terms")
            if not license_name:
                return None
            license_name = license_name.lower()
            license_name = re.sub("^cc[ -]", "", license_name)
            if license_name.count(" ") != 1:
                # Unidentifiable license
                return None
            license_, version = license_name.split(" ")
            return license_, version
        return None

    def get_should_continue(self, response_json) -> bool:
        next_page_url = response_json.get("links", {}).get("next")

        # No more data left to process
        if next_page_url is None:
            return False

        # Special case where we must halt ingestion early to prevent
        # external API errors caused by accessing a page number higher
        # than 50.
        if self.page_number == 50:
            current_url = response_json.get("links", {}).get("self")
            message = (
                f"Request {current_url} contains more than 50 pages of"
                " data and cannot be fully ingested. Reduce the size of"
                " the year range in order to complete ingestion."
            )
            slack.send_alert(message, dag_id=self.dag_id)
            return False

        return True


def main():
    ingester = ScienceMuseumDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
