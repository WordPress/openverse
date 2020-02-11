import json
import logging
import os
from unittest.mock import patch

import flickr

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'tests/resources/flickr'
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG,
)


def _get_resource_json(json_name):
    with open(os.path.join(RESOURCES, json_name)) as f:
        resource_json = json.load(f)
    return resource_json


def test_get_image_list_retries_with_none_response():
    with patch.object(
            flickr.delayed_requester,
            'get',
            return_value=None
    ) as mock_get:
        flickr._get_image_list('1234', '5678', 'test', 4, retries=2)

    assert mock_get.call_count == 3


# This test will fail if default constants change.
def test_build_query_param_dict_default():
    cur_time = '12345'
    nxt_time = '12346'
    flickr_api_key = 'notset'
    actual_query_param_dict = flickr._build_query_param_dict(
        cur_time,
        nxt_time,
        3,
        'test',
        api_key=flickr_api_key
    )
    expect_query_param_dict = {
        'media': 'photos',
        'content_type': 1,
        'extras': 'description,license,date_upload,date_taken,owner_name,tags,o_dims,url_t,url_s,url_m,url_l,views',
        'format': 'json',
        'nojsoncallback': 1,
        'min_test_date': cur_time,
        'max_test_date': nxt_time,
        'page': 3,
        'api_key': flickr_api_key,
        'license': '1,2,3,4,5,6,9,10',
        'per_page': 500,
    }
    assert actual_query_param_dict == expect_query_param_dict


def test_build_query_param_dict_with_givens():
    cur_time = '12345'
    nxt_time = '12346'
    flickr_api_key = 'notset'
    actual_query_param_dict = flickr._build_query_param_dict(
        cur_time,
        nxt_time,
        3,
        'test',
        api_key=flickr_api_key,
        license_info={
            '1': ('by-nc-sa', '2.0'),
            '2': ('by-nc', '2.0'),
        },
        limit=10,
        default_query_param={
            'media': 'photos',
            'extras': 'url_t,url_s,url_m,url_l,views',
            'nojsoncallback': 1,
        }
    )
    expect_query_param_dict = {
        'media': 'photos',
        'extras': 'url_t,url_s,url_m,url_l,views',
        'nojsoncallback': 1,
        'min_test_date': cur_time,
        'max_test_date': nxt_time,
        'page': 3,
        'api_key': flickr_api_key,
        'license': '1,2',
        'per_page': 10,
    }
    assert actual_query_param_dict == expect_query_param_dict


def test_process_image_data():
    pass


def test_get_image_url_returns_Nonetype_tuple_if_no_image():
    data = _get_resource_json('image_data_no_image_url.json')
    actual_tuple = flickr._get_image_url(data)
    expect_tuple = (None, None, None)
    assert expect_tuple == actual_tuple


def test_get_image_url_returns_large_tuple_when_avail():
    image_data = _get_resource_json('image_data_with_large_url_available.json')
    actual_tuple = flickr._get_image_url(image_data)
    expect_tuple = ('https://live.staticflickr.com/456_b.jpg', 768, 1024)
    assert expect_tuple == actual_tuple


def test_get_image_url_returns_medium_tuple_when_large_not_avail():
    data = _get_resource_json('image_data_with_med_url_available.json')
    actual_tuple = flickr._get_image_url(data)
    expect_tuple = ('https://live.staticflickr.com/456.jpg', 375, 500)
    assert expect_tuple == actual_tuple


def test_get_image_url_falls_to_small_tuple():
    data = _get_resource_json('image_data_with_small_url_available.json')
    actual_tuple = flickr._get_image_url(data)
    expect_tuple = ('https://live.staticflickr.com/456_m.jpg', 180, 240)
    assert expect_tuple == actual_tuple


def test_get_license_with_int_license_id():
    license_info = {
        '1': ('by-nc-sa', '2.0'),
        '2': ('by-nc', '2.0'),
    }
    actual_license, actual_license_version = flickr._get_license(
        2,
        license_info=license_info
    )
    expect_license, expect_license_version = 'by-nc', '2.0'
    assert expect_license == actual_license
    assert expect_license_version == actual_license_version


def test_get_license_with_str_license_id():
    license_info = {
        '1': ('by-nc-sa', '2.0'),
        '2': ('by-nc', '2.0'),
    }
    actual_license, actual_license_version = flickr._get_license(
        '2',
        license_info=license_info
    )
    expect_license, expect_license_version = 'by-nc', '2.0'
    assert expect_license == actual_license
    assert expect_license_version == actual_license_version


def test_get_license_with_missing_license_id():
    license_info = {
        '1': ('by-nc-sa', '2.0'),
        '2': ('by-nc', '2.0'),
    }
    actual_license, actual_license_version = flickr._get_license(
        12,
        license_info=license_info
    )
    assert actual_license is None
    assert actual_license_version is None


def test_create_meta_data_fills_meta_data_dict():
    data = _get_resource_json('image_data_full_example.json')
    actual_dict = flickr._create_meta_data_dict(data)
    expect_dict = {
        'pub_date': '1571326372',
        'date_taken': '2019-09-07 16:26:44',
        'description': 'OLYMPUS DIGITAL CAMERA',
        'views': '9'
    }
    assert expect_dict == actual_dict


def test_create_meta_data_fills_partial_meta_data_dict():
    data = _get_resource_json('image_data_partial_meta_data_info.json')
    actual_dict = flickr._create_meta_data_dict(data)
    expect_dict = {
        'pub_date': '1571326372',
        'date_taken': '2019-09-07 16:26:44'
    }
    assert expect_dict == actual_dict


def test_create_meta_data_makes_empty_meta_data_dict():
    data = _get_resource_json('image_data_no_meta_data_info.json')
    actual_dict = flickr._create_meta_data_dict(data)
    expect_dict = {}
    assert expect_dict == actual_dict


def test_create_meta_data_dict_strips_html():
    data = _get_resource_json('image_data_html_description.json')
    actual_dict = flickr._create_meta_data_dict(data)
    expect_dict = _get_resource_json(
        'expect_meta_data_from_html_description.json'
    )
    assert expect_dict == actual_dict


def test_create_meta_data_handles_whitespace_description():
    data = _get_resource_json('image_data_whitespace_description.json')
    actual_dict = flickr._create_meta_data_dict(data)
    expect_dict = _get_resource_json(
        'expect_meta_data_from_whitespace_description.json'
    )
    assert expect_dict == actual_dict


def test_create_tags_list_makes_tags_list():
    data = _get_resource_json('image_data_varying_tags_whitespace.json')
    actual_tags_list = flickr._create_tags_list(data)
    expect_tags_list = ['tag1', 'tag2', 'tag3']
    assert len(actual_tags_list) == len(expect_tags_list)
    assert all(
        [element in actual_tags_list for element in expect_tags_list]
    )


def test_create_tags_list_returns_falsy_no_tag_key():
    data = {'id': 'aslkjb'}
    tags_list = flickr._create_tags_list(data)
    assert not tags_list


def test_create_tags_list_returns_falsy_empty_tags():
    data = {'id': 'aslkjb', 'tags': ''}
    tags_list = flickr._create_tags_list(data)
    assert not tags_list
