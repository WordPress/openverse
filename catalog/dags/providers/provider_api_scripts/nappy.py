"""
Content Provider:       Nappy

ETL Process:            Use the API to identify all CC0-licensed images.

Output:                 TSV file containing the image meta-data.

Notes:                  This api was written specially for Openverse.
                        There are no known limits or restrictions.
                        https://nappy.co/

"""
import logging

from common import constants
from common.licenses import get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)


class NappyDataIngester(ProviderDataIngester):
    providers = {constants.IMAGE: prov.NAPPY_DEFAULT_PROVIDER}
    endpoint = "https://api.nappy.co/v1/openverse/images"
    headers = {"Accept": "application/json"}

    # Hardcoded to CC0, the only license Nappy.co uses
    license_info = get_license_info(
        "https://creativecommons.org/publicdomain/zero/1.0/"
    )

    def get_next_query_params(self, prev_query_params: dict | None, **kwargs) -> dict:
        if not prev_query_params:
            return {
                "page": 1,
                "per_page": self.batch_limit,
            }
        else:
            return {
                **prev_query_params,
                "page": prev_query_params["page"] + 1,
            }

    def get_batch_data(self, response_json):
        if response_json:
            return response_json.get("images")
        return None

    def get_should_continue(self, response_json):
        return bool(response_json.get("next_page"))

    def get_media_type(self, record: dict):
        return constants.IMAGE

    @staticmethod
    def _convert_filesize(raw_filesize_string: str) -> int:
        """Convert sizes from strings to byte integers, ex. "187.8kB" to 188."""
        FILETYPE_MULTIPLIERS = {"kB": 1000, "MB": 1_000_000, "GB": 1_000_000_000}
        if isinstance(raw_filesize_string, str) and len(raw_filesize_string) > 2:
            stripped = raw_filesize_string.strip()
            if stripped[-2:] in FILETYPE_MULTIPLIERS:
                try:
                    units = float(stripped[:-2])
                except ValueError:
                    return
                multiplier = FILETYPE_MULTIPLIERS[stripped[-2:]]
                return round(units * multiplier)

    def get_record_data(self, data: dict) -> dict | None:
        if not (foreign_landing_url := data.get("foreign_landing_url")):
            return None

        if not (url := data.get("url")):
            return None

        if not (foreign_identifier := data.get("foreign_identifier")):
            return None

        thumbnail_url = data.get("url") + "?auto=format&w=600&q=75"
        filesize = self._convert_filesize(data.get("filesize"))
        filetype = data.get("filetype")
        creator = data.get("creator")
        creator_url = data.get("creator_url")
        title = data.get("title")
        meta_data = {
            "views": data.get("views"),
            "saves": data.get("saves"),
            "downloads": data.get("downloads"),
        }
        raw_tags = data.get("tags").split(",")
        width = data.get("width")
        height = data.get("height")

        return {
            "foreign_landing_url": foreign_landing_url,
            "url": url,
            "thumbnail_url": thumbnail_url,
            "license_info": self.license_info,
            "foreign_identifier": foreign_identifier,
            "filesize": filesize,
            "filetype": filetype,
            "creator": creator,
            "creator_url": creator_url,
            "title": title,
            "meta_data": meta_data,
            "raw_tags": raw_tags,
            "width": width,
            "height": height,
        }


def main():
    logger.info("Begin: Nappy data ingestion")
    ingester = NappyDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
