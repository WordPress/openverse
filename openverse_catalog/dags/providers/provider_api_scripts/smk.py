import logging

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

    def get_media_type(self, record: dict) -> str:
        return constants.IMAGE

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
        object_num = item.get("object_number")
        if not object_num:
            logger.info(
                f"Image with (foreign) id {item.get('id')} does not have "
                "`object_number`! Therefore we cannot build the "
                "foreign_landing_url."
            )
            return
        return f"https://open.smk.dk/en/artwork/image/{object_num}"

    @staticmethod
    def _get_image_url(image_iiif_id: str, image_size=2048):
        # For high quality IIIF-enabled images, restrict the image size to prevent
        # loading very large files.
        # TODO: consider just using the full "image_native" when adding the
        # "image_thumbnail".
        image_url = f"{image_iiif_id}/full/!{image_size},/0/default.jpg"
        return image_url

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
    def _get_images(item: dict) -> list:
        images = []

        # Legacy images do not have an iiif_id; fall back to the ID from the
        # collection DB.
        iiif_id = item.get("image_iiif_id")
        image_id = iiif_id or item.get("id")

        if image_id is not None:
            if iiif_id is None:
                # Legacy images do not have IIIF links.
                image_url = item.get("image_native")
            else:
                image_url = SmkDataIngester._get_image_url(iiif_id)

            height = item.get("image_height")
            width = item.get("image_width")
            filesize = item.get("image_size") or item.get("size")
            images.append(
                {
                    "id": image_id,
                    "image_url": image_url,
                    "height": height,
                    "width": width,
                    "filesize": filesize,
                }
            )

        alternative_images = item.get("alternative_images")
        if type(alternative_images) == list:
            for alt_img in alternative_images:
                if type(alt_img) == dict:
                    iiif_id = alt_img.get("iiif_id")
                    if iiif_id is None:
                        # The API for alternative images does not include the
                        # 'id', so we must skip if `iiif_id` is not present.
                        continue
                    image_url = SmkDataIngester._get_image_url(iiif_id)
                    height = alt_img.get("height")
                    width = alt_img.get("width")
                    filesize = alt_img.get("image_size") or alt_img.get("size")

                    images.append(
                        {
                            "id": iiif_id,
                            "image_url": image_url,
                            "height": height,
                            "width": width,
                            "filesize": filesize,
                        }
                    )
        return images

    @staticmethod
    def _get_metadata(item: dict) -> dict:
        meta_data = {}
        if created_date := item.get("created"):
            meta_data["created_date"] = created_date
        collection = item.get("collection")
        if type(collection) == list:
            meta_data["collection"] = ",".join(collection)
        techniques = item.get("techniques")
        if type(techniques) == list:
            meta_data["techniques"] = ",".join(techniques)
        colors = item.get("colors")
        if type(colors) == list:
            meta_data["colors"] = ",".join(colors)
        return meta_data

    def get_record_data(self, data: dict) -> dict | list[dict] | None:
        license_info = get_license_info(license_url=data.get("rights"))
        if license_info is None:
            return
        images = []
        alt_images = self._get_images(data)
        for img in alt_images:
            images.append(
                {
                    "foreign_identifier": img.get("id"),
                    "foreign_landing_url": self._get_foreign_landing_url(data),
                    "image_url": img.get("image_url"),
                    "license_info": license_info,
                    "title": self._get_title(data),
                    "creator": self._get_creator(data),
                    "height": img.get("height"),
                    "width": img.get("width"),
                    "filesize": img.get("filesize"),
                    "meta_data": self._get_metadata(data),
                }
            )
        return images


def main():
    logger.info("Begin: SMK provider script")
    ingester = SmkDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
