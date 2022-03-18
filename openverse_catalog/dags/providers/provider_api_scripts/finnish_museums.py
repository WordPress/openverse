import logging

from common.licenses import get_license_info
from common.loader import provider_details as prov
from common.requester import DelayedRequester
from common.storage.image import ImageStore


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

LIMIT = 100
DELAY = 5
RETRIES = 3
PROVIDER = prov.FINNISH_DEFAULT_PROVIDER
ENDPOINT = "https://api.finna.fi/api/v1/search"
SUB_PROVIDERS = prov.FINNISH_SUB_PROVIDERS
FORMAT_TYPE = "0/Image/"
API_URL = "https://api.finna.fi"
LANDING_URL = "https://www.finna.fi/Record/"

BUILDINGS = ["0/Suomen kansallismuseo/", "0/Museovirasto/", "0/SATMUSEO/", "0/SA-kuva/"]

DEFAULT_QUERY_PARAMS = {
    "filter[]": [f'format:"{FORMAT_TYPE}"'],
    "limit": LIMIT,
    "page": 1,
}

delayed_requester = DelayedRequester(DELAY)
image_store = ImageStore(provider=PROVIDER)


def main():
    logger.info("Begin: Finnish museum provider script")
    for building in BUILDINGS:
        logger.info(f"Obtaining Images of building {building}")
        _get_object_list(building)

    total_images = image_store.commit()
    logger.info(f"Total Images received {total_images}")


def _get_object_list(building, endpoint=ENDPOINT, retries=RETRIES):
    page = 1
    total_images = 0
    condition = True
    while condition:
        query_params = _build_params(building=building, page=page)
        page += 1
        json_resp = delayed_requester.get_response_json(
            endpoint=endpoint, retries=retries, query_params=query_params
        )

        object_list = _get_object_list_from_json(json_resp)
        if object_list is None:
            break
        total_images = _process_object_list(object_list)

    if total_images == 0:
        logger.warning("No more retries ")
        return


def _build_params(building, default_params=None, page=1):
    if default_params is None:
        default_params = DEFAULT_QUERY_PARAMS
    query_params = default_params.copy()
    query_params.update(
        {
            "page": page,
            "filter[]": [f'format:"{FORMAT_TYPE}"', f'building:"{building}"'],
        }
    )

    return query_params


def _get_object_list_from_json(json_resp):
    if (
        json_resp is None
        or str(json_resp.get("status")).lower() != "ok"
        or json_resp.get("records") is None
        or len(json_resp.get("records")) == 0
    ):
        object_list = None
    else:
        object_list = json_resp.get("records")

    return object_list


def _process_object_list(object_list):
    total_images = 0
    if object_list is not None:
        for obj in object_list:
            total_images = _process_object(obj)

    return total_images


def _process_object(obj, sub_providers=SUB_PROVIDERS, provider=PROVIDER):
    total_images = 0
    license_url = get_license_url(obj)
    if license_url is None:
        return None
    foreign_identifier = obj.get("id")
    title = obj.get("title")
    building = obj.get("buildings")[0].get("value")
    source = next((s for s in sub_providers if building in sub_providers[s]), provider)
    foreign_landing_url = _get_landing(obj)
    raw_tags = _get_raw_tags(obj)
    image_list = obj.get("images")
    for img in image_list:
        image_url = _get_image_url(img)
        total_images = image_store.add_item(
            license_info=get_license_info(license_url=license_url),
            foreign_identifier=foreign_identifier,
            foreign_landing_url=foreign_landing_url,
            image_url=image_url,
            title=title,
            source=source,
            raw_tags=raw_tags,
        )
    return total_images


def get_license_url(obj):
    license_url = obj.get("imageRights", {}).get("link")

    if license_url is None:
        return None

    # The API returns urls linking to the Finnish version of the license deed,
    # (eg `licenses/by/4.0/deed.fi`), but the license validation logic expects
    # links to the license page (eg `license/by/4.0`).
    return license_url.removesuffix("deed.fi")


def _get_raw_tags(obj):
    raw_tags = []
    if obj.get("subjects") is None:
        return None
    for tag_list in obj.get("subjects"):
        for tag in tag_list:
            raw_tags.append(tag)
    return raw_tags


def _get_landing(obj, landing_url=LANDING_URL):
    l_url = None
    id_ = obj.get("id")
    if id_:
        l_url = landing_url + id_
    return l_url


def _get_image_url(img, image_url=API_URL):
    img_url = None
    if img:
        img_url = image_url + img
    return img_url


if __name__ == "__main__":
    main()
