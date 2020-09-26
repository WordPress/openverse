"""
Content Provider:       Walters Art Museum

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the images and the
                        respective meta-data.

Notes:                  http://api.thewalters.org/
                        Rate limit: 250000 Per Day Per Key
"""

import os
import logging
import common.requester as requester
import common.storage.image as image
from util.loader import provider_details as prov

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

DELAY = 1
LIMIT = 250000
PROVIDER = prov.WALTERS_DEFAULT_PROVIDER
REQUEST_TYPE = 'objects'
ENDPOINT = f'http://api.thewalters.org/v1/{REQUEST_TYPE}'
API_KEY = os.getenv('WALTERS_ART_MUSEUEM_KEY')
MUSEUM_SITE = "https://art.thewalters.org"
LICENSE = 'CC0 1.0'

# The API takes api_key as a query and not as a header
DEFAULT_QUERY_PARAMS = {
    'accept': 'json',
    'pageSize': 100,
    'orderBy': 'classification'
}

QUERY_CLASSIFICATION = [
    'Miniatures',
    'Stained & Painted Glass',
    'Lacquer & Inlay',
    'Ceramics',
    'Precious Stones & Gems',
    'Pearl, Horn, Coral & Shell',
    'Sculpture',
    'Textiles',
    'Painting & Drawing',
    'Prints',
    'Coins & Medals',
    'Arms & Armor',
    'Mosaics & Cosmati',
    'Niello',
    'Paper & Paper-Mache',
    'Wood',
    'Enamels',
    'Manuscripts & Rare Books',
    'Ivory & Bone',
    'Mummies & Cartonnage',
    'Timepieces, Clocks & Watches',
    'Glasswares',
    'Metal',
    'Gold, Silver & Jewelry',
    'Stone',
    'Resin, Wax & Composite',
    'Leather'
]

delayed_requester = requester.DelayedRequester(DELAY)
image_store = image.ImageStore(provider=PROVIDER)


def main():

    logger.info("Begin: Walters Art Museum provider script.")

    for class_param in QUERY_CLASSIFICATION:
        logger.info(f"Obtaining Images of Classfication: {class_param}")
        il = _get_image_list(class_param)
        _ = _process_image_list(il)

    total_images = image_store.commit()
    logger.info(f"Total Images: {total_images}")
    logger.info("Terminating Script!")


def _get_image_list(
        class_param,
        endpoint=ENDPOINT,
        retries=5
):
    image_list = []
    cond = True
    for num_tries in range(retries):
        while cond:
            query_param = _build_query_param(class_param)
            response_dict = delayed_requester.get(
                endpoint,
                params=query_param,
            )

            logger.debug("Response Status Code: {response_dict.status_code}")
            json_response_inpydict_form = _extract_response_json(response_dict)

            if json_response_inpydict_form is None:
                logger.warning("JSON response is None.")
                image_list = None
                break

            if json_response_inpydict_form.get("ReturnCode") != 200:
                break

            items_list = _extract_image_list_from_json(
                json_response_inpydict_form)
            for img in items_list:
                image_list.append(img)

            if json_response_inpydict_form.get("NextPage") is False:
                cond = False

        if image_list is not None:
            break

    if num_tries == retries - 1 and image_list is None:
        logger.warning("No more tries remaining. Returning Nonetypes.")
        return None
    else:
        # total_images = _process_image_list(image_list)
        # logger.info(f"Total Images obtained: {total_images}")
        return image_list


def _build_query_param(
        class_param=None,
        default_query_params=DEFAULT_QUERY_PARAMS,
        apikey=API_KEY
):
    query_param = default_query_params.copy()
    query_param.update(
        {
            'classification': class_param,
            'apikey': apikey
        }
    )

    return query_param


def _extract_response_json(response_dict):
    if response_dict is not None and response_dict.status_code == 200:
        try:
            json_response_inpydict_form = response_dict.json()
        except Exception as error:
            logger.warning(f"Could not get image data in JSON.\n{error}")
            json_response_inpydict_form = None
    else:
        json_response_inpydict_form = None

    return json_response_inpydict_form


def _extract_image_list_from_json(json_response_inpydict_form):
    if (
            json_response_inpydict_form is None
            or str(
                json_response_inpydict_form.get('ReturnStatus')
            ).lower() != 'true'
            or json_response_inpydict_form.get('Items') is None
            or len(json_response_inpydict_form.get('Items')) == 0
    ):
        image_list = None
    else:
        image_list = json_response_inpydict_form.get('Items')

    return image_list


def _process_image_list(image_list):
    total_images = 0
    if image_list is not None:
        for img in image_list:
            total_images = _process_image(img)

    return total_images


def _process_image(img):
    logger.debug(f'Processing Image: {img}')

    foreign_landing_url = _get_foreign_landing_url(img)
    image_url = _get_image_url(img)
    thumbnail_url = _get_thumbnail_url(img)
    license_url = "https://creativecommons.org/publicdomain/zero/1.0/"
    foreign_identifier = _get_foreign_id(img)
    creator, creator_url = _get_creator_info(img)
    title = _get_title(img)
    meta_data = _get_image_meta_data(img)

    return image_store.add_item(
            foreign_landing_url=foreign_landing_url,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            license_url=license_url,
            foreign_identifier=foreign_identifier,
            creator=creator,
            creator_url=creator_url,
            title=title,
            meta_data=meta_data,
    )


def _get_foreign_landing_url(img):
    foreign_landing_url = None
    foreign_landing_url = img.get("ResourceURL")
    return foreign_landing_url


def _get_image_url(img):
    image_url = None
    image_url = (img.get("PrimaryImage")).get("Raw")
    return image_url


def _get_thumbnail_url(img):
    thumbnail_url = None
    thumbnail_url = (img.get("PrimaryImage")).get("Small")
    return thumbnail_url


def _get_foreign_id(img):
    foreign_id = None
    foreign_id = img.get("ObjectNumber")
    return foreign_id


def _get_creator_info(img):
    creator, creator_url = None, None
    creator = img.get("Creator")
    if creator:
        creator = img.get("Creator")
        creator_url = (f"{MUSEUM_SITE}/browse/{creator.lower()}")

    return creator, creator_url


def _get_title(img):
    title = None
    title = img.get("Title")
    return title


def _get_image_meta_data(img):
    image_meta_data = {}
    image_meta_data["ObjectNumber"] = img.get("ObjectNumber")
    image_meta_data["PublicAccessDate"] = img.get("PublicAccessDate")
    image_meta_data["Collection"] = img.get("Collection")
    image_meta_data["Medium"] = img.get("Medium")
    image_meta_data["Classification"] = img.get("Classification")
    image_meta_data["Description"] = img.get("Description")
    image_meta_data["CreditLine"] = img.get("CreditLine")
    return {k: v for k, v in image_meta_data.items() if v is not None}


if __name__ == "__main__":
    main()
