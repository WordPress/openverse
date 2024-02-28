"""
Content Provider:       Europeana

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the images and the
                        respective meta-data.

Notes:                  https://pro.europeana.eu/page/search
"""
import argparse
import functools
import logging
from datetime import datetime, timedelta, timezone

from airflow.models import Variable

import common
from common.licenses import LicenseInfo, get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)
logging.getLogger(common.urls.__name__).setLevel(logging.WARNING)


class EmptyRequiredFieldException(Exception):
    def __init__(self, method_name: str, value):
        super().__init__(f"`{method_name}` returned an empty value: {value}.")


def raise_if_empty(fn):
    """
    Raise an exception if the value returned by the wrapped function is empty.

    Used to decorate RecordBuilder methods for "required" fields to shortcut record
    building in the case where a record would be missing some required fields and be
    thrown out anyway.
    """

    @functools.wraps(fn)
    def inner(*args, **kwargs):
        value = fn(*args, **kwargs)

        if not value:
            raise EmptyRequiredFieldException(fn.__name__, value)

        return value

    return inner


class EuropeanaRecordBuilder:
    """
    Build records for Europeana.

    This small class contains the record building functionality and simplifies testing.
    """

    def get_record_data(self, data: dict) -> dict | None:
        try:
            item_data = data.get("item_webresource", {})
            record = {
                "foreign_landing_url": self._get_foreign_landing_url(data),
                "url": self._get_image_url(data),
                "foreign_identifier": self._get_foreign_identifier(data),
                "meta_data": self._get_meta_data_dict(data),
                "title": self._get_title(data),
                "license_info": self._get_license_info(data),
                "filetype": self._get_filetype(item_data),
                "filesize": self._get_filesize(item_data),
            } | self._get_image_dimensions(item_data)

            data_providers = set(record["meta_data"]["dataProvider"])
            eligible_sub_providers = {
                s
                for s in EuropeanaDataIngester.sub_providers
                if EuropeanaDataIngester.sub_providers[s] in data_providers
            }
            if len(eligible_sub_providers) > 1:
                raise Exception(
                    f"More than one sub-provider identified for the "
                    f"image with foreign ID {record['foreign_identifier']}"
                )

            record["source"] = (
                eligible_sub_providers.pop()
                if len(eligible_sub_providers) == 1
                else EuropeanaDataIngester.providers["image"]
            )
            return {k: v for k, v in record.items() if v is not None}
        except EmptyRequiredFieldException as exc:
            logger.warning("A required field was empty", exc_info=exc)
            return None

    @raise_if_empty
    def _get_image_url(self, data: dict) -> str | None:
        group = data.get("edmIsShownBy")
        if not group:
            return None
        url = group[0]
        # Some Europeana URLs may have prefixes, or reference Dropbox (which we can't
        # include in our catalog because we cannot access them directly ourselves).
        # E.g.: L-APC248-https://www.dropbox.com/s/i1pqizm1joof8y1/Belgium_Diptyque%20_MAR-SGP-CO1.jpg?raw=1
        if "dropbox.com" in url:
            return None
        return url

    @raise_if_empty
    def _get_foreign_identifier(self, data: dict) -> str | None:
        return data.get("id")

    @raise_if_empty
    def _get_title(self, data: dict) -> str | None:
        group = data.get("title")
        return group[0] if group else None

    @raise_if_empty
    def _get_license_info(self, data: dict) -> LicenseInfo | None:
        license_field = data.get("rights")
        if not license_field:
            return None

        if len(license_field) > 1:
            logger.warning("More than one license field found")
        for license_url in license_field:
            if "creativecommons" in license_url:
                return get_license_info(license_url=license_url)

        return None

    @raise_if_empty
    def _get_foreign_landing_url(self, data: dict) -> str:
        original_url = data.get("edmIsShownAt")
        if original_url:
            return original_url[0]
        europeana_url = data.get("guid")

        return europeana_url

    def _get_image_dimensions(self, item_data: dict) -> dict:
        width = item_data.get("ebucoreWidth")
        height = item_data.get("ebucoreHeight")
        if width and height:
            return {"width": width, "height": height}
        return {}

    def _get_filetype(self, item_data: dict) -> str:
        if filetype := item_data.get("ebucoreHasMimeType"):
            if "/" in filetype:
                return item_data.get("ebucoreHasMimeType").split("/")[1]
        return filetype

    def _get_filesize(self, item_data: dict) -> int:
        return item_data.get("ebucoreFileByteSize")

    def _get_meta_data_dict(self, data: dict) -> dict:
        meta_data = {
            "country": data.get("country"),
            "dataProvider": data.get("dataProvider"),
            "description": self._get_description(data),
        }

        return {k: v for k, v in meta_data.items() if v is not None}

    def _get_description(self, data: dict) -> str | None:
        description = None
        lang_aware_description = data.get("dcDescriptionLangAware")
        if lang_aware_description:
            description = lang_aware_description.get(
                "en"
            ) or lang_aware_description.get("def")

        if not description:  # cover None and []
            description = data.get("dcDescription")

        if description:
            return description[0].strip()

        return ""


