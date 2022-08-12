"""
Content Provider:       Europeana

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the images and the
                        respective meta-data.

Notes:                  https://www.europeana.eu/api/v2/search.json
"""

import argparse
import logging
from datetime import datetime, timedelta, timezone

from airflow.models import Variable
from common.licenses import get_license_info
from common.loader import provider_details as prov
from common.requester import DelayedRequester
from common.storage.image import ImageStore
from requests.exceptions import JSONDecodeError


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

DELAY = 30.0
RESOURCES_PER_REQUEST = "100"
PROVIDER = prov.EUROPEANA_DEFAULT_PROVIDER
API_KEY = Variable.get("API_KEY_EUROPEANA", default_var=None)
ENDPOINT = "https://www.europeana.eu/api/v2/search.json?"
# SUB_PROVIDERS is a collection of providers within europeana which are
# valuable to a broad audience
SUB_PROVIDERS = prov.EUROPEANA_SUB_PROVIDERS

RESOURCE_TYPE = "IMAGE"
REUSE_TERMS = ["open", "restricted"]

DEFAULT_QUERY_PARAMS = {
    "profile": "rich",
    "reusability": REUSE_TERMS,
    "sort": ["europeana_id+desc", "timestamp_created+desc"],
    "rows": RESOURCES_PER_REQUEST,
    "media": "true",
    "start": 1,
    "qf": [f"TYPE:{RESOURCE_TYPE}", "provider_aggregation_edm_isShownBy:*"],
}

delayed_requester = DelayedRequester(DELAY)
image_store = ImageStore(provider=PROVIDER)


def main(date):
    logger.info(f"Processing Europeana API for date: {date}")

    start_timestamp, end_timestamp = _derive_timestamp_pair(date)
    _get_pagewise(start_timestamp, end_timestamp)

    total_images = image_store.commit()
    logger.info(f"Total images: {total_images}")
    logger.info("Terminated!")


def _get_pagewise(start_timestamp, end_timestamp):
    cursor = "*"

    while cursor is not None:
        image_list, next_cursor, total_number_of_images = _get_image_list(
            start_timestamp, end_timestamp, cursor
        )

        if next_cursor is None:
            break

        cursor = next_cursor

        if image_list is not None:
            images_stored = _process_image_list(image_list)
            logger.info(f"Images stored: {images_stored} of {total_number_of_images}")

        else:
            logger.warning("No image data!  Attempting to continue")


def _get_image_list(
    start_timestamp,
    end_timestamp,
    cursor,
    endpoint=ENDPOINT,
    max_tries=6,  # one original try, plus 5 retries
):
    try_number = 0
    image_list, next_cursor, total_number_of_images = (None, None, None)
    for try_number in range(max_tries):

        query_param_dict = _build_query_param_dict(
            start_timestamp, end_timestamp, cursor
        )

        response = delayed_requester.get(
            endpoint,
            params=query_param_dict,
        )

        logger.debug("response.status_code: {response.status_code}")
        response_json = _extract_response_json(response)
        (
            image_list,
            next_cursor,
            total_number_of_images,
        ) = _extract_image_list_from_json(response_json)

        if image_list is not None:
            break

    if try_number == max_tries - 1 and (image_list is None or next_cursor is None):
        logger.warning("No more tries remaining. Returning None types.")
    return image_list, next_cursor, total_number_of_images


def _extract_response_json(response):
    if response is not None and response.status_code == 200:
        try:
            response_json = response.json()
        except JSONDecodeError as e:
            logger.warning(f"Could not get image_data json.\n{e}")
            response_json = None
    else:
        response_json = None

    return response_json


def _extract_image_list_from_json(response_json):
    if response_json is None or str(response_json.get("success")) != "True":
        image_list, next_cursor, total_number_of_images = None, None, None
    else:
        image_list = response_json.get("items")
        next_cursor = response_json.get("nextCursor")
        total_number_of_images = response_json.get("totalResults")

    return image_list, next_cursor, total_number_of_images


def _process_image_list(image_list):
    prev_total = 0
    total_images = 0
    for image_data in image_list:
        total_images = _process_image_data(image_data)
        if total_images is None:
            total_images = prev_total
        else:
            prev_total = total_images

    return total_images


def _process_image_data(image_data, sub_providers=SUB_PROVIDERS, provider=PROVIDER):
    logger.debug(f"Processing image data: {image_data}")
    license_url = _get_license_url(image_data.get("rights"))
    image_url = image_data.get("edmIsShownBy")[0]
    foreign_landing_url = _get_foreign_landing_url(image_data)
    foreign_id = image_data.get("id")
    title = image_data.get("title")[0]
    meta_data = _create_meta_data_dict(image_data)

    data_providers = set(meta_data["dataProvider"])
    eligible_sub_providers = {
        s for s in sub_providers if sub_providers[s] in data_providers
    }
    if len(eligible_sub_providers) > 1:
        raise Exception(
            f"More than one sub-provider identified for the "
            f"image with foreign ID {foreign_id}"
        )
    source = (
        eligible_sub_providers.pop() if len(eligible_sub_providers) == 1 else provider
    )

    license_info = get_license_info(license_url=license_url)

    return image_store.add_item(
        foreign_landing_url=foreign_landing_url,
        image_url=image_url,
        license_info=license_info,
        foreign_identifier=foreign_id,
        title=title,
        meta_data=meta_data,
        source=source,
    )


def _get_license_url(license_field):
    if len(license_field) > 1:
        logger.warning("More than one license field found")
    for license_ in license_field:
        if "creativecommons" in license_:
            return license_
    return None


def _get_foreign_landing_url(image_data):
    original_url = image_data.get("edmIsShownAt")
    if original_url is not None:
        return original_url[0]
    europeana_url = image_data.get("guid")
    return europeana_url


def _create_meta_data_dict(image_data):
    meta_data = {
        "country": image_data.get("country"),
        "dataProvider": image_data.get("dataProvider"),
        "description": _get_description(image_data),
    }

    return {k: v for k, v in meta_data.items() if v is not None}


def _get_description(image_data):
    if (
        image_data.get("dcDescriptionLangAware") is not None
        and image_data.get("dcDescriptionLangAware").get("en") is not None
    ):
        description = image_data.get("dcDescriptionLangAware").get("en")[0]
    elif (
        image_data.get("dcDescriptionLangAware") is not None
        and image_data.get("dcDescriptionLangAware").get("def") is not None
    ):
        description = image_data.get("dcDescriptionLangAware").get("def")[0]
    elif image_data.get("dcDescription") is not None:
        description = image_data.get("dcDescription")[0]
    else:
        description = None

    description = description.strip() if description is not None else ""

    return description


def _build_query_param_dict(
    start_timestamp,
    end_timestamp,
    cursor,
    api_key=API_KEY,
    default_query_param=None,
):
    if default_query_param is None:
        default_query_param = DEFAULT_QUERY_PARAMS
    query_param_dict = default_query_param.copy()
    query_param_dict.update(
        wskey=api_key,
        query=f"timestamp_created:[{start_timestamp} TO {end_timestamp}]",
        cursor=cursor,
    )
    return query_param_dict


def _derive_timestamp_pair(date):
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    utc_date = date_obj.replace(tzinfo=timezone.utc)
    start_timestamp = utc_date.isoformat()
    end_timestamp = (utc_date + timedelta(days=1)).isoformat()

    start_timestamp = start_timestamp.replace("+00:00", "Z")
    end_timestamp = end_timestamp.replace("+00:00", "Z")

    return start_timestamp, end_timestamp


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
