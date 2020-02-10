import logging
from unittest.mock import patch, MagicMock

import flickr


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG,
)


def test_get_image_list_retries_with_none_response():
    with patch.object(
            flickr.delayed_requester,
            'get',
            return_value=None
    ) as mock_get:
        flickr._get_image_list('1234', '5678', 'test', 4, retries=2)

    assert mock_get.call_count == 3


# This test will fail if default constants change.
def test_build_query_param_dict_default(monkeypatch):
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


def test_get_image_url_returns_Nonetype_tuple_if_no_image():
    data = {
        "id": "456",
        "owner": "456@N04",
        "title": "233 Ordesa sept 2019",
        "license": "3",
        "description": {
            "_content": "OLYMPUS DIGITAL CAMERA"
        },
        "dateupload": "1571326372",
        "datetaken": "2019-09-07 16:26:44",
        "ownername": "RADIOfotoGRAFIANDO",
        "tags": "amarilla",
        "url_t": "https://live.staticflickr.com/456_t.jpg",
        "height_t": 75,
        "width_t": 100,
    }
    actual_tuple = flickr._get_image_url(data)
    expect_tuple = (None, None, None)
    assert expect_tuple == actual_tuple


def test_get_image_url_returns_large_tuple_when_avail():
    data = {
        "id": "456",
        "owner": "456@N04",
        "title": "233 Ordesa sept 2019",
        "license": "3",
        "description": {
            "_content": "OLYMPUS DIGITAL CAMERA"
        },
        "dateupload": "1571326372",
        "datetaken": "2019-09-07 16:26:44",
        "ownername": "RADIOfotoGRAFIANDO",
        "tags": "amarilla",
        "url_t": "https://live.staticflickr.com/456_t.jpg",
        "height_t": 75,
        "width_t": 100,
        "url_s": "https://live.staticflickr.com/456_m.jpg",
        "height_s": 180,
        "width_s": 240,
        "url_m": "https://live.staticflickr.com/456.jpg",
        "height_m": 375,
        "width_m": 500,
        "url_l": "https://live.staticflickr.com/456_b.jpg",
        "height_l": 768,
        "width_l": 1024
    }
    actual_tuple = flickr._get_image_url(data)
    expect_tuple = ('https://live.staticflickr.com/456_b.jpg', 768, 1024)
    assert expect_tuple == actual_tuple


def test_get_image_url_returns_medium_tuple_when_large_not_avail():
    data = {
        "id": "456",
        "owner": "456@N04",
        "title": "233 Ordesa sept 2019",
        "license": "3",
        "description": {
            "_content": "OLYMPUS DIGITAL CAMERA"
        },
        "dateupload": "1571326372",
        "datetaken": "2019-09-07 16:26:44",
        "ownername": "RADIOfotoGRAFIANDO",
        "tags": "amarilla",
        "url_t": "https://live.staticflickr.com/456_t.jpg",
        "height_t": 75,
        "width_t": 100,
        "url_s": "https://live.staticflickr.com/456_m.jpg",
        "height_s": 180,
        "width_s": 240,
        "url_m": "https://live.staticflickr.com/456.jpg",
        "height_m": 375,
        "width_m": 500,
    }
    actual_tuple = flickr._get_image_url(data)
    expect_tuple = ('https://live.staticflickr.com/456.jpg', 375, 500)
    assert expect_tuple == actual_tuple


def test_get_image_url_falls_to_small_tuple():
    data = {
        "id": "456",
        "owner": "456@N04",
        "title": "233 Ordesa sept 2019",
        "license": "3",
        "description": {
            "_content": "OLYMPUS DIGITAL CAMERA"
        },
        "dateupload": "1571326372",
        "datetaken": "2019-09-07 16:26:44",
        "ownername": "RADIOfotoGRAFIANDO",
        "tags": "amarilla",
        "url_t": "https://live.staticflickr.com/456_t.jpg",
        "height_t": 75,
        "width_t": 100,
        "url_s": "https://live.staticflickr.com/456_m.jpg",
        "height_s": 180,
        "width_s": 240,
    }
    actual_tuple = flickr._get_image_url(data)
    expect_tuple = ('https://live.staticflickr.com/456_m.jpg', 180, 240)
    assert expect_tuple == actual_tuple


def test_create_meta_data_fills_meta_data_dict():
    data = {
        "title": "233 Ordesa sept 2019",
        "description": {
            "_content": "OLYMPUS DIGITAL CAMERA"
        },
        "dateupload": "1571326372",
        "datetaken": "2019-09-07 16:26:44",
        "ownername": "RADIOfotoGRAFIANDO",
        "tags": "amarilla",
        "views": "9"
    }
    actual_dict = flickr._create_meta_data_dict(data)
    expect_dict = {
        'pub_date': '1571326372',
        'date_taken': '2019-09-07 16:26:44',
        'description': 'OLYMPUS DIGITAL CAMERA',
        'views': '9'
    }
    assert expect_dict == actual_dict


def test_create_meta_data_fills_partial_meta_data_dict():
    data = {
        "title": "233 Ordesa sept 2019",
        "dateupload": "1571326372",
        "datetaken": "2019-09-07 16:26:44",
        "ownername": "RADIOfotoGRAFIANDO",
        "tags": "amarilla",
    }
    actual_dict = flickr._create_meta_data_dict(data)
    expect_dict = {
        'pub_date': '1571326372',
        'date_taken': '2019-09-07 16:26:44'
    }
    assert expect_dict == actual_dict


def test_create_meta_data_makes_empty_meta_data_dict():
    data = {
        "ownername": "RADIOfotoGRAFIANDO",
        "tags": "amarilla",
    }
    actual_dict = flickr._create_meta_data_dict(data)
    expect_dict = {}
    assert expect_dict == actual_dict


def test_create_meta_data_dict_strips_html():
    data = {
        "title": "233 Ordesa sept 2019",
        "description": {
            "_content": "Warsy (Somme, France) -\n\n<a href=\"https://www.google.com/maps/@49.69839,2.64689,3a,90y,102.98h,114.44t/data=!3m6!1e1!3m4!1s6s0eTwQy1M3dTex1cH7pVQ!2e0!7i13312!8i6656\" rel=\"noreferrer nofollow\">www.google.com/maps/@49.69839,2.64689,3a,90y,102.98h,114....</a>"
        },
        "dateupload": "1571326372",
        "datetaken": "2019-09-07 16:26:44",
        "ownername": "RADIOfotoGRAFIANDO",
        "tags": "amarilla",
        "views": "9"
    }
    actual_dict = flickr._create_meta_data_dict(data)
    expect_dict = {
        'pub_date': '1571326372',
        'date_taken': '2019-09-07 16:26:44',
        'description': 'Warsy (Somme, France) -\n\n www.google.com/maps/@49.69839,2.64689,3a,90y,102.98h,114....',
        'views': '9'
    }
    assert expect_dict == actual_dict


def test_create_tags_list_makes_tags_list():
    data = {
        "id": "456",
        "tags": "tag1 tag2   tag3  tag3 ",
        "width_l": 1024
    }
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
