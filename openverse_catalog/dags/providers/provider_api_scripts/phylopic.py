"""
Content Provider:       PhyloPic

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the image,
                        their respective meta-data.

Notes:                  http://phylopic.org/api/
                        No rate limit specified.
"""

import argparse
import logging
from datetime import date, timedelta

from common.licenses import get_license_info
from common.requester import DelayedRequester
from common.storage.image import ImageStore


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

DELAY = 5.0
HOST = "phylopic.org"
ENDPOINT = f"http://{HOST}/api/a"
PROVIDER = "phylopic"
LIMIT = 5
# Default number of days to process if date_end is not defined
DEFAULT_PROCESS_DAYS = 7

delayed_requester = DelayedRequester(DELAY)
image_store = ImageStore(provider=PROVIDER)


def main(date_start: str = "all", date_end: str = None):
    """
    This script pulls the data for a given date from the PhyloPic
    API, and writes it into a .TSV file to be eventually read
    into our DB.

    Required Arguments:

    date_start:  Date String in the form YYYY-MM-DD. This date defines the beginning
                 of the range that the script will pull data from.
    date_end:    Date String in the form YYYY-MM-DD. Similar to `date_start`, this
                 defines the end of the range of data pulled. Defaults to
                 DEFAULT_PROCESS_DAYS (7) if undefined.
    """

    offset = 0

    logger.info("Begin: PhyloPic API requests")

    if date_start == "all":
        logger.info("Processing all images")
        param = {"offset": offset}

        image_count = _get_total_images()
        logger.info(f"Total images: {image_count}")

        while offset <= image_count:
            _add_data_to_buffer(**param)
            offset += LIMIT
            param = {"offset": offset}

    else:
        if date_end is None:
            date_end = _compute_date_range(date_start)
        param = {"date_start": date_start, "date_end": date_end}

        logger.info(f"Processing from {date_start} to {date_end}")
        _add_data_to_buffer(**param)

    image_store.commit()

    logger.info("Terminated!")


def _add_data_to_buffer(**kwargs):
    endpoint = _create_endpoint_for_IDs(**kwargs)
    IDs = _get_image_IDs(endpoint)

    for id_ in IDs:
        if id_ is not None:
            details = _get_meta_data(id_)
            if details is not None:
                image_store.add_item(**details)


def _get_total_images():
    # Get the total number of PhyloPic images
    total = 0
    endpoint = "http://phylopic.org/api/a/image/count"
    result = delayed_requester.get_response_json(endpoint, retries=2)

    if result and result.get("success") is True:
        total = result.get("result", 0)

    return total


def _create_endpoint_for_IDs(**kwargs):
    limit = LIMIT

    if ((date_start := kwargs.get("date_start")) is not None) and (
        (date_end := kwargs.get("date_end")) is not None
    ):
        # Get a list of objects uploaded/updated from a given date to another date
        # http://phylopic.org/api/#method-image-time-range
        endpoint = (
            f"http://phylopic.org/api/a/image/list/modified/{date_start}/{date_end}"
        )

    elif (offset := kwargs.get("offset")) is not None:
        # Get all images and limit the results for each request.
        endpoint = f"http://phylopic.org/api/a/image/list/{offset}/{limit}"

    else:
        raise ValueError("No valid selection criteria found!")
    return endpoint


def _get_image_IDs(_endpoint):
    result = delayed_requester.get_response_json(_endpoint, retries=2)
    image_IDs = []

    if result and result.get("success") is True:
        data = list(result.get("result"))

        if len(data) > 0:
            for i in range(len(data)):
                image_IDs.append(data[i].get("uid"))

    if not image_IDs:
        logger.warning("No content available!")
        return [None]

    return image_IDs


def _get_meta_data(_uuid):
    logger.info(f"Processing UUID: {_uuid}")

    base_url = "http://phylopic.org"
    meta_data = {}
    endpoint = (
        f"http://phylopic.org/api/a/image/{_uuid}?options=credit+"
        "licenseURL+pngFiles+submitted+submitter+taxa+canonicalName"
        "+string+firstName+lastName"
    )
    request = delayed_requester.get_response_json(endpoint, retries=2)
    if request and request.get("success") is True:
        result = request["result"]
    else:
        return None

    license_url = result.get("licenseURL")

    meta_data["taxa"], title = _get_taxa_details(result)

    foreign_url = f"{base_url}/image/{_uuid}"

    (creator, meta_data["credit_line"], meta_data["pub_date"]) = _get_creator_details(
        result
    )

    img_url, width, height = _get_image_info(result, _uuid)

    if img_url is None:
        return None

    details = {
        "foreign_identifier": _uuid,
        "foreign_landing_url": foreign_url,
        "image_url": img_url,
        "license_info": get_license_info(license_url=license_url),
        "width": str(width),
        "height": str(height),
        "creator": creator,
        "title": title,
        "meta_data": meta_data,
    }
    return details


def _get_creator_details(result):
    credit_line = None
    pub_date = None
    creator = None
    first_name = result.get("submitter", {}).get("firstName")
    last_name = result.get("submitter", {}).get("lastName")
    if first_name and last_name:
        creator = f"{first_name} {last_name}".strip()

    if result.get("credit"):
        credit_line = result.get("credit").strip()
        pub_date = result.get("submitted").strip()

    return creator, credit_line, pub_date


def _get_taxa_details(result):
    taxa = result.get("taxa", [])
    # [0].get('canonicalName', {}).get('string')
    taxa_list = None
    title = ""
    if taxa:
        taxa = [
            _.get("canonicalName") for _ in taxa if _.get("canonicalName") is not None
        ]
        taxa_list = [_.get("string", "") for _ in taxa]

    if taxa_list:
        title = taxa_list[0]

    return taxa_list, title


def _get_image_info(result, _uuid):
    base_url = "http://phylopic.org"
    img_url = ""
    width = ""
    height = ""

    image_info = result.get("pngFiles")
    img = []
    if image_info:
        img = list(filter(lambda x: (int(str(x.get("width", "0"))) >= 257), image_info))
        img = sorted(img, key=lambda x: x["width"], reverse=True)

    if len(img) > 0:
        img_url = img[0].get("url")
        img_url = f"{base_url}{img_url}"
        width = img[0].get("width")
        height = img[0].get("height")

    if img_url == "":
        logging.warning(f"Image not detected in url: {base_url}/image/{_uuid}")
        return None, None, None
    else:
        return img_url, width, height


def _compute_date_range(date_start: str, days: int = DEFAULT_PROCESS_DAYS) -> str:
    """
    Given an ISO formatted date string and a number of days, compute the
    ISO string that represents the start date plus the days provided.
    """
    date_end = date.fromisoformat(date_start) + timedelta(days=days)
    return date_end.isoformat()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PhyloPic API Job", add_help=True)
    parser.add_argument(
        "--date-start",
        default="all",
        help="Identify all images starting from a particular date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--date-end",
        default=None,
        help="Used in conjunction with --date-start, identify all images ending on "
        f"a particular date (YYYY-MM-DD), defaults to {DEFAULT_PROCESS_DAYS} "
        "if not defined.",
    )

    args = parser.parse_args()

    main(args.date_start, args.date_end)
