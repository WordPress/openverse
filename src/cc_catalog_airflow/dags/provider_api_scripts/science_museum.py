import logging
from common.requester import DelayedRequester
from common.storage.image import ImageStore

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

LIMIT = 100
DELAY = 5.0
RETRIES = 3
PROVIDER = "sciencemuseum"
ENDPOINT = "https://collection.sciencemuseumgroup.org.uk/search/"

delay_request = DelayedRequester(delay=DELAY)
image_store = ImageStore(provider=PROVIDER)

HEADERS = {
    "Accept": "application/json"
}

DEFAULT_QUERY_PARAM = {
    "has_image": 1,
    "image_license": "CC",
    "page[size]": LIMIT,
    "page[number]": 1
}


def main():
    logger.info("Begin: Science Museum script")
    page_number = 1
    condition = True
    while condition:
        query_param = _get_query_param(
            page_number=page_number
            )
        batch_data = _get_batch_objects(
            query_param=query_param
        )
        if batch_data:
            image_count = _handle_object_data(batch_data)
            page_number += 1
            logger.info(
                f"{image_count} images crawled from page : {page_number}"
            )
        else:
            condition = False
    logger.info(f"Total pages crawled {page_number}")
    image_count = image_store.commit()
    logger.info(f"Total images : {image_count}")


def _get_query_param(
        page_number=1,
        default_query_param=DEFAULT_QUERY_PARAM
        ):
    query_param = default_query_param.copy()
    query_param["page[number]"] = page_number
    return query_param


def _get_batch_objects(
        endpoint=ENDPOINT,
        headers=HEADERS,
        retries=RETRIES,
        query_param=None
        ):
    for retry in range(retries):
        response = delay_request.get(
            endpoint,
            query_param,
            headers=headers
        )
        try:
            response_json = response.json()
            if "data" in response_json.keys():
                data = response_json.get("data")
                break
            else:
                data = None
        except Exception as e:
            logger.error(f"Failed to due to {e}")
            data = None
    return data


def _handle_object_data(batch_data):
    image_count = 0
    for obj_ in batch_data:
        id_ = obj_.get("id")
        links = obj_.get("links")

        if links:
            foreign_landing_url = links.get("self")
        if foreign_landing_url is None:
            continue
        obj_attributes = obj_.get("attributes")
        if obj_attributes is None:
            continue
        title = obj_attributes.get("summary_title")
        creator = _get_creator_info(obj_attributes)
        metadata = _get_metadata(obj_attributes)
        multimedia = obj_attributes.get("multimedia")
        if multimedia is None:
            continue
        for image_data in multimedia:
            processed = image_data.get("processed")
            source = image_data.get("source")
            image_url, height, width = _get_image_info(
                processed
            )
            if image_url is None:
                continue

            license_version = _get_license_version(source)
            if license_version is None:
                continue
            license_, version = license_version.lower().split(" ")
            license_ = license_.replace("cc-", "")
            thumbnail_url = _get_thumbnail_url(processed)
            image_count = image_store.add_item(
                    foreign_identifier=id_,
                    foreign_landing_url=foreign_landing_url,
                    image_url=image_url,
                    height=height,
                    width=width,
                    license_=license_,
                    license_version=version,
                    thumbnail_url=thumbnail_url,
                    creator=creator,
                    title=title,
                    meta_data=metadata
                    )
    return image_count


def _get_creator_info(obj_attr):
    creator_info = None
    life_cycle = obj_attr.get("lifecycle")
    if life_cycle:
        creation = life_cycle.get("creation")
        if type(creation) == list:
            maker = creation[0].get("maker")
            if type(maker) == list:
                creator_info = maker[0].get("summary_title")
    return creator_info


def _get_image_info(processed):
    if processed.get("large"):
        image = processed.get("large").get("location")
        measurements = processed.get("large").get("measurements")
    elif processed.get("medium"):
        image = processed.get("medium").get("location")
        measurements = processed.get("medium").get("measurements")
    else:
        image = None
        measurements = None
    image = check_url(image)
    height, width = _get_dimensions(measurements)
    return image, height, width


def _get_thumbnail_url(processed):
    if processed.get("large_thumbnail"):
        image = processed.get("large_thumbnail").get("location")
    elif processed.get("medium_thumbnail"):
        image = processed.get("medium_thumbnail").get("location")
    elif processed.get("small_thumbnail"):
        image = processed.get("small_thumbnail").get("location")
    else:
        image = None
    thumbnail_url = check_url(image)
    return thumbnail_url


def check_url(image_url):
    base_url = "https://coimages.sciencemuseumgroup.org.uk/images/"
    if image_url:
        if "http" in image_url:
            checked_url = image_url
        else:
            checked_url = base_url + image_url
    else:
        checked_url = None
    return checked_url


def _get_dimensions(measurements):
    height_width = {}
    if measurements:
        dimensions = measurements.get("dimensions")
        if dimensions:
            for dim in dimensions:
                height_width[
                    dim.get("dimension")
                ] = dim.get("value")
    return height_width.get("height"), height_width.get("width")


def _get_license_version(source):
    license_version = None
    if source:
        legal = source.get("legal")
        if legal:
            rights = legal.get("rights")
            if type(rights) == list:
                license_version = rights[0].get("usage_terms")
    return license_version


def _get_metadata(obj_attr):
    metadata = {}
    identifier = obj_attr.get("identifier")
    if type(identifier) == list:
        metadata["accession number"] = identifier[0].get("value")
    name = obj_attr.get("name")
    if type(name) == list:
        metadata["name"] = name[0].get("value")
    category = obj_attr.get("categories")
    if type(category) == list:
        metadata["category"] = category[0].get("value")
    creditline = obj_attr.get("legal")
    if type(creditline) == dict:
        metadata["creditline"] = creditline.get("credit_line")
    description = obj_attr.get("description")
    if type(description) == list:
        metadata["description"] = description[0].get("value")
    return metadata


if __name__ == "__main__":
    main()
