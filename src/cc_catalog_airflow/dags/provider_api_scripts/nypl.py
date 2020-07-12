import os
import logging
from urllib.parse import urlparse
from common.requester import DelayedRequester
from common.storage.image import ImageStore

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

LIMIT = 500
DELAY = 5.0
RETRIES = 3
PROVIDER = "nypl"
BASE_ENDPOINT = "http://api.repo.nypl.org/api/v1/items/search"
METADATA_ENDPOINT = "http://api.repo.nypl.org/api/v1/items/item_details/"
NYPL_API = os.getenv("NYPL_API")
TOKEN = f"Token token={NYPL_API}"

delay_request = DelayedRequester(delay=DELAY)
image_store = ImageStore(provider=PROVIDER)

DEFAULT_QUERY_PARAM = {
    "q": "CC_0",
    "field": "use_rtxt_s",
    "page": 1,
    "per_page": LIMIT
}

HEADERS = {
    "Authorization": TOKEN
}

IMAGE_URL_DIMENSIONS = [
    "t=g", "t=v", "t=q", "t=w", "t=r"
]

THUMBNAIL_DIMENSIONS = [
    "t=w", "t=r", "t=q", "t=f", "t=v", "t=g"
]


def main():
    page = 1
    condition = True
    while condition:
        query_param = _get_query_param(
            page=page
        )
        request_response = _request_handler(
            params=query_param
        )
        results = request_response.get("result")
        if type(results) == list:
            if len(results) > 0:
                image_count = _handle_results(results)
                page = page + 1
            else:
                condition = False
        else:
            condition = False
    image_store.commit()
    logger.info(f"total images {image_store.total_images}")


def _get_query_param(
        default_query_param=DEFAULT_QUERY_PARAM,
        page=1,
        ):
    query_param = default_query_param
    query_param["page"] = page
    return query_param


def _request_handler(
        endpoint=BASE_ENDPOINT,
        request_type="search",
        params=None,
        headers=HEADERS,
        retries=RETRIES
        ):
    results = None
    for retry in range(retries):
        response = delay_request.get(
            endpoint,
            params=params,
            headers=headers
        )

        try:
            response_json = response.json()
            response_json = response_json.get("nyplAPI")
            response_headers = response_json.get("response", {}).get("headers")

            if request_type == "search" and response_headers is not None:
                if response_headers.get("code") == "200":
                    results = response_json.get("response")
                    break

            elif response_headers is not None:
                if response_headers.get("code", {}).get("$") == "200":
                    results = response_json.get("response")
                    break
        except Exception as e:
            logger.warning(f"Request failed due to {e}")

    return results


def _handle_results(results):
    image_count = 0
    for item in results:
        uuid = item.get("uuid")

        item_details = _request_handler(
            endpoint=METADATA_ENDPOINT+uuid,
            request_type="item_details"
        )
        if item_details is None:
            continue

        mods = item_details.get("mods")
        title = _get_title(
            mods.get("titleInfo")
        )
        creator = _get_creators(
            mods.get("")
        )
        metadata = _get_metadata(mods)
        capture_count = item_details.get("numResults", {}).get("$")
        captures = item_details.get("sibling_captures", {}).get("capture", [])
        if type(captures) is not list:
            captures = [captures]

        for img in captures:
            image_id = img.get("imageID", {}).get("$")
            if image_id is None:
                continue
            image_url, thumbnail_url = _get_images(
                img.get("imageLinks", {}).get("imageLink", [])
            )
            foreign_landing_url = img.get("itemLink", {}).get("$")
            license_url = img.get("rightsStatementURI", {}).get("$")
            if (
                image_url is None or foreign_landing_url is None or
                license_url is None
            ):
                continue
            print(image_id + "\n" + image_url + "\n" + license_url)
            image_count = image_store.add_item(
                foreign_identifier=image_id,
                foreign_landing_url=foreign_landing_url,
                image_url=image_url,
                license_url=license_url,
                thumbnail_url=thumbnail_url,
                title=title,
                creator=creator,
                meta_data=metadata
            )

    return image_count


def _get_title(titleinfo):
    title = None
    if type(titleinfo) == list:
        if len(titleinfo) > 0:
            title = titleinfo[0].get("title", {}).get("$")
    return title


def _get_creators(creatorinfo):
    creator = []
    if type(creatorinfo) == list:
        if len(creatorinfo) > 0:
            for info in creatorinfo:
                creator.append(
                    info.get("namePart", {}).get("$", "")
                )
            creator = '|'.join(creator)
    return creator


def _get_images(
        images,
        image_url_dimensions=IMAGE_URL_DIMENSIONS,
        thumbnail_dimensions=THUMBNAIL_DIMENSIONS
        ):
    image_url, thumbnail_url = None, None
    image_type = {
        urlparse(img.get("$")).query.split("&")[1]: img.get("$")
        for img in images
    }
    for dimension in image_url_dimensions:
        if dimension in image_type.keys():
            image_url = image_type.get(
                dimension
                ).replace(
                    "&download=1", ""
                    )
            break

    for dimension in thumbnail_dimensions:
        if dimension in image_type.keys():
            thumbnail_url = image_type.get(
                dimension
                ).replace(
                    "&download=1", ""
                    )
            break

    return image_url, thumbnail_url


def _get_metadata(mods):
    metadata = {}
    type_of_resource = mods.get("typeOfResource")
    if type(type_of_resource) == list:
        if type_of_resource[0].get("usage") == "primary":
            metadata["type_of_resource"] = type_of_resource[0].get("$")

    metadata["genre"] = mods.get("genre", {}).get("$")

    origin_info = mods.get("originInfo")
    if type(origin_info) == dict:
        metadata['date_issued'] = origin_info.get("dateIssued", {}).get("$")
        metadata["publisher"] = origin_info.get("publisher", {}).get("$")

    metadata["description"] = mods.get("physicalDescription").get(
        "note").get("$")

    return metadata


if __name__ == "__main__":
    main()


# http://images.nypl.org/index.php?id=489669&t=w&suffix=510d47dc-3a5e-a3d9-e040-e00a18064a99.001
