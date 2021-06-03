import json
import logging
import os
from unittest.mock import patch
from collections import namedtuple
from common import MockImageStore

import raw_pixel as rwp

LicenseInfo = namedtuple(
    'LicenseInfo',
    ['license', 'version', 'url']
)
_license_info = ('cc0', '1.0', 'https://creativecommons.org/publicdomain/zero/1.0/')
license_info = LicenseInfo(*_license_info)
rwp.image_store = MockImageStore(
    provider=rwp.PROVIDER,
    license_info=license_info
)

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "tests/resources/rawpixel"
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s",
    level=logging.DEBUG,
)


def _get_resource_json(json_name):
    with open(os.path.join(RESOURCES, json_name)) as f:
        resource_json = json.load(f)
    return resource_json


def test_get_image_list_giving_none():
    with patch.object(rwp, "_request_content", return_value=None):
        total, result = rwp._get_image_list()
        assert total is None
        assert result is None


def test_get_image_list_correct():
    r = _get_resource_json("total_images_example.json")
    with patch.object(rwp, "_request_content", return_value=r):
        total, result = rwp._get_image_list()
        assert total == 22215
        assert len(result) == 2


def test_process_pages_giving_zero():
    with patch.object(rwp, "_request_content", return_value=None):
        total, result = rwp._get_image_list()
        img_ctr = rwp._process_pages(total, result, page=1)
        assert img_ctr == 0


def test_process_image_data():
    r = _get_resource_json("total_images_example.json")
    with patch.object(rwp, "_request_content", return_value=r):
        result = rwp._get_image_list()[1]
        assert rwp._process_image_data(image=result[0]) == 1


def test_get_foreign_id_url():
    r = _get_resource_json("total_images_example.json")
    with patch.object(rwp, "_request_content", return_value=r):
        result = rwp._get_image_list()[1]
        expected_foreign_ids = [
            2041320,
            2041320,
        ]
        expected_foreign_urls = [
            "https://www.rawpixel.com/image/2041320/world-map-drawn-oval-projection",
            "https://www.rawpixel.com/image/2041320/world-map-drawn-oval-projection",
        ]
        for i in range(2):
            foreign_id, foreign_url = rwp._get_foreign_id_url(image=result[0])
            assert foreign_id == expected_foreign_ids[i]
            assert foreign_url == expected_foreign_urls[i]


def test_get_image_properties():
    r = _get_resource_json("total_images_example.json")
    with patch.object(rwp, "_request_content", return_value=r):
        result = rwp._get_image_list()[1]
        img_url, width, height, thumbnail = rwp._get_image_properties(
            image=result[0]
        )
        assert (
                img_url
                == ("https://img.rawpixel.com/s3fs-private/rawpixel_images/"
                    "website_content/pdmaps-loc-06-nam_1.jpg?w=1200&h=630&fit="
                    "crop&dpr=1.5&crop=entropy&fm=pjpg&q=75&vib=3&con=3&usm=15&"
                    "markpad=13&markalpha=90&markscale=10&markx=25&mark=rawpixel"
                    "-watermark.png&cs=srgb&bg=F4F4F3&ixlib=js-2.2.1&s=edbf5b4204"
                    "30b7f118a0093686c40f93")
        )
        assert width == "1200"
        assert height == "630"
        assert (
                thumbnail
                == ("https://img.rawpixel.com/s3fs-private/rawpixel_images/"
                    "website_content/pdmaps-loc-06-nam_1.jpg?w=400&dpr=1&fit"
                    "=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con="
                    "3&usm=15&bg=F4F4F3&ixlib=js-2.2.1&s=6f33bfab36227436a0f9ad230"
                    "fc1d64a")
        )

        img_url, width, height, thumbnail = rwp._get_image_properties(
            image=result[1]
        )
        assert (
                img_url
                == ("https://images.rawpixel.com/image_png_1300/czNmcy1wcml"
                    "2YXRlL3Jhd3BpeGVsX2ltYWdlcy93ZWJzaXRlX2NvbnRlbnQvZmw0OTk"
                    "0MjIxMjA1MS1pbWFnZS1rcDR2eDlhNi5wbmc.png?s=jMjsC0i4AdUsn"
                    "ZY91VWFxTyuHEAgLqjmCRIH7_b76R0")
        )
        assert width == '1300'
        assert height == '731'
        assert (
                thumbnail
                == ("https://images.rawpixel.com/image_png_400/czNmcy1wcml2YXR"
                    "lL3Jhd3BpeGVsX2ltYWdlcy93ZWJzaXRlX2NvbnRlbnQvZmw0OTk0MjIxM"
                    "jA1MS1pbWFnZS1rcDR2eDlhNi5wbmc.png?s=DVKwFVZT14d39M_xKMN8i"
                    "hYLeaqv8wUoT4cCaWCuVm4")
        )


def test_get_title_owner():
    r = _get_resource_json("total_images_example.json")
    with patch.object(rwp, "_request_content", return_value=r):
        result = rwp._get_image_list()[1]
        title, owner = rwp._get_title_owner(image=result[0])
        assert title == "World map drawn on an oval projection"
        assert owner == "Library of Congress"


def test_get_meta_data_given_pinterest_descr_is_present():
    r = _get_resource_json("total_images_example.json")
    with patch.object(rwp, "_request_content", return_value=r):
        result = rwp._get_image_list()[1]
        expected_data = [
            "Portolan atlas of the Mediterranean Sea, western Europe, and the "
            "northwest coast of Africa: World map drawn on an oval projection"
            " (ca. 1590) by Joan Oliva. Original from Library of Congress. "
            "Digitally enhanced by rawpixel. | free image by rawpixel.com / "
            "Library of Congress (Source)",
            "From research to community support, Oak Ridge National "
            "Laboratory enlists world-class science and staff in the fight "
            "against COVID-19. Original public domain image from Flickr | "
            "free image by rawpixel.com / United States Department of "
            "Energy (source)",
        ]
        for i in range(2):
            meta_data = rwp._get_meta_data(image=result[i])
            expected_meta_data = {"description": expected_data[i]}
            assert meta_data == expected_meta_data


def test_get_meta_data_given_no_pinterest_descr():
    r = _get_resource_json("total_images_but_pinterest_descr_example.json")
    with patch.object(rwp, "_request_content", return_value=r):
        result = rwp._get_image_list()[1]
        meta_data = rwp._get_meta_data(image=result[0])
        assert meta_data == {}


def test_get_tags():
    r = _get_resource_json("total_images_example.json")
    with patch.object(rwp, "_request_content", return_value=r):
        result = rwp._get_image_list()[1]
        expected_data = [
            {"tag_count": 47, "first_tag": "america"},
            {"tag_count": 12, "first_tag": "coronavirus"},
        ]
        for i in range(2):
            tags = rwp._get_tags(image=result[i])
            assert len(tags) == expected_data[i]["tag_count"]
            assert tags[0] == expected_data[i]["first_tag"]
