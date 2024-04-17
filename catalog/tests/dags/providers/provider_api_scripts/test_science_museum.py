import logging
from unittest.mock import patch

import pytest
from tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)

from common.licenses import get_license_info
from common.loader import provider_details as prov
from common.storage.image import ImageStore
from providers.provider_api_scripts.science_museum import ScienceMuseumDataIngester


BY_NC_SA_4_0 = get_license_info(license_="by-nc-sa", license_version="4.0")
BY_NC_ND_4_0 = get_license_info(license_="by-nc-nd", license_version="4.0")
BY_SA_4_0 = get_license_info(license_="by-sa", license_version="4.0")

sm = ScienceMuseumDataIngester()
image_store = ImageStore(provider=prov.SCIENCE_DEFAULT_PROVIDER)
sm.media_stores = {"image": image_store}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.DEBUG
)


@pytest.fixture(autouse=True)
def after_test():
    yield
    sm.RECORD_IDS = set()


_get_resource_json = make_resource_json_func("sciencemuseum")


@pytest.fixture
def object_data():
    yield _get_resource_json("object_data.json")


@pytest.fixture
def single_image_data():
    object_data = _get_resource_json("object_data.json")
    object_data["attributes"]["multimedia"] = object_data["attributes"]["multimedia"][
        :1
    ]
    yield object_data


default_params = {
    "has_image": 1,
    "image_license": "CC",
    "page[size]": 100,
}


def test_get_year_ranges():
    # Expected list when using 1933 as the final year
    expected_list = [
        (0, 200),
        (200, 1500),
        (1500, 1750),
        (1750, 1775),
        (1775, 1800),
        (1800, 1825),
        (1825, 1835),
        (1835, 1845),
        (1845, 1855),
        (1855, 1865),
        (1865, 1875),
        (1875, 1885),
        (1885, 1895),
        (1895, 1905),
        (1905, 1915),
        (1915, 1925),
        (1925, 1930),
        (1930, 1933),
    ]
    actual_list = sm._get_year_ranges(1933)
    assert actual_list == expected_list


def test_get_query_param_default():
    actual_param = sm.get_next_query_params({}, **{"year_range": (0, 1500)})
    expected_param = default_params | {
        "page[number]": 0,
        "date[from]": 0,
        "date[to]": 1500,
    }

    assert actual_param == expected_param


def test_get_query_param_offset_page_number():
    sm = ScienceMuseumDataIngester()
    sm.page_number = 10
    actual_param = sm.get_next_query_params(
        default_params | {"page[number]": 10}, **{"year_range": (1500, 2000)}
    )
    expected_param = default_params | {
        "page[number]": 11,
        "date[from]": 1500,
        "date[to]": 2000,
    }

    assert actual_param == expected_param


@pytest.mark.parametrize(
    "record",
    [
        # Missing any item in the foreign_landing_url chain
        # Here we return `None` only if the foreign_landing_url is missing.
        # Otherwise, we create an image list, check each image's
        # required fields and return a blank list if none are valid (see next test).
        {"links": {}},
        {"links": {"self": ""}},
        {"links": {"self": "link"}, "attributes": {"multimedia": []}},
    ],
)
def test_get_record_data_returns_none_for_falsy_foreign_landing_url_and_multimedia(
    record,
):
    actual_record_data = sm.get_record_data(record)
    assert actual_record_data is None


@pytest.mark.parametrize(
    "record",
    [
        # missing foreign_identifier
        {"links": {"self": "link"}, "attributes": {"multimedia": [{"admin": {}}]}},
        {
            "links": {"self": "link"},
            "attributes": {"multimedia": [{"admin": {"uid": ""}}]},
        },
        # missing url
        {
            "links": {"self": "link"},
            "attributes": {"multimedia": [{"admin": {"uid": "fid"}}]},
        },
        {
            "links": {"self": "link"},
            "attributes": {
                "multimedia": [{"admin": {"uid": "fid"}, "processed": {"large": ""}}],
            },
        },
        # missing license_pair
        {
            "links": {"self": "link"},
            "attributes": {
                "multimedia": [
                    {"admin": {"uid": "fid"}, "processed": {"large": {}}},
                ],
            },
        },
    ],
)
def test_get_record_data_returns_empty_list_for_falsy_image_required_values(record):
    # If we have a foreign_landing_url, we create an image list, and check each
    # image's required fields. If none are valid, we return an empty list.
    actual_record_data = sm.get_record_data(record)
    assert actual_record_data == []


