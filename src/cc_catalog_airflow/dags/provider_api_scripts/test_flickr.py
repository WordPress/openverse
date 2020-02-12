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


def test_extract_image_list_from_json_handles_realistic_input():
    test_dict = _get_resource_json('flickr_example_pretty.json')
    expect_image_list = _get_resource_json('flickr_example_photo_list.json')
    expect_total_pages = 1
    for item in expect_image_list:
        print(item)
    actual_image_list, actual_total_pages = (
        flickr._extract_image_list_from_json(test_dict)
    )
    assert actual_image_list == expect_image_list
    assert actual_total_pages == expect_total_pages


def test_extract_image_list_from_json_handles_missing_photo_list():
    test_dict = {'stat': 'ok', 'photos': {}}
    assert flickr._extract_image_list_from_json(test_dict)[0] is None


def test_extract_image_list_from_json_handles_missing_photos():
    test_dict = {'stat': 'ok', 'abc': 'def'}
    assert flickr._extract_image_list_from_json(test_dict) == (None, None)


def test_extract_image_list_from_json_returns_nones_given_non_ok_stat():
    test_dict = {'stat': 'notok', 'abc': 'def'}
    assert flickr._extract_image_list_from_json(test_dict) == (None, None)


def test_extract_image_list_from_json_returns_nones_given_none_json():
    assert flickr._extract_image_list_from_json(None) == (None, None)


def test_process_image_data_with_real_example():
    image_data = _get_resource_json('image_data_complete_example.json')
    with patch.object(
            flickr.image_store,
            'add_item',
            return_value=100
    ) as mock_add_item:
        total_images = flickr._process_image_data(image_data)

    expect_meta_data = {
        'pub_date': '1581318235',
        'date_taken': '2020-02-10 09:38:16',
        'views': '70',
        'description': 'We had spectacular underwater scenery with great visibility today despite the big seas and winds at Lord Howe Island.'
    }

    mock_add_item.assert_called_once_with(
        foreign_landing_url='https://www.flickr.com/photos/71925535@N03/49514824541',
        image_url='https://live.staticflickr.com/65535/49514824541_35d1b4f8db_b.jpg',
        thumbnail_url='https://live.staticflickr.com/65535/49514824541_35d1b4f8db_m.jpg',
        license_='by-nc-sa',
        license_version='2.0',
        foreign_identifier='49514824541',
        width=1024,
        height=683,
        creator='Marine Explorer',
        creator_url='https://www.flickr.com/photos/71925535@N03',
        title='Surveying Ruperts Reef @reeflifesurvey #lapofaus #marineexplorer',
        meta_data=expect_meta_data,
        raw_tags=[
            'australia',
            'marine',
            'marineexplorer',
            'nature',
            'scuba',
            'underwater'
        ]
    )
    assert total_images == 100


def test_build_creator_url_nones_missing_owner():
    image_data = _get_resource_json('image_data_long_tags_string.json')
    actual_url = flickr._build_creator_url(
        image_data,
        photo_url_base='https://photo.com'
    )
    assert actual_url is None


def test_build_creator_url_finds_owner():
    image_data = _get_resource_json('image_data_complete_example.json')
    actual_url = flickr._build_creator_url(
        image_data,
        photo_url_base='https://photo.com'
    )
    expect_url = 'https://photo.com/71925535@N03'
    assert actual_url == expect_url


def test_build_foreign_landing_url():
    actual_url = flickr._build_foreign_landing_url(
        'https://creator.com',
        'foreignid'
    )
    expect_url = 'https://creator.com/foreignid'
    assert actual_url == expect_url


def test_build_foreign_landing_url_nones_with_falsy_foreign_id():
    actual_url = flickr._build_foreign_landing_url(
        'https://creator.com',
        False
    )
    assert actual_url is None


def test_build_foreign_landing_url_nones_with_falsy_creator_url():
    assert flickr._build_foreign_landing_url('', 'abcde') is None


def test_url_join_no_trailing_slashes():
    expect_url = 'https://aurl.com/path/morepath/lastpath'
    actual_url = flickr._url_join(
        'https://aurl.com',
        'path',
        'morepath',
        'lastpath'
    )
    assert expect_url == actual_url


def test_url_join_with_slashes():
    expect_url = 'https://aurl.com/path/morepath/lastpath'
    actual_url = flickr._url_join(
        'https://aurl.com/',
        '/path/',
        '/morepath/',
        'lastpath'
    )
    assert expect_url == actual_url


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
    data = _get_resource_json('image_data_full_meta_data_example.json')
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


def test_create_tags_list_sorts_tags():
    data = _get_resource_json('image_data_unsorted_tags.json')
    actual_tags_list = flickr._create_tags_list(data)
    expect_tags_list = ['tag1', 'tag2', 'tag3']
    assert len(actual_tags_list) == len(expect_tags_list)
    assert all(
        [element in actual_tags_list for element in expect_tags_list]
    )


def test_create_tags_list_truncates_long_tags():
    data = _get_resource_json('image_data_long_tags_string.json')
    actual_tags_list = flickr._create_tags_list(data, max_tag_string_length=37)
    expect_tags_list = ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6']
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
