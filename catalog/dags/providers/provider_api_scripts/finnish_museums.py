"""
Content Provider:       Finnish Museums

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the images and the
                        respective meta-data.

Notes:                  https://api.finna.fi/swagger-ui/
                        https://www.finna.fi/Content/help-syntax?lng=en-gb
                        The Finnish Museums provider script is a dated DAG that
                        ingests all records that were last updated in the previous
                        day. Because of this, it is not necessary to run a separate
                        reingestion DAG, as updated data will be processed during
                        regular ingestion.
"""

import logging
from itertools import chain

from common.licenses import LicenseInfo, get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.time_delineated_provider_data_ingester import (
    TimeDelineatedProviderDataIngester,
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

API_URL = "https://api.finna.fi"
LANDING_URL = "https://www.finna.fi/Record/"

PROVIDER = prov.FINNISH_DEFAULT_PROVIDER
SUB_PROVIDERS = prov.FINNISH_SUB_PROVIDERS


class FinnishMuseumsDataIngester(TimeDelineatedProviderDataIngester):
    providers = {"image": PROVIDER}
    endpoint = "https://api.finna.fi/api/v1/search"
    batch_limit = 100
    delay = 5
    format_type = "0/Image/"
    buildings = [
        "0/Suomen kansallismuseo/",
        "0/Museovirasto/",
        "0/SATMUSEO/",
        "0/SA-kuva/",
    ]
    max_records = 10_000
    division_threshold = 100_000
    min_divisions = 12
    max_divisions = 20

    def ingest_records(self, **kwargs):
        for building in self.buildings:
            logger.info(f"Obtaining images of building {building}")
            super().ingest_records(building=building)

    def get_next_query_params(self, prev_query_params, **kwargs):
        if not prev_query_params:
            building = kwargs.get("building")
            start_ts = self.format_ts(kwargs.get("start_ts"))
            end_ts = self.format_ts(kwargs.get("end_ts"))

            return {
                "filter[]": [
                    f'format:"{self.format_type}"',
                    f'building:"{building}"',
                    f'last_indexed:"[{start_ts} TO {end_ts}]"',
                ],
                "field[]": [
                    "authors",
                    "buildings",
                    "id",
                    "imageRights",
                    "images",
                    "subjects",
                    "title",
                ],
                "limit": self.batch_limit,
                "page": 1,
            }
        return {**prev_query_params, "page": prev_query_params["page"] + 1}

    def get_record_count_from_response(self, response_json):
        if response_json:
            return response_json.get("resultCount", 0)
        return 0

    def get_batch_data(self, response_json):
        if (
            not response_json
            or str(response_json.get("status")).lower() != "ok"
            or not response_json.get("records")
        ):
            return None

        return response_json["records"]

    def get_record_data(self, data):
        if not (license_info := self.get_license_info(data)):
            return None

        if not (foreign_identifier := data.get("id")):
            return None
        foreign_landing_url = LANDING_URL + foreign_identifier

        if not (image_list := data.get("images")):
            return None

        title = data.get("title")
        creator = self.get_creator(data.get("authors")) if data.get("authors") else None
        building = data.get("buildings")[0].get("value")
        source = next(
            (s for s in SUB_PROVIDERS if building in SUB_PROVIDERS[s]), PROVIDER
        )

        raw_tags = None
        if tag_lists := data.get("subjects"):
            raw_tags = list(chain(*tag_lists))

        records = []
        for img in image_list:
            if not (image_url := self._get_image_url(img)):
                continue
            records.append(
                {
                    "license_info": license_info,
                    "foreign_identifier": foreign_identifier,
                    "foreign_landing_url": foreign_landing_url,
                    "url": image_url,
                    "title": title,
                    "source": source,
                    "creator": creator,
                    "raw_tags": raw_tags,
                }
            )
        return records

    @staticmethod
    def get_license_info(obj) -> LicenseInfo | None:
        if not (license_url := obj.get("imageRights", {}).get("link")):
            return None

        # The API returns urls linking to the Finnish version of the license deed,
        # (eg `licenses/by/4.0/deed.fi`), but the license validation logic expects
        # links to the license page (eg `license/by/4.0`).
        return get_license_info(license_url=license_url.removesuffix("deed.fi"))

    @staticmethod
    def _get_image_url(img, image_url=API_URL) -> str | None:
        if not img:
            return None
        return image_url + img

    @staticmethod
    def get_creator(authors_raw) -> str | None:
        authors = []
        for author_type in ["primary", "secondary", "corporate"]:
            author = authors_raw.get(author_type)
            if not isinstance(author, dict):
                continue
            author = "; ".join(list(author.keys()))
            authors.append(author)

        return "; ".join(authors) or None


def main():
    ingester = FinnishMuseumsDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
