
import os
import json
import logging
import requests
from unittest.mock import patch, MagicMock
import finnish_museums as fm


RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "tests/resources/finnishmuseums"
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG
)


def _get_resource_json(json_name):
    with open(os.path.join(RESOURCES, json_name)) as f:
        resource_json = json.load(f)
    return resource_json

def test_get_object_list_with_none_response():
    with patch.object(
            fm.delayed_requester,
            'get_response_json',
            return_value=None
    ) as mock_get:
        fm._get_object_list('some_museum', retries=3)

    assert mock_get.call_count == 1

def test_get_object_list_with_empty_response():
    json_resp = {
        'records':[]
    }
    with patch.object(
            fm.delayed_requester,
            'get_response_json',
            return_value=json_resp
    ) as mock_get:
        obj_list =fm._get_object_list('some_museum', retries=3)

    assert mock_get.call_count == 1
    assert obj_list is None

def test_build_query_param_default():
    
    actual_param_made = fm._build_params(
        building='0/Museovirasto/'
    )
    expected_param = {
        'filter[]':['format:"0/Image/"','building:"0/Museovirasto/"'],
        'limit':100,
        'page':1
    }
    assert actual_param_made == expected_param

def test_build_query_param_given():
    building = '0/Museovirasto/'
    page=2
    actual_param_made = fm._build_params(
        building=building,
        page=page
    )
    expected_param = {
        'filter[]':['format:"0/Image/"','building:"0/Museovirasto/"'],
        'limit':100,
        'page':2
    }
    assert actual_param_made == expected_param

def test_get_object_list_from_json_returns_expected_output():
    json_resp = _get_resource_json(
        'finna_full_response_example.json'
    )
    actual_items_list = fm._get_object_list_from_json(
        json_resp
    )
    expect_items_list = _get_resource_json('object_list_example.json')
    assert actual_items_list == expect_items_list

def test_get_object_list_return_none_if_empty():
    test_dict = {
        'records':[]
    }
    assert fm._get_object_list_from_json(test_dict) is None

def test_get_object_list_return_none_if_missing():
    test_dict = {}
    assert fm._get_object_list_from_json(test_dict) is None

def test_get_object_list_return_none_if_none_json():
    
    assert fm._get_object_list_from_json(None) is None

def test_process_object_with_real_example():
    object_data = _get_resource_json("object_complete_example.json")
    with patch.object(fm.image_store, "add_item", return_value=100) as mock_add_item:
        total_images = fm._process_object(object_data)


    mock_add_item.assert_called_once_with(
        license_url =('http://creativecommons.org/licenses/by/4.0/deed.fi'),
        foreign_identifier =('museovirasto.CC0641BB5337F541CBD19169838BAC1F'),
        image_url =('https://api.finna.fi/Cover/Show?id=museovirasto.CC0641BB5337F541CBD19169838BAC1F&index=0&size=large'),
        title = ('linnunpönttö koivussa'),
        source = ('finnish_heritage_agency'),
        raw_tags = [
        [
            "koivu"
        ],
        [
            "linnunpöntöt"
        ],
        [
            "Revonristi"
        ],
        [
            "valmistusaika: 11.06.1923"
        ]
    ]
    )
    assert total_images == 100

def test_get_landing():
    response_json = _get_resource_json('object_complete_example.json')
    landing_url = fm._get_landing(response_json)
    expected_landing_url = 'https://www.finna.fi/Record/museovirasto.CC0641BB5337F541CBD19169838BAC1F'
    assert landing_url == expected_landing_url

def test_get_image_url():
    response_json = _get_resource_json('full_image_object.json')
    image_url = fm._get_image_url(response_json)
    expected_image_url = 'https://api.finna.fi/Cover/Show?id=museovirasto.CC0641BB5337F541CBD19169838BAC1F&index=0&size=large'
    assert image_url == expected_image_url





