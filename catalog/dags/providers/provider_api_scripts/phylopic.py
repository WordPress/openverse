"""
Content Provider:       PhyloPic

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the image,
                        their respective meta-data.

Notes:                  http://api-docs.phylopic.org/v2/
                        No rate limit specified.
"""

import logging

from common import constants
from common.licenses import get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)


class PhylopicDataIngester(ProviderDataIngester):
    delay = 5
    host = "https://www.phylopic.org"
    endpoint = "https://api.phylopic.org/images"
    providers = {constants.IMAGE: prov.PHYLOPIC_DEFAULT_PROVIDER}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_page = 1
        self.total_pages = 0
        self.build_param = 0

    def ingest_records(self):
        self._get_initial_query_params()
        super().ingest_records()

    def _get_initial_query_params(self) -> None:
        """Get the required `build` param from the API and set the total pages."""
        resp = self.get_response_json(query_params={})
        if not resp:
            raise Exception("No response from Phylopic API.")
        self.build_param = resp.get("build")
        self.total_pages = resp.get("totalPages")
        logger.info(
            f"Total items to fetch: {resp.get('totalItems')}. "
            f"Total pages: {self.total_pages}."
        )

    def get_next_query_params(self, prev_query_params: dict | None, **kwargs) -> dict:
        if prev_query_params is not None:
            self.current_page += 1

        return {
            "build": self.build_param,
            "page": self.current_page - 1,  # PhyloPic pages are 0-indexed.
            "embed_items": "true",
        }

    def get_should_continue(self, response_json):
        logger.debug(f"Processing page {self.current_page} of {self.total_pages}.")
        return self.current_page < self.total_pages

    def get_batch_data(self, response_json):
        return response_json.get("_embedded", {}).get("items", [])

    def _get_creator(self, data: dict) -> tuple[str | None, str | None]:
        creator_name = data.get("title")
        href = data.get("href")
        creator_url = self.host + href if href else None
        return creator_name, creator_url

    @staticmethod
    def _get_image_sizes(data: dict) -> tuple[int | None, int | None]:
        width, height = None, None
        sizes = data.get("sourceFile", {}).get("sizes")
        if sizes and "x" in sizes:
            width, height = sizes.split("x")
            # SVG sizes include decimal points so we get an approximation.
            width, height = int(float(width)), int(float(height))
        return width, height

    def get_record_data(self, data: dict) -> dict | list[dict] | None:
        """
        Get the data for a single image record.

        TODO: Adapt `url` and `creator_url` to avoid redirects.
        """

        if not (foreign_identifier := data.get("uuid")):
            return None

        links = data.get("_links", {})

        if not (url := links.get("sourceFile", {}).get("href")):
            return None

        if not (foreign_url_path := links.get("self", {}).get("href")):
            return None
        foreign_landing_url = self.host + foreign_url_path

        license_url = links.get("license", {}).get("href")
        if not (license_info := get_license_info(license_url)):
            return None

        title = data.get("self", {}).get("title")
        creator, creator_url = self._get_creator(data.get("contributor", {}))
        width, height = self._get_image_sizes(data)

        return {
            "license_info": license_info,
            "foreign_identifier": foreign_identifier,
            "foreign_landing_url": foreign_landing_url,
            "url": url,
            "title": title,
            "creator": creator,
            "creator_url": creator_url,
            "width": width,
            "height": height,
            # TODO: Evaluate whether to include upstream thumbnails.
            # Sizes available: 192x192, 128x128, 64x64.
            # "thumbnail": thumbnail,
            # TODO: Evaluate whether to include nodes' titles as tags.
            # "tags": tags,
        }


def main():
    logger.info("Begin: Phylopic provider script")
    ingester = PhylopicDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