class EuropeanaDataIngester(ProviderDataIngester):
    providers = {"image": prov.EUROPEANA_DEFAULT_PROVIDER}
    sub_providers = prov.EUROPEANA_SUB_PROVIDERS
    endpoint = "https://api.europeana.eu/record/v2/search.json?"
    delay = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Each response back from Europeana returns a `nextCursor`
        # property that needs to be passed to subsequent requests
        # as `cursor`. This allows us to systematically page
        # through the API data.
        self.cursor = None

        self.base_request_body = {
            "wskey": Variable.get("API_KEY_EUROPEANA", default_var=None),
            "profile": "rich",
            "reusability": ["open", "restricted"],
            "sort": ["europeana_id+desc", "timestamp_created+desc"],
            "rows": str(self.batch_limit),
            "media": "true",
            "start": 1,
            "qf": ["TYPE:IMAGE", "provider_aggregation_edm_isShownBy:*"],
            # As a dated DAG, Europeana accepts a ``query`` prop in the
            # request params that delineates the timestamps between which
            # records will have been added. The base class sets up the
            # ``self.date`` attribute for us, so we can construct that
            # ``query`` prop for the request params ahead of time.
            "query": self._get_timestamp_query_param(self.date),
            "cursor": "*",
        }

        self.item_params = {
            "wskey": Variable.get("API_KEY_EUROPEANA", default_var=None)
        }
        self.record_builder = EuropeanaRecordBuilder()

    def _get_timestamp_query_param(self, date):
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        utc_date = date_obj.replace(tzinfo=timezone.utc)
        start_timestamp = utc_date.isoformat()
        end_timestamp = (utc_date + timedelta(days=1)).isoformat()

        start_timestamp = start_timestamp.replace("+00:00", "Z")
        end_timestamp = end_timestamp.replace("+00:00", "Z")

        return f"timestamp_update:[{start_timestamp} TO {end_timestamp}]"

    def get_next_query_params(self, prev_query_params) -> dict:
        if not prev_query_params:
            return self.base_request_body

        return prev_query_params | {
            "cursor": self.cursor,
        }

    def get_should_continue(self, response_json: dict):
        self.cursor = response_json.get("nextCursor")

        return self.cursor is not None

    def get_batch_data(self, response_json: dict) -> None | list[dict]:
        if not response_json.get("success"):
            logger.warning("Request failed with ``success != True``")
            # No batch data to process if the request failed.
            return None

        return response_json.get("items")

    def get_record_data(self, data: dict) -> dict:
        return self.record_builder.get_record_data(
            data | {"item_webresource": self._get_additional_item_data(data)}
        )

    def _get_id_and_url(self, data) -> tuple:
        try:
            return (
                self.record_builder._get_foreign_identifier(data),
                self.record_builder._get_image_url(data),
            )
        except EmptyRequiredFieldException as exc:
            logger.warning("Missing id or url", exc_info=exc)
            return (None, None)

    def _get_additional_item_data(self, data) -> dict:
        # The Europeana requester uses a 3 second delay to avoid overwhelming the item
        # endpoint and to maintain at least a 30 second break between calls to the
        # search endpoint.
        (item_id, url) = self._get_id_and_url(data)
        if not (item_id and url):
            return {}
        item_response = self.get_response_json(
            query_params=self.item_params,
            endpoint=f"https://api.europeana.eu/record/v2{item_id}.json",
        )
        if not item_response or not item_response.get("success"):
            logger.warning("Item request failed no response or ``success != True``")
            return {}
        aggregations = item_response.get("object", {}).get("aggregations", [])
        for aggregation in aggregations:
            return next(
                (
                    resource
                    for resource in aggregation.get("webResources", [])
                    if (
                        resource.get("ebucoreHasMimeType", "").startswith("image")
                        and resource.get("about") == url
                    )
                ),
                {},
            )
        return {}


def main(date):
    logger.info(f"Begin: Europeana data ingestion for {date}")
    ingester = EuropeanaDataIngester(date)
    ingester.ingest_records()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Europeana API Job", add_help=True)
    parser.add_argument(
        "--date", help="Identify images uploaded on a date (format: YYYY-MM-DD)."
    )
    args = parser.parse_args()
    if args.date:
        date = args.date
    else:
        date_obj = datetime.now() - timedelta(days=2)
        date = datetime.strftime(date_obj, "%Y-%m-%d")

    main(date)
