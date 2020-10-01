import os
import json
import logging
import requests
from unittest.mock import patch, MagicMock
import walters_art_museum as wam


RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'tests/resources/waltersartmuseum'
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)


def _get_resource_json(json_resource):
    with open(os.path.join(RESOURCES, json_resource)) as file:
        json_resource = json.load(file)
    return json_resource


# _get_image_list test suite
def test_get_image_list_retries_with_none_response():
    with patch.object(
            wam.delayed_requester,
            'get_response_json',
            return_value=None
    ) as mock_get:
        wam._get_image_list('some_class', retries=3)

    assert mock_get.call_count == 1


def test_get_image_list_retries_with_non_ok_response():
    response_json = _get_resource_json('walters_full_response_example.json')
    r = requests.Response()
    r.status_code = 504
    r.json = MagicMock(return_value=response_json)
    with patch.object(
            wam.delayed_requester,
            'get_response_json',
            return_value=r.json()
    ) as mock_get:
        wam._get_image_list('some_class', retries=3)

    assert mock_get.call_count == 1


def test_get_image_list_with_full_response():
    response_json = _get_resource_json('walters_full_response_example.json')
    r = requests.Response()
    r.status_code = 200
    r.json = MagicMock(return_value=response_json)
    with patch.object(
            wam.delayed_requester,
            'get_response_json',
            return_value=r.json()
    ) as mock_get:
        image_list = wam._get_image_list('Manuscripts & Rare Books', retries=3)

    # Here image list is same as items list because test example has only one
    # page and image. In case of more than one pages the image list will be
    # contain all images of more than one items list.
    expect_image_list = _get_resource_json('items_list_example.json')
    assert mock_get.call_count == 1
    assert image_list == expect_image_list


# _build_query_param test suite
# This test fails if default constants change.
def test_build_query_param_default():
    walters_api_key = 'notset'
    actual_param_made = wam._build_query_param(
        apikey=walters_api_key
    )
    expected_param = {
        'accept': 'json',
        'apikey': walters_api_key,
        'pageSize': 100,
        'orderBy': 'classification',
        'classification': None
    }
    assert actual_param_made == expected_param


def test_build_query_param_given():
    walters_api_key = 'notset'
    class_param = 'someclass'
    actual_param_made = wam._build_query_param(
        class_param=class_param,
        apikey=walters_api_key
    )
    expected_param = {
        'accept': 'json',
        'apikey': walters_api_key,
        'pageSize': 100,
        'orderBy': 'classification',
        'classification': class_param
    }
    assert actual_param_made == expected_param


# _extract_image_list_from_json test suite
def test_extract_items_list_from_json_returns_expected_output():
    json_response_inpydict_form = _get_resource_json(
        'walters_full_response_example.json'
    )
    actual_items_list = wam._extract_items_list_from_json(
        json_response_inpydict_form
    )
    expect_items_list = _get_resource_json('items_list_example.json')
    assert actual_items_list == expect_items_list


def test_extract_items_list_from_json_returns_nones_given_false_return_stat():
    test_dict = {
        "ReturnStatus": False,
        "ReturnCode": 404
    }
    assert wam._extract_items_list_from_json(test_dict) is None


def test_extract_items_list_from_json_handles_missing_Items():
    test_dict = {
        "ReturnStatus": True,
        "ReturnCode": 200
    }
    assert wam._extract_items_list_from_json(test_dict) is None


def test_extract_items_list_from_json_handles_missing_imgs_in_Items():
    test_dict = {
        "Items": [],
        "ReturnStatus": True,
        "ReturnCode": 200
    }
    assert wam._extract_items_list_from_json(test_dict) is None


def test_extract_items_list_from_json_returns_nones_given_none_json():
    assert wam._extract_items_list_from_json(None) is None


# _process_image test suite
def test_process_image_returns_expected_output_given_right_input():
    image = _get_resource_json('full_image_object.json')
    with patch.object(
            wam.image_store,
            'add_item',
            return_value=100
    ) as mock_add_item:
        total_images = wam._process_image(image)

    expect_meta_data = {
        "ObjectNumber": "W.569.4A",
        "PublicAccessDate": "2014-04-25T13:19:25.22",
        "Collection": "Manuscripts",
        "Medium": "ink and pigments on thick cream-colored, gold-flecked paper",
        "Classification": "Manuscripts & Rare Books",
        "Description": "abc",
        "CreditLine": "Acquired by Henry Walters",
    }

    mock_add_item.assert_called_once_with(
                foreign_landing_url="http://art.thewalters.org/detail/2",
                image_url="http://static.thewalters.org/images/CPS_W.569.4a_Fp_DD.jpg",
                thumbnail_url="http://static.thewalters.org/images/CPS_W.569.4a_Fp_DD.jpg?width=100",
                license_url="https://creativecommons.org/publicdomain/zero/1.0/",
                foreign_identifier="W.569.4A",
                creator="Iranian",
                creator_url="https://art.thewalters.org/browse/iranian",
                title="Leaf from Qur'an",
                meta_data=expect_meta_data
    )

    assert total_images == 100


# _get_creator_info test suite
def test_get_creator_info_returns_expected_output_given_right_input():
    response_json = _get_resource_json('full_image_object.json')
    actual_creator, actual_creator_url = wam._get_creator_info(response_json)
    expected_creator = "Iranian"
    expected_creator_url = "https://art.thewalters.org/browse/iranian"

    assert actual_creator == expected_creator
    assert actual_creator_url == expected_creator_url


def test_get_creator_info_returns_none_given_no_creator_info():
    response_json = _get_resource_json('no_creator_info.json')
    actual_creator, actual_creator_url = wam._get_creator_info(response_json)
    expected_creator = None
    expected_creator_url = None

    assert actual_creator == expected_creator
    assert actual_creator_url == expected_creator_url


# get_meta_data test suite
def test_get_image_meta_data_returns_full_meta_data_given_right_input():
    response_json = _get_resource_json("full_image_object.json")
    actual_metadata = wam._get_image_meta_data(response_json)
    expected_metadata = {
      "ObjectNumber": "W.569.4A",
      "PublicAccessDate": "2014-04-25T13:19:25.22",
      "Collection": "Manuscripts",
      "Medium": "ink and pigments on thick cream-colored, gold-flecked paper",
      "Classification": "Manuscripts & Rare Books",
      "Description": "abc",
      "CreditLine": "Acquired by Henry Walters",
    }

    assert actual_metadata == expected_metadata


def test_get_image_meta_data_returns_partial_meta_data():
    response_json = _get_resource_json("partial_meta_data.json")
    actual_metadata = wam._get_image_meta_data(response_json)
    expected_metadata = {
      "ObjectNumber": "W.569.4A",
      "PublicAccessDate": "2014-04-25T13:19:25.22",
      "Collection": "Manuscripts",
      "Medium": "ink and pigments on thick cream-colored, gold-flecked paper"
    }

    assert actual_metadata == expected_metadata


def test_get_image_meta_data_return_empty_dict_given_no_meta_data():
    response_json = _get_resource_json("no_meta_data.json")
    actual_metadata = wam._get_image_meta_data(response_json)
    expected_metadata = {}
    assert actual_metadata == expected_metadata