def test_get_record_data_success(object_data):
    actual_record_data = sm.get_record_data(object_data)
    actual_image_data = actual_record_data[0]
    assert len(actual_record_data) == 3

    expected_image_data = {
        "foreign_identifier": "i458349",
        "foreign_landing_url": "https://collection.sciencemuseumgroup.org.uk/objects/co84905/small-votive-organ-of-unknown-type-votive-viscera",
        "url": "https://coimages.sciencemuseumgroup.org.uk/458/349/large_a659676__0001_.jpg",
        "height": 1150,
        "width": 1536,
        "filetype": "jpeg",
        "filesize": 134947,
        "license_info": BY_SA_4_0,
        "creator": "Unknown maker",
        "title": "Small votive organ of unknown type",
        "meta_data": {
            "accession number": "A659676",
            "category": "SCM - Classical & Medieval Medicine",
            "description": "Small votive organ of unknown type, built up from coiled strips of terracotta, probably Roman, 200BCE-200BC",
            "name": "votive viscera",
            "creditline": "Loan, Wellcome Trust",
        },
    }
    for key, value in expected_image_data.items():
        assert key and value == actual_image_data[key]
    assert actual_image_data == expected_image_data


def test_save_item_adds_filetype(single_image_data):
    with patch.object(sm.media_stores["image"], "save_item") as mock_save:
        sm.process_batch([single_image_data])
    actual_image = mock_save.call_args[0][0]
    assert "jpg" == actual_image.filetype


def test_creator_info_success(object_data):
    attributes = object_data["attributes"]
    actual_creator = sm._get_creator_info(attributes)

    assert actual_creator == "Unknown maker"


def test_creator_info_fail(object_data):
    attributes = object_data["attributes"]
    attributes["creation"].pop("maker", None)
    actual_creator = sm._get_creator_info(attributes)

    assert actual_creator is None


def test_image_info_large():
    large_image = _get_resource_json("large_image.json")
    actual_image, actual_height, actual_width, actual_filetype, actual_filesize = (
        sm._get_image_info(large_image)
    )
    expected_image = (
        "https://coimages.sciencemuseumgroup.org.uk/3/563/"
        "large_1999_0299_0001__0002_.jpg"
    )
    expected_height = 1022
    expected_width = 1536
    expected_filetype = "jpeg"
    expected_filesize = 58772

    assert actual_image == expected_image
    assert actual_height == expected_height
    assert actual_width == expected_width
    assert actual_filetype == expected_filetype
    assert actual_filesize == expected_filesize


def test_image_info_medium():
    medium_image = _get_resource_json("medium_image.json")
    actual_url, actual_height, actual_width, actual_filetype, actual_filesize = (
        sm._get_image_info(medium_image)
    )

    expected_image = (
        "https://coimages.sciencemuseumgroup.org.uk/3/563/"
        "medium_1999_0299_0001__0002_.jpg"
    )
    expected_height = 576
    expected_width = 866

    assert actual_url == expected_image
    assert actual_height == expected_height
    assert actual_width == expected_width
    assert actual_filetype == "jpeg"
    assert actual_filesize is None


def test_image_info_failure():
    actual_url, actual_height, actual_width, actual_filetype, actual_filesize = (
        sm._get_image_info({})
    )

    assert actual_url is None
    assert actual_height is None
    assert actual_width is None
    assert actual_filetype is None
    assert actual_filesize is None


def test_check_relative_url():
    rel_url = "3/563/large_thumbnail_1999_0299_0001__0002_.jpg"
    actual_url = sm.check_url(rel_url)
    expected_url = (
        "https://coimages.sciencemuseumgroup.org.uk/3/563/"
        "large_thumbnail_1999_0299_0001__0002_.jpg"
    )

    assert actual_url == expected_url


