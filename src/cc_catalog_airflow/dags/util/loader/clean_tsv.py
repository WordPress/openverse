import json
import logging

from provider_api_scripts.common.storage import image

logger = logging.getLogger(__name__)

_image_store_dict = {}


def main(tsv_filename):
    with open(tsv_filename) as f:
        for row in f:
            _process_row(row)
            for image_store in _image_store_dict.values():
                image_store.commit()


def _process_row(tsv_row, image_store_dict=_image_store_dict):
    row_image = _get_image_from_row(tsv_row)
    row_meta_data = _get_json_from_string(row_image.meta_data)
    image_store = image_store_dict.setdefault(
        row_image.provider, image.ImageStore(provider=row_image.provider)
    )
    image_store.add_item(
        foreign_landing_url=row_image.foreign_landing_url,
        image_url=row_image.image_url,
        thumbnail_url=row_image.thumbnail_url,
        license_url=_get_license_url_from_row_meta_data(row_meta_data),
        license_=row_image.license_,
        license_version=row_image.license_version,
        foreign_identifier=row_image.foreign_identifier,
        width=row_image.width,
        height=row_image.height,
        creator=row_image.creator,
        creator_url=row_image.creator_url,
        title=row_image.title,
        meta_data=row_meta_data,
        raw_tags=_get_json_from_string(row_image.tags),
        watermarked=row_image.watermarked,
        source=row_image.source
    )


def _get_image_from_row(tsv_row):
    exploded_row = [
        s if s != "\\N" else None for s in tsv_row.strip().split('\t')
    ]
    try:
        row_image = image.Image(*exploded_row)
    except Exception as e:
        logger.warning(
            f"Could not unpack row {tsv_row} into valid image: {e}"
        )
        row_image = None
    return row_image


def _get_json_from_string(json_str):
    try:
        json_obj = json.loads(json_str)
    except Exception as e:
        logger.warning(f"Could not parse {json_str} into valid JSON: {e}")
        json_obj = None
    return json_obj


def _get_license_url_from_row_meta_data(meta_data):
    return meta_data.get('raw_license_url', meta_data.get('license_url', None))
