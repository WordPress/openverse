"""
Content Provider:       Metropolitan Museum of Art

ETL Process:            Use the API to identify all CC0 artworks.

Output:                 TSV file containing the image, their respective
                        meta-data.

Notes:                  https://metmuseum.github.io/
                        No rate limit specified.
"""

import argparse
import logging

from common.licenses import get_license_info
from common.requester import DelayedRequester
from common.storage.image import ImageStore


DELAY = 1.0  # time delay (in seconds)
PROVIDER = "met"
ENDPOINT = "https://collectionapi.metmuseum.org/public/collection/v1/objects"
DEFAULT_LICENSE_INFO = get_license_info(license_="cc0", license_version="1.0")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

delayed_requester = DelayedRequester(DELAY)
image_store = ImageStore(provider=PROVIDER)


def main(date=None):
    """
    This script pulls the data for a given date from the Metropolitan
    Museum of Art API, and writes it into a .TSV file to be eventually
    read into our DB.

    Required Arguments:

    date:  Date String in the form YYYY-MM-DD.  This is the date for
           which running the script will pull data.
    """

    logger.info(f"Begin: Met Museum API requests for date: {date}")

    fetch_the_object_id = _get_object_ids(date)
    if fetch_the_object_id:
        logger.info(f"Total object found {fetch_the_object_id[0]}")
        _extract_the_data(fetch_the_object_id[1])

    total_images = image_store.commit()
    logger.info(f"Total CC0 images received {total_images}")


def _get_object_ids(date, endpoint=ENDPOINT):
    query_params = ""
    if date:
        query_params = {"metadataDate": date}

    response = _get_response_json(query_params, endpoint)

    if response:
        total_object_ids = response["total"]
        object_ids = response["objectIDs"]
    else:
        logger.warning("No content available")
        return None
    return [total_object_ids, object_ids]


def _get_response_json(
    query_params,
    endpoint,
    retries=5,
):
    response_json = delayed_requester.get_response_json(
        endpoint, query_params=query_params, retries=retries
    )

    return response_json


def _extract_the_data(object_ids):
    for i in object_ids:
        _get_data_for_image(i)


def _get_data_for_image(object_id):
    object_json = _get_and_validate_object_json(object_id)
    if not object_json:
        logger.warning(f"Could not retrieve object_json for object_id: {object_id}")
        return

    main_image = object_json.get("primaryImage")
    main_thumbnail = object_json.get("primaryImageSmall")
    other_images = object_json.get("additionalImages", [])
    image_list = [(main_image, main_thumbnail)] + [(i, None) for i in other_images]

    meta_data = _create_meta_data(object_json)

    for img, thumb in image_list:
        foreign_id = _build_foreign_id(object_id, img)
        image_store.add_item(
            foreign_landing_url=object_json.get("objectURL"),
            image_url=img,
            thumbnail_url=thumb,
            license_info=DEFAULT_LICENSE_INFO,
            foreign_identifier=foreign_id,
            creator=object_json.get("artistDisplayName"),
            title=object_json.get("title"),
            meta_data=meta_data,
        )


def _get_and_validate_object_json(object_id, endpoint=ENDPOINT):
    object_endpoint = f"{endpoint}/{object_id}"
    object_json = _get_response_json(None, object_endpoint)
    if not object_json.get("isPublicDomain"):
        logger.warning("CC0 license not detected")
        object_json = None
    return object_json


def _build_foreign_id(object_id, image_url):
    unique_identifier = image_url.split("/")[-1].split(".")[0]
    return f"{object_id}-{unique_identifier}"


def _create_meta_data(object_json):
    meta_data = {
        "accession_number": object_json.get("accessionNumber"),
        "classification": object_json.get("classification"),
        "culture": object_json.get("culture"),
        "date": object_json.get("objectDate"),
        "medium": object_json.get("medium"),
        "credit_line": object_json.get("creditLine"),
    }
    meta_data = {k: v for k, v in meta_data.items() if v is not None}
    return meta_data


if __name__ == "__main__":
    mode = "date :"
    parser = argparse.ArgumentParser(
        description="Metropolitan Museum of Art API", add_help=True
    )
    parser.add_argument(
        "--date", help="Fetches all the artwork uploaded after given date"
    )
    args = parser.parse_args()
    if args.date:
        date = args.date

    else:
        date = None
    logger.info("Processing images")

    main(date)
