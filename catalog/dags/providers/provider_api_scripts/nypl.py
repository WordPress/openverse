import logging
import re
from urllib.parse import parse_qs, urlparse

from airflow.models import Variable

from common import constants
from common.licenses import get_license_info
from common.loader import provider_details as prov
from common.loader.provider_details import ImageCategory
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)


def get_value_from_dict_or_list(
    dict_or_list: dict | list, keys: list[str]
) -> dict | list | str | None:
    """
    Return the nested value.

    If dict_or_list is a list, returns the value from the first dictionary in the list.
    If it is a dict, returns the value from the dict.
    """
    if not keys or not dict_or_list:
        return dict_or_list
    current_key, *updated_keys = keys
    if isinstance(dict_or_list, list):
        for item in dict_or_list:
            if current_key in item:
                val = item[current_key]
                if isinstance(val, (list, dict)):
                    return get_value_from_dict_or_list(val, updated_keys)
                elif isinstance(val, str) or val is None:
                    return val
        return None
    elif isinstance(dict_or_list, dict):
        val = dict_or_list.get(current_key)
        if isinstance(val, (list, dict)):
            return get_value_from_dict_or_list(val, updated_keys)
        return val


class NyplDataIngester(ProviderDataIngester):
    providers = {"image": prov.NYPL_DEFAULT_PROVIDER}
    endpoint_base = "http://api.repo.nypl.org/api/v2/items"
    endpoint = f"{endpoint_base}/search/"
    metadata_endpoint = f"{endpoint_base}/item_details/"
    batch_limit = 500
    delay = 5
    # NYPL returns a list of image objects, with the dimension encoded
    # in the URL's query parameter.
    # This list is in order from the largest image to the smallest one.
    url_dimensions = ["g", "v", "q", "w", "r"]

    def __init__(self, *args, **kwargs):
        NYPL_API = Variable.get("API_KEY_NYPL")
        NyplDataIngester.headers = {"Authorization": f"Token token={NYPL_API}"}
        super().__init__(*args, **kwargs)

    def get_next_query_params(self, prev_query_params, **kwargs):
        if not prev_query_params:
            return {
                "q": "CC_0",
                "field": "use_rtxt_s",
                "page": 1,
                "per_page": self.batch_limit,
            }

        else:
            # Increment `skip` by the batch limit.
            return {
                **prev_query_params,
                "page": prev_query_params["page"] + 1,
            }

    def get_media_type(self, record):
        # This provider only supports Images.
        return constants.IMAGE

    def get_batch_data(self, response_json):
        if response_json:
            return response_json.get("nyplAPI", {}).get("response", {}).get("result")
        return None

    def get_record_data(self, data):
        if not (uuid := data.get("uuid")):
            return None

        item_json = (
            self.get_response_json({}, endpoint=self.metadata_endpoint + uuid) or {}
        )
        if not (item_details := item_json.get("nyplAPI", {}).get("response")):
            return None
        mods = item_details.get("mods", {})

        title = NyplDataIngester._get_title(mods)

        creator = (
            NyplDataIngester._get_creators(name_properties)
            if (name_properties := mods.get("name"))
            else None
        )

        metadata = NyplDataIngester._get_metadata(mods)
        category = (
            ImageCategory.PHOTOGRAPH if metadata.get("genre") == "Photographs" else None
        )

        if not (captures := NyplDataIngester._get_captures(item_details)):
            return None

        images = []
        for capture in captures:
            if not (foreign_identifier := capture.get("imageID", {}).get("$")):
                continue

            image_link = capture.get("imageLinks", {}).get("imageLink", [])
            url, filetype = NyplDataIngester._get_image_data(image_link)
            if not url:
                continue

            if not (foreign_landing_url := capture.get("itemLink", {}).get("$")):
                continue

            license_url = capture.get("rightsStatementURI", {}).get("$")
            if not (license_info := get_license_info(license_url)):
                continue

            image_data = {
                "foreign_identifier": foreign_identifier,
                "foreign_landing_url": foreign_landing_url,
                "url": url,
                "license_info": license_info,
                "title": title,
                "creator": creator,
                "filetype": filetype,
                "category": category,
                "meta_data": metadata,
                "raw_tags": NyplDataIngester._get_tags(mods) or None,
            }
            images.append(image_data)
        return images

    @staticmethod
    def _get_title(mods: dict) -> str:
        title_info = mods.get("titleInfo")
        if isinstance(title_info, list) and title_info:
            title_info = title_info[0]
        return "" if not title_info else title_info.get("title", {}).get("$")

    @staticmethod
    def _get_captures(item_details: dict) -> list[dict]:
        captures = item_details.get("sibling_captures", {}).get("capture")
        if captures and not isinstance(captures, list):
            captures = [captures]
        return captures

    @staticmethod
    def _get_filetype(description: str):
        """
        Extract the filetype from a description string.

        Example:
        "Cropped .jpeg (1600 pixels on the long side)"
        This is required because the filetype is not present/extractable from the
        url via the MediaStore class.
        :param description: the description string
        :return:  jpeg | gif
        """
        if match := re.search(r" .(jpeg|gif) ", description):
            return match.group(1)
        return None

    @staticmethod
    def _get_image_data(images) -> tuple[None, None] | tuple[str, str]:
        """
        Get the image data from the list of images.

        Receives a list of dictionaries of the following shape:
        {
          "$": "http://images.nypl.org/index.php?id=56738467&t=q&download=1
        &suffix=29eed1f0-3d50-0134-c4c7-00505686a51c.001",
          "description": "Cropped .jpeg (1600 pixels on the long side)"
        }
        Selects the largest image based on the image URL's `t` query parameter
        and url_dimensions.
        """
        # Create a dict with the NyplDataIngester.url_dimensions as keys,
        # and image data as value.
        image_types = {
            parse_qs(urlparse(img["$"]).query)["t"][0]: i
            for i, img in enumerate(images)
        }
        if not image_types:
            return None, None

        # Select the dict containing the URL for the largest image.
        # The image size is encoded in the URL query parameter `t`.
        # The list of dimensions is sorted by size of the corresponding image.
        for dimension in NyplDataIngester.url_dimensions:
            preferred_image_index = image_types.get(dimension)
            if preferred_image_index is not None:
                preferred_image = images[preferred_image_index]

                # Removes the `download` query to get the viewable image URL
                url = preferred_image["$"].replace("&download=1", "")
                filetype = NyplDataIngester._get_filetype(
                    preferred_image["description"]
                )
                return url, filetype

        return None, None

    @staticmethod
    def _get_creators(creatorinfo):
        if not isinstance(creatorinfo, list):
            creatorinfo = [creatorinfo]
        for info in creatorinfo:
            if info.get("usage") == "primary":
                return info.get("namePart", {}).get("$")
        return None

    @staticmethod
    def _get_tags(mods: dict) -> list[str]:
        subject_list = mods.get("subject", [])
        if isinstance(subject_list, dict):
            subject_list = [subject_list]
        # Topic can be a dictionary or a list
        topics = [subject["topic"] for subject in subject_list if "topic" in subject]
        tags = []
        if topics:
            for topic in topics:
                if isinstance(topic, list):
                    tags.extend([t.get("$") for t in topic])
                else:
                    tags.append(topic.get("$"))
        return tags

    @staticmethod
    def _get_type_of_resource(mods: dict) -> str | None:
        type_of_resource = mods.get("typeOfResource", {})
        if isinstance(type_of_resource, list):
            for type_ in type_of_resource:
                if type_.get("usage") == "primary":
                    return type_.get("$")
            return None
        else:
            return type_of_resource.get("$")

    @staticmethod
    def _get_metadata(mods):
        metadata = {}

        if type_of_resource := NyplDataIngester._get_type_of_resource(mods):
            metadata["type_of_resource"] = type_of_resource

        if genre := get_value_from_dict_or_list(mods, ["genre", "$"]):
            metadata["genre"] = genre

        origin_info = mods.get("originInfo", {})

        if date_issued := get_value_from_dict_or_list(
            mods, ["originInfo", "dateIssued", "$"]
        ):
            metadata["date_issued"] = date_issued

        if date_created_object := get_value_from_dict_or_list(
            origin_info, ["dateCreated"]
        ):
            if isinstance(date_created_object, dict):
                if date_created := date_created_object.get("$"):
                    metadata["date_created"] = date_created
            elif isinstance(date_created_object, list):
                # Approximate dates have a start and an end
                # [{'encoding': 'w3cdtf', 'keyDate': 'yes',
                # 'point': 'start', 'qualifier': 'approximate', '$': '1990'},
                # {'encoding': 'w3cdtf', 'point': 'end',
                # 'qualifier': 'approximate', '$': '1999'}]
                start, end = None, None
                for item in date_created_object:
                    point = item.get("point")
                    if point == "start":
                        start = item.get("$")
                    elif point == "end":
                        end = item.get("$")
                if start:
                    metadata["date_created"] = f"{start}{f'-{end}' if end else ''}"

        if publisher := get_value_from_dict_or_list(origin_info, ["publisher", "$"]):
            metadata["publisher"] = publisher

        if physical_description := get_value_from_dict_or_list(
            mods, ["physicalDescription", "note", "$"]
        ):
            metadata["physical_description"] = physical_description

        return metadata


def main():
    logger.info("Begin: NYPL data ingestion")
    ingester = NyplDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
