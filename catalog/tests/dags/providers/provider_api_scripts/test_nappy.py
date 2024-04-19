import pytest
from tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)

from common.constants import IMAGE
from common.licenses import get_license_info
from providers.provider_api_scripts.nappy import NappyDataIngester


_get_resource_json = make_resource_json_func("nappy")


# resource files
FULL_BATCH_RESPONSE = _get_resource_json("images.json")
SINGLE_ITEM = _get_resource_json("single_item.json")

# Set up test class
ingester = NappyDataIngester()


@pytest.mark.parametrize(
    "previous, expected_result",
    [
        pytest.param(
            None, {"per_page": ingester.batch_limit, "page": 1}, id="default_response"
        ),
        pytest.param(
            {"per_page": ingester.batch_limit, "page": 42},
            {"per_page": ingester.batch_limit, "page": 43},
            id="basic_increment",
        ),
        pytest.param(
            {"thing1": "some", "thing2": "data", "page": 0},
            {"thing1": "some", "thing2": "data", "page": 1},
            id="other_parameters",
        ),
    ],
)
def test_get_next_query_params(previous, expected_result):
    actual_result = ingester.get_next_query_params(previous)
    assert actual_result == expected_result


# this is based on the assumption that Nappy will only ever send us image data
@pytest.mark.parametrize(
    "record",
    [None, {}, {"here is": "some data"}],
)
def test_get_media_type(record):
    expected_result = IMAGE
    actual_result = ingester.get_media_type(record)
    assert actual_result == expected_result


@pytest.mark.parametrize(
    "response_json, expected",
    [
        pytest.param(
            FULL_BATCH_RESPONSE,
            FULL_BATCH_RESPONSE["images"],
            id="happy_path",
        ),
        pytest.param({}, None, id="empty_dict"),
        pytest.param(None, None, id="None"),
    ],
)
def test_get_batch_data(response_json, expected):
    actual = ingester.get_batch_data(response_json)
    assert actual == expected


@pytest.mark.parametrize(
    "response_json, expected_result",
    [
        ({}, False),
        (FULL_BATCH_RESPONSE, True),
        (SINGLE_ITEM, False),
    ],
)
def test_get_should_continue(response_json, expected_result):
    actual_result = ingester.get_should_continue(response_json)
    assert actual_result == expected_result


# def get_record_data(self, data: dict) -> dict | list[dict] | None:
@pytest.mark.parametrize(
    "response_json, expected_data",
    [
        pytest.param({}, None, id="empty_dict"),
        pytest.param(FULL_BATCH_RESPONSE, None, id="no_urls"),
        pytest.param(
            {**SINGLE_ITEM, "foreign_landing_url": ""},
            None,
            id="falsy_foreign_landing_url",
        ),
        pytest.param(
            {**SINGLE_ITEM, "foreign_identifier": ""},
            None,
            id="falsy_foreign_identifier",
        ),
        pytest.param({**SINGLE_ITEM, "url": ""}, None, id="falsy_url"),
        pytest.param(
            SINGLE_ITEM,
            {
                "foreign_landing_url": "https://nappy.co/photo/9/woman-with-tattoos",
                "url": "https://images.nappy.co/uploads/large/101591721349meykm7s6hvaswwvslpjrwibeyzru1fcxtxh0hf09cs7kdhmtptef4y3k4ua5z1bkyrbxov8tmagnafm8upwa3hxaxururtx7azaf.jpg",
                "license_info": get_license_info(
                    "https://creativecommons.org/publicdomain/zero/1.0/"
                ),
                "foreign_identifier": 9,
                "filesize": 233500,
                "filetype": "jpg",
                "creator": "iamconnorrm",
                "creator_url": "https://nappy.co/iamconnorrm",
                "title": "woman with tattoos",
                "thumbnail_url": "https://images.nappy.co/uploads/large/101591721349meykm7s6hvaswwvslpjrwibeyzru1fcxtxh0hf09cs7kdhmtptef4y3k4ua5z1bkyrbxov8tmagnafm8upwa3hxaxururtx7azaf.jpg?auto=format&w=600&q=75",
                "meta_data": {
                    "views": 82692,
                    "saves": 18,
                    "downloads": 1329,
                },
                "raw_tags": [
                    "indoor",
                    "bed",
                    "arthropod",
                    "dark",
                    "lobster",
                    "braids",
                    "female",
                    "red",
                    "blue",
                    "tattoo",
                    "earring",
                    "phone",
                    "laying",
                    "room",
                ],
                "width": 2048,
                "height": 1361,
            },
            id="happy_path",
        ),
    ],
)
def test_get_record_data(response_json, expected_data):
    actual_data = ingester.get_record_data(response_json)
    assert actual_data == expected_data


@pytest.mark.parametrize(
    "raw_filesize_string, expected_result",
    [
        pytest.param("4kB", 4_000, id="happy_kB"),
        pytest.param("4MB", 4_000_000, id="happy_MB"),
        pytest.param("4GB", 4_000_000_000, id="happy_GB"),
        pytest.param("", None, id="empty_string"),
        pytest.param([], None, id="not_a_string"),
        pytest.param("gibberish", None, id="gibberish"),
        pytest.param("10.3kB", 10_300, id="decimal"),
        pytest.param("10.12345kB", 10_123, id="rounding"),
        pytest.param(" 4 kB ", 4_000, id="extra_spaces"),
    ],
)
def test_convert_filesize(raw_filesize_string, expected_result):
    # this is a static method, so not using the instance for testing
    actual_result = NappyDataIngester._convert_filesize(raw_filesize_string)
    assert actual_result == expected_result
