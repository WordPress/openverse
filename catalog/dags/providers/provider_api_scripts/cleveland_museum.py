import logging

from common.licenses import get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)

CC0_LICENSE = get_license_info(license_="cc0", license_version="1.0")


class ClevelandDataIngester(ProviderDataIngester):
    providers = {"image": prov.CLEVELAND_DEFAULT_PROVIDER}
    endpoint = "http://openaccess-api.clevelandart.org/api/artworks/"
    batch_limit = 1000
    delay = 5

    def get_next_query_params(self, prev_query_params, **kwargs):
        if not prev_query_params:
            # Return default query params on the first request
            return {"cc": "1", "has_image": "1", "limit": self.batch_limit, "skip": 0}
        else:
            # Increment `skip` by the batch limit.
            return {
                **prev_query_params,
                "skip": prev_query_params["skip"] + self.batch_limit,
            }

    def get_batch_data(self, response_json):
        if response_json:
            return response_json.get("data")
        return None

    def get_record_data(self, data):
        license_ = data.get("share_license_status", "").lower()
        if license_ != "cc0":
            logger.debug(f"Wrong license image: {license_}")
            return None

        # This would also be falsy if id is equal to `0`.
        if not (foreign_id := data.get("id")):
            return None

        if not (foreign_landing_url := data.get("url")):
            return None

        if not (image := self._get_image_data(data.get("images", {}))):
            return None

        if data.get("creators"):
            creator_name = data.get("creators")[0].get("description", "")
        else:
            creator_name = ""

        return {
            "foreign_identifier": f"{foreign_id}",
            "foreign_landing_url": foreign_landing_url,
            "title": data.get("title", None),
            "creator": creator_name,
            "url": image["url"],
            "width": self._get_int_value(image, "width"),
            "height": self._get_int_value(image, "height"),
            "filesize": self._get_int_value(image, "filesize"),
            "license_info": CC0_LICENSE,
            "meta_data": self._get_metadata(data),
        }

    @staticmethod
    def _get_image_data(image_data) -> dict | None:
        # Returns the best available image in the `image_data` dict,
        # preferring `web` and falling back to other types.
        if not image_data:
            return None

        for key in ["web", "print", "full"]:
            # This dictionary contains the required `url` parameter, so we
            # only use the item that contains the `url` key.
            if (keyed_image := image_data.get(key)) and "url" in keyed_image:
                return keyed_image
        return None

    @staticmethod
    def _get_int_value(data: dict, key: str) -> int | None:
        """
        Convert the value of the key `key` in `data` to an integer.

        Returns None if the value is not convertible to an integer, or
        if the value doesn't exist.
        """
        value = data.get(key)
        if bool(value):
            if isinstance(value, str) and value.isdigit():
                return int(value)
            elif isinstance(value, int):
                return value
        return None

    @staticmethod
    def _get_metadata(data):
        metadata = {
            "accession_number": data.get("accession_number"),
            "technique": data.get("technique"),
            "date": data.get("creation_date"),
            "credit_line": data.get("creditline"),
            "classification": data.get("type"),
            "tombstone": data.get("tombstone"),
            "culture": ",".join([i for i in data.get("culture", []) if i is not None])
            or None,
        }
        metadata = {k: v for k, v in metadata.items() if v is not None}
        return metadata


def main():
    logger.info("Begin: Cleveland Museum data ingestion")
    ingester = ClevelandDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
