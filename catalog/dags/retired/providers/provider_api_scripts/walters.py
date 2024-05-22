"""
Content Provider:       Walters Art Museum

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the images and the
                        respective meta-data.

Notes:                  <http://api.thewalters.org/>
                        Rate limit: 250000 Per Day Per Key
"""

import logging

from airflow.models import Variable
from common.loader import provider_details as prov
from common.requester import DelayedRequester
from common.storage.image import ImageStore


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

DELAY = 1
LIMIT = 250000
PROVIDER = prov.WALTERS_DEFAULT_PROVIDER
REQUEST_TYPE = "objects"
ENDPOINT = f"https://api.thewalters.org/v1/{REQUEST_TYPE}"
API_KEY = Variable.get("API_KEY_WALTERS_ART_MUSEUM", default_var=None)
MUSEUM_SITE = "https://art.thewalters.org"
LICENSE = "CC0 1.0"

# The API takes api_key as a query and not as a header
DEFAULT_QUERY_PARAMS = {"accept": "json", "pageSize": 100, "orderBy": "classification"}

QUERY_CLASSIFICATION = [
    "Miniatures",
    "Stained & Painted Glass",
    "Lacquer & Inlay",
    "Ceramics",
    "Precious Stones & Gems",
    "Pearl, Horn, Coral & Shell",
    "Sculpture",
    "Textiles",
    "Painting & Drawing",
    "Prints",
    "Coins & Medals",
    "Arms & Armor",
    "Mosaics & Cosmati",
    "Niello",
    "Wood",
    "Enamels",
    "Manuscripts & Rare Books",
    "Ivory & Bone",
    "Mummies & Cartonnage",
    "Timepieces, Clocks & Watches",
    "Glasswares",
    "Metal",
    "Gold, Silver & Jewelry",
    "Stone",
    "Resin, Wax & Composite",
    "Leather",
]

delayed_requester = DelayedRequester(DELAY)
image_store = ImageStore(provider=PROVIDER)


def main():
    logger.info("Begin: Walters Art Museum provider script.")

    for class_param in QUERY_CLASSIFICATION:
        logger.info(f"Obtaining Images of Classification: {class_param}")
        image_list = _get_image_list(class_param)
        _ = _process_image_list(image_list)

    total_images = image_store.commit()
    logger.info(f"Total Images: {total_images}")
    logger.info("Terminating Script!")


def _get_image_list(class_param, endpoint=ENDPOINT, retries=5):
    image_list = []
    page = 1
    cond = True
    while cond:
        query_params = _build_query_param(class_param=class_param, page=page)
        page += 1
        json_response_inpydict_form = delayed_requester.get_response_json(
            endpoint=endpoint,
            retries=retries,
            query_params=query_params,
        )

        items_list = _extract_items_list_from_json(json_response_inpydict_form)
        if items_list is None:
            break
        for img in items_list:
            image_list.append(img)

        if json_response_inpydict_form.get("NextPage") is not True:
            cond = False

    if len(image_list) == 0:
        logger.warning("No more tries remaining. Returning Nonetypes.")
        return None
    else:
        return image_list


def _build_query_param(
    class_param=None, default_query_params=None, apikey=API_KEY, page=1
):
    if default_query_params is None:
        default_query_params = DEFAULT_QUERY_PARAMS
    query_params = default_query_params.copy()
    query_params.update({"classification": class_param, "apikey": apikey, "Page": page})

    return query_params


def _extract_items_list_from_json(json_response):
    if (
        json_response is None
        or str(json_response.get("ReturnStatus")).lower() != "true"
        or json_response.get("Items") is None
        or len(json_response.get("Items")) == 0
    ):
        items_list = None
    else:
        items_list = json_response.get("Items")

    return items_list


def _process_image_list(image_list):
    total_images = 0
    if image_list is not None:
        for img in image_list:
            total_images = _process_image(img)

    return total_images


def _process_image(img):
    logger.debug(f"Processing Image: {img}")

    foreign_landing_url = img.get("ResourceURL")
    image_url = img.get("PrimaryImage", {}).get("Raw")
    license_url = "https://creativecommons.org/publicdomain/zero/1.0/"
    foreign_identifier = img.get("ObjectNumber")
    creator, creator_url = _get_creator_info(img)
    title = img.get("Title")
    meta_data = _get_image_meta_data(img)

    return image_store.add_item(
        foreign_landing_url=foreign_landing_url,
        image_url=image_url,
        license_url=license_url,
        foreign_identifier=foreign_identifier,
        creator=creator,
        creator_url=creator_url,
        title=title,
        meta_data=meta_data,
    )


def _get_creator_info(img):
    creator, creator_url = None, None
    creator = img.get("Creator")
    if creator:
        creator_url = f"{MUSEUM_SITE}/browse/{creator.lower()}"

    return creator, creator_url


def _get_image_meta_data(img):
    image_meta_data = {
        "ObjectNumber": img.get("ObjectNumber"),
        "PublicAccessDate": img.get("PublicAccessDate"),
        "Collection": img.get("Collection"),
        "Medium": img.get("Medium"),
        "Classification": img.get("Classification"),
        "Description": img.get("Description"),
        "CreditLine": img.get("CreditLine"),
    }
    return {k: v for k, v in image_meta_data.items() if v is not None}


if __name__ == "__main__":
    main()