def test_check_complete_url():
    url = (
        "https://coimages.sciencemuseumgroup.org.uk/3/563/"
        "large_thumbnail_1999_0299_0001__0002_.jpg"
    )
    actual_url = sm.check_url(url)
    expected_url = url

    assert actual_url == expected_url


def test_check_url_none():
    url = None
    actual_url = sm.check_url(url)

    assert actual_url is None


def test_get_dimensions():
    measurements = _get_resource_json("measurements.json")
    actual_height, actual_width = sm._get_dimensions(measurements)
    expected_height, expected_width = (1022, 1536)

    assert actual_height == expected_height
    assert actual_width == expected_width


def test_get_dimensions_none():
    image_data = {}
    actual_height, actual_width = sm._get_dimensions(image_data)

    assert actual_height is None
    assert actual_width is None


@pytest.mark.parametrize(
    "image_data, expected",
    [
        # Typical license with dash
        (
            {"legal": {"rights": [{"licence": "CC-BY-NC-SA 4.0"}]}},
            BY_NC_SA_4_0,
        ),
        (
            {"legal": {"rights": [{"licence": "CC-BY-NC-ND 4.0"}]}},
            BY_NC_ND_4_0,
        ),
        # Typical license with space
        (
            {"legal": {"rights": [{"licence": "CC BY-NC-SA 4.0"}]}},
            BY_NC_SA_4_0,
        ),
        (
            {"legal": {"rights": [{"licence": "CC BY-SA 4.0"}]}},
            BY_SA_4_0,
        ),
        # No legal section
        (
            {},
            None,
        ),
        # No usage terms
        (
            {"legal": {"rights": [{"details": "Details!"}]}},
            None,
        ),
        # Invalid usage terms
        (
            {
                "source": {
                    "legal": {
                        "rights": [
                            {
                                "usage_terms": "Contact the picture library team (SMG Images) to clear permissions"
                            }
                        ]
                    }
                }
            },
            None,
        ),
        (
            {
                "source": {
                    "legal": {
                        "rights": [
                            {
                                "usage_terms": "© The Board of Trustees of the Science Museum, London"
                            }
                        ]
                    }
                }
            },
            None,
        ),
        (
            {
                "source": {
                    "legal": {
                        "rights": [
                            {"usage_terms": "Restricted - Not for Commercial Use"}
                        ]
                    }
                }
            },
            None,
        ),
    ],
)
def test_get_license(image_data, expected):
    actual_license_version = sm._get_license_info(image_data)
    assert actual_license_version == expected


def test_get_metadata():
    obj_attr = _get_resource_json("object_attr.json")
    actual_metadata = sm._get_metadata(obj_attr)
    expected_metadata = _get_resource_json("metadata.json")

    assert actual_metadata == expected_metadata


def test_handle_obj_data_none(object_data):
    object_data["attributes"]["multimedia"] = []
    actual_images = sm.get_record_data(object_data)

    assert actual_images is None


@pytest.mark.parametrize(
    "next_url, page_number, should_continue, should_alert",
    [
        # Happy path, should continue
        (
            "https://collection.sciencemuseumgroup.org.uk/search/date[from]/1875/date[to]/1900/images/image_license?page[size]=100&page[number]=20",
            20,
            True,
            False,
        ),
        # Don't continue when next_url is None, regardless of page number
        (None, 20, False, False),
        (None, 50, False, False),
        # Don't continue and DO alert when page number is 50 and there is a next_url
        (
            "https://collection.sciencemuseumgroup.org.uk/search/date[from]/1875/date[to]/1900/images/image_license?page[size]=100&page[number]=50",
            50,
            False,
            True,
        ),
    ],
)
def test_get_should_continue(next_url, page_number, should_continue, should_alert):
    response_json = {"links": {"next": next_url}}
    sm = ScienceMuseumDataIngester()
    sm.page_number = page_number

    with patch("common.slack.send_alert") as send_alert_mock:
        assert sm.get_should_continue(response_json) == should_continue
        assert send_alert_mock.called == should_alert


def test_get_should_continue_last_page():
    response_json = {"links": {"next": None}}

    assert sm.get_should_continue(response_json) is False
