import json
import logging
import os
from json import JSONDecodeError

from common.licenses import get_license_info
from common.storage import image


logger = logging.getLogger(__name__)


# This is a workaround for the fact that dict.setdefault is not lazy; it
# always evaluates the default argument, which means the costly
# operation of instantiating an ImageStore in our use case.
class ImageStoreDict(dict):
    def __missing__(self, key):
        ret = self[key] = image.ImageStore(provider=key)
        return ret


_image_store_dict = ImageStoreDict()


def clean_tsv_directory(tsv_directory):
    for tsv in os.listdir(tsv_directory):
        clean_tsv(os.path.join(tsv_directory, tsv))


def clean_tsv(tsv_filename):
    with open(tsv_filename) as f:
        for row in f:
            _process_row(row)
        for image_store in _image_store_dict.values():
            image_store.commit()


def _process_row(tsv_row):
    row_image = _get_image_from_row(tsv_row)
    row_meta_data = _get_json_from_string(row_image.meta_data)
    image_store = _image_store_dict[row_image.provider]
    image_store.add_item(
        foreign_landing_url=row_image.foreign_landing_url,
        url=row_image.url,
        thumbnail_url=row_image.thumbnail_url,
        license_info=get_license_info(
            license_url=get_license_url(row_meta_data),
            license_=row_image.license_,
            license_version=row_image.license_version,
        ),
        foreign_identifier=row_image.foreign_identifier,
        width=row_image.width,
        height=row_image.height,
        creator=row_image.creator,
        creator_url=row_image.creator_url,
        title=row_image.title,
        meta_data=row_meta_data,
        raw_tags=_get_json_from_string(row_image.tags),
        watermarked=row_image.watermarked,
        source=row_image.source,
        ingestion_type=row_image.ingestion_type,
    )


def _get_image_from_row(tsv_row):
    exploded_row = [
        s.replace("\\\\", "\\") if s != "\\N" else None
        for s in tsv_row.strip().split("\t")
    ]
    try:
        row_image = image.Image(*exploded_row)
    except (TypeError, ValueError) as e:
        logger.warning(f"Could not unpack row {tsv_row} into valid image: {e}")
        row_image = None
    return row_image


def _get_json_from_string(json_str):
    try:
        json_obj = json.loads(json_str)
    except (TypeError, ValueError, JSONDecodeError) as e:
        logger.warning(f"Could not parse {json_str} into valid JSON: {e}")
        json_obj = None
    return json_obj


def get_license_url(meta_data):
    try:
        license_url = meta_data.get(
            "raw_license_url", meta_data.get("license_url", None)
        )
    except (TypeError, ValueError) as e:
        logger.debug(f"Couldn't retrieve license URL from {meta_data}.  Error: {e}")
        license_url = None
    return license_url if license_url else None
