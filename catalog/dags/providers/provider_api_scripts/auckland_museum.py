"""
Content Provider:       Auckland War Memorial Museum Tāmaki Paenga Hira

ETL Process:            Use the API to identify all CC licensed media.

Output:                 TSV file containing the media and the
                        respective meta-data.

Notes:                  https://api.aucklandmuseum.com/

Resource:               https://api.aucklandmuseum.com/
                        https://github.com/AucklandMuseum/API/wiki/Tutorial

Resource | Requests per second | Requests per day
-- | -- | --
/search, /id | 10 | 1000
/id/media | 10 | 1000
"""

import logging
from datetime import datetime, timedelta

from common.constants import IMAGE
from common.licenses import get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)

LANDING_URL = (
    "https://www.aucklandmuseum.com/collections-research/collections/record/am_"
)


class AucklandMuseumDataIngester(ProviderDataIngester):
    providers = {
        "image": prov.AUCKLAND_MUSEUM_IMAGE_PROVIDER,
    }
    endpoint = "https://api.aucklandmuseum.com/search/collectionsonline/_search"
    license_url = "https://creativecommons.org/licenses/by/4.0/"
    total_amount_of_data = 10000
    DEFAULT_LICENSE_INFO = get_license_info(license_url=license_url)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.delay = 4
        self.batch_start = 0
        self.batch_limit = 2000
        self.headers = {"Content-Type": "application/json"}
        date_from = datetime.strptime(self.date, "%Y-%m-%d")
        self.date_from = date_from.isoformat()
        self.date_to = (date_from + timedelta(days=1)).isoformat()
        logger.info(f"Start timestamp: {self.date_from}, end timestamp: {self.date_to}")
        self.data = {
            "query": {
                "bool": {
                    "must": [
                        {"wildcard": {"copyright": {"value": "Auckland"}}},
                        {"exists": {"field": "primaryRepresentation"}},
                        {
                            "range": {
                                "lastModifiedOn": {
                                    "from": self.date_from,
                                    "to": self.date_to,
                                }
                            }
                        },
                    ]
                }
            }
        }

    def get_next_query_params(self, prev_query_params: dict | None, **kwargs) -> dict:
        # Return default query params on the first request
        # primaryRepresentation contain a image url for each data
        # "+" is a query string syntax for must be present
        # copyright:CC state Creative Commons Attribution 4.0
        return {
            "size": "2000",
            "from": self.batch_start,
        }

    def get_batch_data(self, response_json):
        # Takes the raw API response from calling `get` on the endpoint, and returns
        # the list of records to process.
        if response_json:
            return response_json.get("hits", {}).get("hits")
        return None

    def get_should_continue(self, response_json):
        # Do not continue if we have exceeded the total amount of data
        self.batch_start += self.batch_limit
        if self.batch_start >= self.total_amount_of_data:
            logger.info(
                "The final amount of data has been processed. Halting ingestion."
            )
            return False

        return True

    def get_media_type(self, record: dict):
        return IMAGE

    def get_record_data(self, data: dict) -> dict | list[dict] | None:
        # check if _id is empty then foreign_landing_url and
        # foreign_identifier doesn't exist

        if not (identifier := data.get("_id")):
            return None

        url_parameter = identifier.split("id/")[-1].replace("/", "-")
        foreign_landing_url = f"{LANDING_URL}{url_parameter}"

        foreign_identifier = identifier.split("/")[-1]

        information = data.get("_source", {})

        if not (url := information.get("primaryRepresentation")):
            return None

        license_info = self.DEFAULT_LICENSE_INFO

        creator = (
            information.get("dc_contributor")[0]
            if information.get("dc_contributor", [])
            else None
        )

        appellation = information.get("appellation", {})
        title = (
            appellation.get("Primary Title")[0]
            if appellation.get("Primary Title")
            else None
        )
        meta_data = self._get_meta_data(information)

        return {
            "foreign_landing_url": foreign_landing_url,
            "foreign_identifier": foreign_identifier,
            "url": url,
            "license_info": license_info,
            "creator": creator,
            "title": title,
            "meta_data": meta_data,
        }

    @staticmethod
    def _get_meta_data(object_json: dict) -> dict | None:
        geopos = object_json.get("geopos")[0] if object_json.get("geopos", []) else ""
        department = (
            object_json.get("department")[0]
            if object_json.get("department", [])
            else None
        )

        metadata = {
            "type": object_json.get("type"),
            "geopos": geopos,
            "department": department,
        }

        metadata = {k: v for k, v in metadata.items() if v is not None}
        return metadata

    def _get_file_info(self, url) -> int | None:
        """Get the image size in bytes."""
        resp = self.delayed_requester.head(url)
        if resp:
            filesize = int(resp.headers.get("Content-Length", 0))
            return filesize if filesize != 0 else None

    def get_response_json(
        self, query_params: dict, endpoint: str | None = None, **kwargs
    ):
        """
        Make the actual API requests needed to ingest a batch.

        This can be overridden in order to support APIs that require multiple requests,
        for example.
        """
        return self.delayed_requester.get_response_json(
            endpoint or self.endpoint,
            self.retries,
            query_params,
            headers=self.headers,
            requestMethod="post",
            json=self.data,
            **kwargs,
        )


def main():
    # Allows running ingestion from the CLI without Airflow running for debugging
    # purposes.
    ingester = AucklandMuseumDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
