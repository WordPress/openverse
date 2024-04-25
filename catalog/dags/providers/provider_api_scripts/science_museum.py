"""
Content Provider:       Science Museum

ETL Process:            Use the API to identify all CC-licensed images.

Output:                 TSV file containing the image, the respective
                        meta-data.

Notes:                  <https://github.com/TheScienceMuseum/collectionsonline/wiki/Collections-Online-API>
                        Rate limited, no specific rate given.
"""  # noqa: E501

import logging
import re
from datetime import date

from common import slack
from common.licenses import LicenseInfo, get_license_info
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
        Get the year ranges based on a final year.

        The Science Museum API currently raises a 400 when attempting to access
        any page number higher than 50
        (<https://github.com/TheScienceMuseum/collectionsonline/issues/1470>).

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
        return [{"date[from]": from_, "date[to]": to_} for from_, to_ in year_ranges]

    def get_fixed_query_params(self):
        """
        Provide a set of year ranges. Ingestion will be performed for each range,
        with the dates set as fixed query params.
        """
        next_year = date.today().year + 1
        return self._get_year_ranges(next_year)

    def get_next_query_params(self, prev_query_params):
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
        }

    def get_batch_data(self, response_json):
        if response_json:
            return response_json.get("data")
        return None

    def get_record_data(self, record):
        id_ = record.get("id")
        if id_ in self.RECORD_IDS:
            return None
        self.RECORD_IDS.add(id_)
        if not (foreign_landing_url := record.get("links", {}).get("self")):
            return None
        if not (attributes := record.get("attributes")) or not (
            multimedia := attributes.get("multimedia")
        ):
            return None

        title = ScienceMuseumDataIngester._get_first_list_value("title", attributes)
        creator = self._get_creator_info(attributes)
        metadata = self._get_metadata(attributes)
        images = []
        for image_data in multimedia:
            if not (foreign_identifier := image_data.get("@admin", {}).get("uid")):
                continue
            processed = image_data.get("@processed")
            if not isinstance(processed, dict):
                continue
            (
                url,
                height,
                width,
                filetype,
                filesize,
            ) = self._get_image_info(processed)
            if not url:
                continue

            if not (license_info := self._get_license_info(image_data)):
                continue

            image = {
                "foreign_identifier": foreign_identifier,
                "foreign_landing_url": foreign_landing_url,
                "url": url,
                "height": height,
                "width": width,
                "filetype": filetype,
                "filesize": filesize,
                "license_info": license_info,
                "creator": creator,
                "title": title,
                "meta_data": metadata,
            }
            images.append(image)
        return images

    @staticmethod
    def _get_creator_info(attributes):
        if not (maker := attributes.get("creation", {}).get("maker", [])):
            return None

        return maker[0].get("summary", {}).get("title", None)

    @staticmethod
    def check_url(url: str | None) -> str | None:
        if not url:
            return None
        if url.startswith("http"):
            return url
        return f"https://coimages.sciencemuseumgroup.org.uk/{url}"

    @staticmethod
    def _get_dimensions(image_data: dict) -> tuple[int | None, int | None]:
        """
        Return the height and width of the image.

        Uses the values from "image_data"."measurements" with keys of "dimension",
        "units", "value".
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
    ) -> tuple[str | None, int | None, int | None, str | None, int | None]:
        height, width, filetype, filesize = None, None, None, None
        image_data = processed.get("large") or processed.get("medium", {})

        url = ScienceMuseumDataIngester.check_url(image_data.get("location"))
        if url:
            filetype = image_data.get("format")
            height, width = ScienceMuseumDataIngester._get_dimensions(image_data)

            if not (
                filesize := int(
                    image_data.get("measurements", {})
                    .get("filesize", {})
                    .get("value", 0)
                )
            ):
                filesize = None

        return url, height, width, filetype, filesize

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
            ("category", "category"),
            ("description", "description"),
        ]:
            val = ScienceMuseumDataIngester._get_first_list_value(attr_key, attributes)
            if val is not None:
                metadata[metadata_key] = val

        creditline = attributes.get("legal")
        if isinstance(creditline, dict):
            line = creditline.get("credit")
            if line is not None:
                metadata["creditline"] = line

        return metadata

    @staticmethod
    def _get_license_info(image_data) -> LicenseInfo | None:
        # some items do not return license anywhere, but in the UI
        # they look like CC
        rights = image_data.get("legal", {}).get("rights")
        if isinstance(rights, list):
            license_name = rights[0].get("licence")
            if not license_name:
                return None
            license_name = license_name.lower()
            license_name = re.sub("^cc[ -]", "", license_name)
            if license_name.count(" ") != 1:
                # Unidentifiable license
                return None
            license_, version = license_name.split(" ")
            return get_license_info(license_=license_, license_version=version)
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
