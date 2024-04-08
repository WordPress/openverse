"""
Content Provider:       Statens Museum for Kunst (National Gallery of Denmark)

ETL Process:            Use the API to identify all openly licensed media.

Output:                 TSV file containing the media metadata.

Notes:                  https://www.smk.dk/en/article/smk-api/
"""

import logging
import urllib.parse

from common import constants
from common.licenses import get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)


class SmkDataIngester(ProviderDataIngester):
    endpoint = "https://api.smk.dk/api/v1/art/search/"
    delay = 5
    batch_limit = 2000
    headers = {"Accept": "application/json"}
    providers = {"image": prov.SMK_DEFAULT_PROVIDER}

    def get_next_query_params(self, prev_query_params: dict | None, **kwargs) -> dict:
        if not prev_query_params:
            return {
                "keys": "*",
                "filters": "[has_image:true],[public_domain:true]",
                "offset": 0,
                "rows": self.batch_limit,
                "lang": "en",
            }
        return {
            **prev_query_params,
            "offset": prev_query_params["offset"] + self.batch_limit,
        }

    def get_batch_data(self, response_json) -> list:
        return response_json.get("items")

    @staticmethod
    def _get_foreign_landing_url(item) -> str | None:
        """Use the English site instead of the original link."""
        if not (object_num := item.get("object_number")):
            logger.info(
                f"Image with (foreign) id {item.get('id')} does not have "
                "`object_number`! Therefore we cannot build the "
                "foreign_landing_url."
            )
            return None
        # Occasionally, the object number will have a space in it. for these cases we
        # need to urlencode it.
        return f"https://open.smk.dk/en/artwork/image/{urllib.parse.quote(object_num)}"

    @staticmethod
    def _get_image_url(image_iiif_id: str, image_size=2048):
        # For high quality IIIF-enabled images, restrict the image size to prevent
        # loading very large files.
        return f"{image_iiif_id}/full/!{image_size},/0/default.jpg"

    @staticmethod
    def _get_title(item: dict) -> str | None:
        titles = item.get("titles")
        if not titles or not isinstance(titles, list):
            logger.info(f"No title for image with (foreign) id {item.get('id')}.")
            return
        return titles[0].get("title")

    @staticmethod
    def _get_creator(item: dict) -> str | None:
        # TODO: review this field, there could be more than one creator or artist.
        # Keeping it as it was for the class refactor.
        data = item.get("production", [])
        if not data or not isinstance(data, list):
            return
        return data[0].get("creator")

    @staticmethod
    def _get_metadata(item: dict) -> dict:
        meta_data = {}
        if created_date := item.get("created"):
            meta_data["created_date"] = created_date
        collection = item.get("collection")
        if isinstance(collection, list):
            meta_data["collection"] = ",".join(collection)
        techniques = item.get("techniques")
        if isinstance(techniques, list):
            meta_data["techniques"] = ",".join(techniques)
        colors = item.get("colors")
        if isinstance(colors, list):
            meta_data["colors"] = ",".join(colors)
        return meta_data

    def get_record_data(self, data: dict) -> dict | None:
        # We used to get additional images from the `alternative_images` field,
        # but we found these to be either redundant, duplicates, or lower quality
        # versions. See https://github.com/WordPress/openverse-catalog/issues/875
        # for the full investigation & discussion
        if not (license_info := get_license_info(data.get("rights"))):
            return None
        if not (foreign_landing_url := self._get_foreign_landing_url(data)):
            return None

        # Legacy images do not have an iiif_id; fall back to the ID from the
        # collection DB.
        iiif_id = data.get("image_iiif_id")
        foreign_identifier = iiif_id or data.get("id")
        if not foreign_identifier:
            return None

        # Legacy images do not have IIIF links.
        url = (
            SmkDataIngester._get_image_url(iiif_id)
            if iiif_id
            else data.get("image_native")
        )
        if not url:
            return None

        thumbnail_url = data.get("image_thumbnail")
        if thumbnail_url:
            thumbnail_url = thumbnail_url.replace(" ", "%20")
        height = data.get("image_height")
        width = data.get("image_width")
        filesize = data.get("image_size") or data.get("size")

        return {
            "foreign_identifier": foreign_identifier,
            "foreign_landing_url": foreign_landing_url,
            "license_info": license_info,
            "title": self._get_title(data),
            "url": url.replace(" ", "%20"),
            "thumbnail_url": thumbnail_url,
            "height": height,
            "width": width,
            "filesize": filesize,
            "creator": self._get_creator(data),
            "meta_data": self._get_metadata(data),
        }


def main():
    logger.info("Begin: SMK provider script")
    ingester = SmkDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
