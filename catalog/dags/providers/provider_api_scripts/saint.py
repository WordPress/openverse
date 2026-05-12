"""
Content Provider: SAiNT (IMG Saxony-Anhalt)

ETL Process: Use the API to identify all CC licensed media.

Output: TSV file containing the media and the respective meta-data.

Notes: https://saint.tech/api/docs
"""

import logging

from airflow.models import Variable

from common.licenses import get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)


class SaintDataIngester(ProviderDataIngester):
    providers = {
        "image": prov.SAINT_DEFAULT_PROVIDER,
    }
    endpoint = "https://saint.tech/api/poi"
    creator = "IMG Saxony-Anhalt"
    creator_url = "https://saint.tech/en"

    def get_next_query_params(self, prev_query_params: dict | None) -> dict:
        if not prev_query_params:
            return {
                "page": 1,
                "pageSize": 100,
                "api_key": Variable.get("API_KEY_SAINT", default_var=""),
            }
        else:
            return {
                **prev_query_params,
                "page": prev_query_params["page"] + 1,
            }

    def get_batch_data(self, response_json) -> list[dict] | None:
        if response_json and (data := response_json.get("data")):
            return data
        return None

    def get_record_data(self, data: dict) -> dict | None:
        # Expected fields based on typical Swagger UI schemas for POI
        if not (foreign_identifier := data.get("id")):
            return None

        # Look for image
        if not (image := data.get("PrimaryImage")):
            return None

        if not (url := image.get("url")):
            return None

        # Try to find license
        license_url = (image.get("license") or {}).get("url")
        if not license_url:
            return None

        license_info = get_license_info(license_url)
        if license_info is None:
            return None

        foreign_landing_url = f"https://saint.tech/poi/{foreign_identifier}"

        title = data.get("title")

        raw_record_data = {
            "foreign_landing_url": foreign_landing_url,
            "url": url,
            "license_info": license_info,
            "foreign_identifier": str(foreign_identifier),
            "title": title,
            "creator": self.creator,
            "creator_url": self.creator_url,
        }

        if width := image.get("width"):
            raw_record_data["width"] = width
        if height := image.get("height"):
            raw_record_data["height"] = height

        return {k: v for k, v in raw_record_data.items() if v is not None}


def main():
    ingester = SaintDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
