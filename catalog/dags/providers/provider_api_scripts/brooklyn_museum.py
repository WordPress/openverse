import logging

import lxml.html as html
from airflow.models import Variable

from common import constants
from common.licenses import LicenseInfo, get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)


class BrooklynMuseumDataIngester(ProviderDataIngester):
    providers = {"image": prov.BROOKLYN_DEFAULT_PROVIDER}
    endpoint = "https://www.brooklynmuseum.org/api/v2/object/"
    batch_limit = 35

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = Variable.get("API_KEY_BROOKLYN_MUSEUM")
        self.headers = {"api_key": self.api_key}

    def get_next_query_params(self, prev_query_params: dict | None, **kwargs) -> dict:
        if not prev_query_params:
            return {
                "has_images": 1,
                "rights_type_permissive": 1,
                "limit": self.batch_limit,
                "offset": 0,
            }
        else:
            return {
                **prev_query_params,
                "offset": prev_query_params["offset"] + self.batch_limit,
            }

    @staticmethod
    def _get_data_from_response(response_json) -> dict | None:
        if response_json and response_json.get("message", "").lower() == "success.":
            return response_json.get("data")
        return None

    def get_batch_data(self, response_json) -> list | None:
        return self._get_data_from_response(response_json)

    @staticmethod
    def _get_license_info(data: dict) -> LicenseInfo | None:
        rights_info = data.get("rights_type", {}).get("description", "")
        elements = html.fromstring(rights_info)
        cc_links = [
            link
            for _, _, link, _ in elements.iterlinks()
            if "https://creativecommons.org/" in link
        ]
        if len(cc_links) == 1:
            return get_license_info(license_url=cc_links[0])

        return None

    @staticmethod
    def _get_image_sizes(image):
        height, width = None, None
        size_list = image.get("derivatives", "")
        if isinstance(size_list, list):
            # Pull out the largest sized image we have access to
            # https://www.brooklynmuseum.org/api/new-documentation/#definition-Image
            size_type = image.get("largest_derivative", "")
            for size in size_list:
                if size.get("size", "") == size_type:
                    height = size.get("height")
                    width = size.get("width")
        return height, width

    @staticmethod
    def _get_metadata(data):
        metadata = {
            "accession_number": data.get("accession_number"),
            "date": data.get("object_date"),
            "description": data.get("description"),
            "medium": data.get("medium"),
            "credit_line": data.get("credit_line"),
            "classification": data.get("classification"),
        }
        return {k: v for k, v in metadata.items() if v is not None}

    @staticmethod
    def _get_creators(data):
        artists_info = data.get("artists")
        if isinstance(artists_info, list):
            creators_list = (
                artists.get("name")
                for artists in artists_info
                if artists.get("rank") == 1
            )
            creator = next(creators_list, None)
        else:
            creator = None
        return creator

    @staticmethod
    def _handle_object_data(data, license_info: LicenseInfo) -> list[dict]:
        # id_ is used to create the foreign_landing_url, which is a required field
        if not (image_info := data.get("images")) or not (id_ := data.get("id")):
            return []

        foreign_landing_url = (
            f"https://www.brooklynmuseum.org/opencollection/objects/{id_}"
        )

        title = data.get("title", "")
        metadata = BrooklynMuseumDataIngester._get_metadata(data)
        creators = BrooklynMuseumDataIngester._get_creators(data)

        images = []
        for image in image_info:
            if not (foreign_identifier := image.get("id")):
                continue
            if not (image_url := image.get("largest_derivative_url")):
                continue
            height, width = BrooklynMuseumDataIngester._get_image_sizes(image)
            images.append(
                {
                    "foreign_landing_url": foreign_landing_url,
                    "url": image_url,
                    "license_info": license_info,
                    "foreign_identifier": foreign_identifier,
                    "width": width,
                    "height": height,
                    "title": title,
                    "meta_data": metadata,
                    "creator": creators,
                }
            )
        return images

    def get_record_data(self, data: dict) -> dict | list[dict] | None:
        if not (id_ := data.get("id")):
            return None
        if not (license_info := self._get_license_info(data)):
            return None
        endpoint = f"{self.endpoint}{id_}"
        object_data = self._get_data_from_response(
            self.get_response_json(query_params={}, endpoint=endpoint)
        )
        if not object_data:
            return None
        return self._handle_object_data(data=object_data, license_info=license_info)


def main():
    logger.info("Begin: Brooklyn museum provider script")
    ingester = BrooklynMuseumDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
