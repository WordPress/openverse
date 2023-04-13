from unittest.mock import patch

import pytest

from common.licenses import get_license_info
from providers.provider_api_scripts.phylopic import PhylopicDataIngester
from tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)


pp = PhylopicDataIngester()


@pytest.fixture
def image_data():
    yield get_json("correct_meta_data_example.json")


get_json = make_resource_json_func("phylopic")


def test__get_initial_query_params():
    with patch.object(pp, "get_response_json", return_value={}), pytest.raises(
        Exception
    ):
        pp._get_initial_query_params()

    data = get_json("initial_request.json")
    with patch.object(pp, "get_response_json", return_value=data):
        pp._get_initial_query_params()

    assert pp.build_param == 194
    assert pp.total_pages == 145


@pytest.mark.parametrize(
    "current_page, prev_query_params, expected_query_params",
    [
        (1, None, {"build": 111, "page": 0, "embed_items": "true"}),  # First call
        (  # Second call
            1,
            {"build": 111, "page": 0, "embed_items": "true"},
            {"build": 111, "page": 1, "embed_items": "true"},
        ),
        (  # Third call
            2,
            {"build": 111, "page": 1, "embed_items": "true"},
            {"build": 111, "page": 2, "embed_items": "true"},
        ),
        (  # Random intermediate call
            50,
            {"build": 111, "page": 1, "embed_items": "true"},
            {"build": 111, "page": 50, "embed_items": "true"},
        ),
    ],
)
def test_get_next_query_params(current_page, prev_query_params, expected_query_params):
    pp.build_param = 111
    pp.current_page = current_page
    actual_query_params = pp.get_next_query_params(prev_query_params)

    assert actual_query_params == expected_query_params


@pytest.mark.parametrize(
    "contributor_data, expected_creator",
    [
        ({}, (None, None)),
        ({"title": "Jane Doe", "href": ""}, ("Jane Doe", None)),
        (
            {"title": "Jane Doe", "href": "/contributors/uuid?build=123"},
            ("Jane Doe", "https://www.phylopic.org/contributors/uuid?build=123"),
        ),
    ],
)
def test__get_creator(contributor_data, expected_creator):
    actual_creator = pp._get_creator(contributor_data)
    assert actual_creator == expected_creator


@pytest.mark.parametrize(
    "data, expected_sizes",
    [
        ({}, (None, None)),
        ({"sourceFile": {}}, (None, None)),
        ({"sourceFile": {"sizes": "123x321"}}, (123, 321)),
        ({"sourceFile": {"sizes": "413.39108x272.68854"}}, (413, 272)),
    ],
)
def test__get_image_sizes(data, expected_sizes):
    actual_sizes = pp._get_image_sizes(data)
    assert actual_sizes == expected_sizes


def test_get_record_data():
    data = get_json("sample_record.json")
    image = pp.get_record_data(data)
    license_info = get_license_info(
        license_url="https://creativecommons.org/publicdomain/zero/1.0/"
    )

    assert image == {
        "license_info": license_info,
        "foreign_identifier": "5b1e88b5-159d-495d-b8cb-04f9e28d2f02",
        "foreign_landing_url": "https://www.phylopic.org/images/5b1e88b5-159d-495d-b8cb-04f9e28d2f02?build=194",
        "image_url": "https://images.phylopic.org/images/5b1e88b5-159d-495d-b8cb-04f9e28d2f02/source.svg",
        "title": "Hemaris tityus",
        "creator": "Andy Wilson",
        "creator_url": "https://www.phylopic.org/contributors/c3ac6939-e85a-4a10-99d1-4079537f34de?build=194",
        "width": 2048,
        "height": 2048,
    }
