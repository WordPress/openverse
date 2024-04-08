"""
Content Provider:   Smithsonian

ETL Process:        Use the API to identify all CC licensed images.

Output:             TSV file containing the images and the respective meta-data.

Notes:              https://api.si.edu/openaccess/api/v1.0/search
"""

import logging

from airflow.exceptions import AirflowException
from airflow.models import Variable
from retry import retry

from common import constants
from common.licenses import get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)


class SmithsonianDataIngester(ProviderDataIngester):
    providers = {"image": prov.SMITHSONIAN_DEFAULT_PROVIDER}
    sub_providers = prov.SMITHSONIAN_SUB_PROVIDERS
    base_endpoint = "https://api.si.edu/openaccess/api/v1.0/"
    endpoint = f"{base_endpoint}search"
    delay = 5.0
    batch_limit = 1000
    hash_prefix_length = 2
    description_types = {
        "description",
        "summary",
        "caption",
        "notes",
        "description (brief)",
        "description (spanish)",
        "description (brief spanish)",
        "gallery label",
        "exhibition label",
        "luce center label",
        "publication label",
        "new acquisition label",
    }

    # `creator_types` should have lower-case strings as keys, and integers as values.
    # The integers given the preference order of the different creator types, with
    # lower being more preferred. No preference is implied between two creator
    # types with the same integer value.
    creator_types = {
        "artist": 0,
        "artist/maker": 0,
        "attributed to": 0,
        "author": 0,
        "created_by": 0,
        "creator": 0,
        "created by": 0,
        "model maker": 0,
        "modeler": 0,
        "photographer": 0,
        "photograph by": 0,
        "written by": 0,
        "architect": 1,
        "designer": 1,
        "designed by": 1,
        "illustrator": 1,
        "illustrated by": 1,
        "cartoonist": 1,
        "weaver": 1,
        "composer": 1,
        "composed by": 1,
        "embroiderer": 1,
        "landscape architect": 1,
        "calligrapher": 1,
        "sculptor": 1,
        "jeweler": 1,
        "potter": 1,
        "ceramist": 1,
        "compiled by": 2,
        "engraver": 2,
        "etcher": 2,
        "maker": 2,
        "silversmith": 2,
        "producer": 2,
        "produced by": 2,
        "metal worker": 2,
        "carver": 2,
        "cartographer": 2,
        "print maker": 3,
        "painter": 3,
        "after": 3,
        "inventor": 3,
        "lithographer": 3,
        "attribution": 3,
        "former attribution": 3,
        "manufactured by": 4,
        "manufacturer": 4,
        "published by": 4,
        "publisher": 4,
        "editor": 4,
        "patentee": 5,
        "collector": 6,
    }

    tag_types = ("date", "object_type", "topic", "place")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = Variable.get("API_KEY_DATA_GOV")
        self.units_endpoint = f"{self.base_endpoint}terms/unit_code"
        self.license_info = get_license_info(
            license_url="https://creativecommons.org/publicdomain/zero/1.0/"
        )

    def get_next_query_params(self, prev_query_params: dict | None, **kwargs) -> dict:
        # On the first request, `prev_query_params` will be `None`. We can detect this
        # and return our default params.
        query_string = "online_media_type:Images AND media_usage:CC0"
        if hash_prefix := kwargs.get("hash_prefix"):
            query_string += f" AND hash:{hash_prefix}*"

        if not prev_query_params:
            return {
                "api_key": self.api_key,
                "q": query_string,
                "rows": self.batch_limit,
                "start": 0,
            }
        else:
            return {
                **prev_query_params,
                "start": prev_query_params["start"] + self.batch_limit,
            }

    def get_batch_data(self, response_json) -> list | None:
        # Takes the raw API response from calling `get` on the endpoint, and returns
        # the list of records to process.
        if response_json:
            rows = response_json.get("response", {}).get("rows")
            return self._check_type(rows, list)
        return None

    def get_record_data(self, data: dict) -> dict | list[dict] | None:
        # Parse out the necessary info from the record data into a dictionary.
        images = []
        if image_list := self._get_image_list(data):
            if (foreign_landing_url := self._get_foreign_landing_url(data)) is None:
                return None

            meta_data = self._extract_meta_data(data)
            shared_image_data = {
                "foreign_landing_url": foreign_landing_url,
                "title": data.get("title"),
                "license_info": self.license_info,
                "source": self._extract_source(meta_data),
                "creator": self._get_creator(data),
                "meta_data": meta_data,
                "raw_tags": self._extract_tags(data),
                # TODO: Check if the following columns can be filled.
                # creator_url
                # thumbnail_url
                # filesize
                # filetype
                # category
                # watermarked
            }
            images += self._get_associated_images(image_list, shared_image_data)
        return images

    @retry(ValueError, tries=3, delay=1, backoff=2)
    def _get_unit_codes_from_api(self) -> set:
        query_params = {"api_key": self.api_key, "q": "online_media_type:Images"}
        response_json = self.get_response_json(
            endpoint=self.units_endpoint, query_params=query_params
        )
        unit_codes_from_api = set(response_json.get("response", {}).get("terms", []))

        if len(unit_codes_from_api) == 0:
            raise ValueError("No unit codes received")

        logger.debug(f"\nUnit codes received:\n{unit_codes_from_api}\n")
        return unit_codes_from_api

    def _get_new_and_outdated_unit_codes(
        self, unit_codes_from_api: set
    ) -> tuple[set, set]:
        current_unit_codes = set().union(*self.sub_providers.values())
        new_unit_codes = unit_codes_from_api - current_unit_codes
        outdated_unit_codes = current_unit_codes - unit_codes_from_api
        return new_unit_codes, outdated_unit_codes

    def validate_unit_codes_from_api(self) -> None:
        """
        Validate the SMITHSONIAN_SUB_PROVIDERS dictionary.

        This raises an exception if human intervention is needed to add or
        remove unit codes.
        """
        logger.info("Validating Smithsonian sub-providers...")
        unit_codes_from_api = self._get_unit_codes_from_api()
        new_unit_codes, outdated_unit_codes = self._get_new_and_outdated_unit_codes(
            unit_codes_from_api
        )

        if bool(new_unit_codes) or bool(outdated_unit_codes):
            message = (
                "\n*Updates needed to the SMITHSONIAN_SUB_PROVIDERS dictionary*:\n\n"
            )

            if bool(new_unit_codes):
                codes_string = "\n".join(f"  - `{code}`" for code in new_unit_codes)
                message += "New unit codes must be added:\n"
                message += codes_string
                message += "\n"

            if bool(outdated_unit_codes):
                codes_string = "\n".join(
                    f"  - `{code}`" for code in outdated_unit_codes
                )
                message += "Outdated unit codes must be deleted:\n"
                message += codes_string

            logger.info(message)
            raise AirflowException(message)

    def _get_hash_prefixes(self):
        max_prefix = "f" * self.hash_prefix_length
        format_string = f"0{self.hash_prefix_length}x"
        for h in range(int(max_prefix, 16) + 1):
            yield format(h, format_string)

    @staticmethod
    def _check_type(unknown_input, required_type):
        """
        Ensure that the input is of the required type.

        Required Arguments:

        unknown_input:  This can be anything
        required_type:  built-in type name/constructor

        This function will check whether the unknown_input is of type
        required_type. If it is, it returns the unknown_input value
        unchanged. If not, will return the DEFAULT VALUE FOR THE TYPE
        required_type. So, if unknown_input is a float 3.0 and the
        required_type is int, this function will return 0.

        This function will work for required_type in:
        str, int, float, complex, list, tuple, dict, set, bool, and bytes.

        This function will create a relatively high-level log message
        whenever it has to initialize a default value for type
        required_type.
        """
        logger.debug(f"Ensuring {unknown_input} is of type {required_type}")
        if unknown_input is None:
            logger.debug(f"{unknown_input} is of type {type(unknown_input)}.")
            typed_input = required_type()
        elif type(unknown_input) != required_type:
            logger.info(
                f"{unknown_input} is of type {type(unknown_input)}"
                f" rather than {required_type}."
            )
            typed_input = required_type()
        else:
            typed_input = unknown_input
        return typed_input

    def _get_content_dict(self, row, field):
        logger.debug(f"Getting `{field}` from row")
        content = self._check_type(row.get("content"), dict)
        return self._check_type(content.get(field), dict)

    def _get_image_list(self, row):
        dnr_dict = self._get_content_dict(row, "descriptiveNonRepeating")
        online_media = self._check_type(dnr_dict.get("online_media"), dict)
        return self._check_type(online_media.get("media"), list)

    @staticmethod
    def _get_associated_images(image_list, partial_image_data: dict) -> list:
        images = []
        for image_data in image_list:
            usage = image_data.get("usage", {}).get("access")
            if image_data.get("type") != "Images" or usage != "CC0":
                continue

            if not (url := image_data.get("content")):
                continue

            if not (foreign_identifier := image_data.get("idsId")):
                continue

            images.append(
                {
                    **partial_image_data,
                    "url": url,
                    "foreign_identifier": foreign_identifier,
                }
            )
        return images

    def _get_foreign_landing_url(self, row):
        logger.debug("Getting foreign_landing_url from row")
        dnr_dict = self._get_content_dict(row, "descriptiveNonRepeating")
        foreign_landing_url = dnr_dict.get("record_link")
        if foreign_landing_url is None:
            foreign_landing_url = dnr_dict.get("guid")

        return foreign_landing_url

    def _extract_meta_data(self, row) -> dict:
        freetext = self._get_content_dict(row, "freetext")
        descriptive_non_repeating = self._get_content_dict(
            row, "descriptiveNonRepeating"
        )
        description, label_texts = "", ""
        notes = self._check_type(freetext.get("notes"), list)

        for note in notes:
            label = self._check_type(note.get("label", ""), str)
            if label.lower().strip() in self.description_types:
                description += " " + self._check_type(note.get("content", ""), str)
            elif label.lower().strip() == "label text":
                label_texts += " " + self._check_type(note.get("content", ""), str)

        meta_data = {
            "unit_code": descriptive_non_repeating.get("unit_code"),
            "data_source": descriptive_non_repeating.get("data_source"),
        }

        if description:
            meta_data.update(description=description.strip())
        if label_texts:
            meta_data.update(label_text=label_texts.strip())

        return {k: v for (k, v) in meta_data.items() if v is not None}

    def _extract_source(self, meta_data):
        unit_code = meta_data.get("unit_code").strip()
        source = next(
            (s for s in self.sub_providers if unit_code in self.sub_providers[s]), None
        )
        if source is None:
            raise Exception(f"An unknown unit code value {unit_code} encountered ")
        return source

    def _get_creator(self, row):
        freetext = self._get_content_dict(row, "freetext")
        indexed_structured = self._get_content_dict(row, "indexedStructured")
        ordered_freetext_creator_objects = sorted(
            [
                i
                for i in self._check_type(freetext.get("name"), list)
                if isinstance(i, dict)
                and (
                    self._check_type(i.get("label"), str).lower() in self.creator_types
                )
                and (self._check_type(i.get("content"), str))
                and ("unknown" not in i.get("content").lower())
            ],
            key=lambda x: self.creator_types[x["label"].lower()],
        )

        indexed_structured_creator_generator = (
            i["content"]
            for i in self._check_type(indexed_structured.get("name"), list)
            if isinstance(i, dict)
            and (self._check_type(i.get("type"), str).lower() == "personal_main")
            and (self._check_type(i.get("content"), str))
        )

        if ordered_freetext_creator_objects:
            first_creator_object = ordered_freetext_creator_objects[0]
            top_priority = self.creator_types[first_creator_object["label"].lower()]

            creators_list = [
                c["content"]
                for c in ordered_freetext_creator_objects
                if top_priority == self.creator_types[c["label"].lower()]
            ]

            creator = (
                "; ".join(creators_list[:-1]) + " and " + creators_list[-1]
                if len(creators_list) > 1
                else creators_list[0]
            )

        else:
            creator = None

        if creator is None:
            logger.debug(f"No creator found in freetext:  {freetext}")
            creator = next(indexed_structured_creator_generator, None)
        if creator is None:
            logger.debug(
                f"No creator found in indexed_structured:  {indexed_structured}"
            )
        return creator

    def _extract_tags(self, row):
        indexed_structured = self._get_content_dict(row, "indexedStructured")
        tag_lists_generator = (
            self._check_type(indexed_structured.get(key), list)
            for key in self.tag_types
        )
        return [tag for tag_list in tag_lists_generator for tag in tag_list if tag]

    def ingest_records(self, **kwargs) -> None:
        self.validate_unit_codes_from_api()
        for hash_prefix in self._get_hash_prefixes():
            logger.debug(f"Getting records for hash prefix {hash_prefix}")
            super().ingest_records(hash_prefix=hash_prefix)


def main():
    ingester = SmithsonianDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
