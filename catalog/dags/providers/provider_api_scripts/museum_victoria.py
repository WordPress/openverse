import logging
from typing import TypedDict

from common.licenses import LicenseInfo, get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)


class ImageDetails(TypedDict, total=False):
    foreign_identifier: str
    url: str
    license_info: LicenseInfo
    foreign_landing_url: str
    title: str
    meta_data: dict
    height: int | None
    width: int | None
    creator: str | None


class VictoriaDataIngester(ProviderDataIngester):
    providers = {"image": prov.VICTORIA_DEFAULT_PROVIDER}
    endpoint = "https://collections.museumsvictoria.com.au/api/search"
    headers = {"Accept": "application/json"}
    batch_limit = 100
    delay = 5
    LANDING_PAGE = "https://collections.museumsvictoria.com.au/"
    LICENSE_LIST = [
        "public domain",
        "cc by",
        "cc by-nc",
        "cc by-nc-sa",
        "cc by-nc-nd",
        "cc by-sa",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This set is used to prevent duplicate images of the same items
        self.RECORDS_IDS = set()

    def get_batch_data(self, response_json):
        return response_json or None

    def get_fixed_query_params(self):
        return [{"imagelicense": license_} for license_ in self.LICENSE_LIST]

    def get_next_query_params(self, prev_query_params: dict | None) -> dict:
        if not prev_query_params:
            return {
                "hasimages": "yes",
                "perpage": self.batch_limit,
                "page": 0,
            }
        else:
            return {
                **prev_query_params,
                "page": prev_query_params["page"] + 1,
            }

    def get_record_data(self, data: dict):
        if not (object_id := data.get("id")) or object_id in self.RECORDS_IDS:
            return None
        self.RECORDS_IDS.add(object_id)
        foreign_landing_url = f"{self.LANDING_PAGE}{object_id}"

        if not (media_data := data.get("media")) or not (
            images := self._get_images(media_data)
        ):
            return None
        meta_data = self._get_metadata(data)
        title = data.get("displayTitle")
        image_data = {
            "foreign_landing_url": foreign_landing_url,
            "title": title,
            "meta_data": meta_data,
        }

        record_images = []
        for image in images:
            image.update(image_data)
            record_images.append(image)

        return record_images

    @staticmethod
    def _get_images(media_data) -> list[ImageDetails]:
        images = []
        for media in media_data:
            if media.get("type") != "image":
                continue
            if not (foreign_identifier := media.get("id")):
                continue
            url, height, width, filesize = VictoriaDataIngester._get_image_data(media)
            license_info = VictoriaDataIngester._get_license_info(media)
            if not url or not license_info:
                continue
            creator = VictoriaDataIngester._get_creator(media)

            image: ImageDetails = {
                "foreign_identifier": foreign_identifier,
                "url": url,
                "height": height,
                "width": width,
                "license_info": license_info,
                "creator": creator,
            }
            images.append(image)
        return images

    @staticmethod
    def _get_image_data(
        media: dict,
    ) -> tuple[str | None, int | None, int | None, int | None]:
        height, width, filesize = None, None, None
        media_data = {}
        for size in ["large", "medium", "small"]:
            if isinstance(media.get(size), dict) and media[size].get("uri"):
                media_data = media[size]
                break
        if image_url := media_data.get("uri"):
            height = media_data.get("height")
            width = media_data.get("width")
            filesize = media_data.get("size")
        return image_url, height, width, filesize

    @staticmethod
    def _get_creator(media) -> str | None:
        creators = media.get("creators")
        if isinstance(creators, list):
            creators = ",".join(media.get("creators"))
        return creators

    @staticmethod
    def join_string_list(object_key, obj):
        data = obj.get(object_key)
        return ",".join(data) if isinstance(data, list) else None

    @staticmethod
    def _get_metadata(obj):
        meta_data = {
            "datemodified": obj.get("dateModified"),
            "category": obj.get("category"),
            "description": obj.get("physicalDescription"),
            "keywords": VictoriaDataIngester.join_string_list("keywords", obj),
            "classifications": VictoriaDataIngester.join_string_list(
                "classifications", obj
            ),
        }

        return {key: value for key, value in meta_data.items() if value is not None}

    @staticmethod
    def _get_license_info(media: dict) -> LicenseInfo | None:
        license_uri = media.get("licence", {}).get("uri", {})
        if "creativecommons" in license_uri:
            return get_license_info(license_url=license_uri)
        return None


def main():
    logger.info("Begin: Victoria Museum data ingestion")
    ingester = VictoriaDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
