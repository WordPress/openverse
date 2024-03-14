"""
Content Provider:       Justtakeitfree

ETL Process:            Use the API to identify all CC licensed media.

Output:                 TSV file containing the media and the
                        respective meta-data.

Notes:                  https://justtakeitfree.com/api/api.php
This API requires an API key. For more details, see https://github.com/WordPress/openverse/pull/2793
"""

import logging

from airflow.models import Variable

from common.constants import IMAGE
from common.licenses import get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)


class JusttakeitfreeDataIngester(ProviderDataIngester):
    providers = {
        "image": prov.JUSTTAKEITFREE_IMAGE_PROVIDER,
    }
    endpoint = "https://justtakeitfree.com/api/api.php"
    creator = "Justtakeitfree Free Photos"
    creator_url = "https://justtakeitfree.com"

    def get_next_query_params(self, prev_query_params: dict | None, **kwargs) -> dict:
        if not prev_query_params:
            return {"page": 1, "key": Variable.get("API_KEY_JUSTTAKEITFREE")}
        else:
            return {
                **prev_query_params,
                "page": prev_query_params["page"] + 1,
            }

    def get_batch_data(self, response_json) -> list[list[dict]] | None:
        if response_json and (data := response_json.get("data")):
            return data
        return None

    def get_media_type(self, record: dict):
        return IMAGE

    def get_record_data(self, data: list[dict]) -> dict | None:
        data = data[0]
        if not (foreign_landing_url := data.get("page_link")):
            return None

        if not (foreign_identifier := foreign_landing_url.split("/")[-2]):
            return None

        if not (url := data.get("full_image_link")):
            return None

        license_url = data.get("license_link", "").replace("deed.en", "")
        license_info = get_license_info(license_url)
        if license_info is None:
            return None

        raw_record_data = {
            "foreign_landing_url": foreign_landing_url,
            "url": url,
            "license_info": license_info,
            "foreign_identifier": foreign_identifier,
            # Optional fields
            "creator": self.creator,
            "creator_url": self.creator_url,
            "raw_tags": set(data.get("tags")),
            "filesize": self.get_file_info(url),
            "thumbnail_url": data.get("preview_link"),
        }
        return {k: v for k, v in raw_record_data.items() if v is not None}

    def get_file_info(self, url) -> int | None:
        """Get the image size in bytes."""
        resp = self.delayed_requester.head(url)
        if resp:
            filesize = int(resp.headers.get("Content-Length", 0))
            return filesize if filesize != 0 else None


def main():
    ingester = JusttakeitfreeDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
