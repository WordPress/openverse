import Flickr
from datetime import datetime
import os

def test_process_images(monkeypatch):
    cur_time = datetime.strptime('2019-12-01', '%Y-%m-%d')
    nxt_time = datetime.strptime('2019-12-02', '%Y-%m-%d')
    def mockresult(a_url):
        return {
            "photos": {
                "page": 1,
                "pages": 1,
                "perpage": 500,
                "total": "2",
                "photo": [
                    {
                        "id": "123",
                        "owner": "123@N07",
                        "title": "rpk 10 ans-8",
                        "license": "3",
                        "description": {
                            "_content": ""
                        },
                        "dateupload": "1572340565",
                        "datetaken": "2019-09-07 16:27:59",
                        "ownername": "Tom-C photographe",
                        "tags": "",
                        "url_t": "https://live.staticflickr.com/123_t.jpg",
                        "height_t": 100,
                        "width_t": 75,
                        "url_s": "https://live.staticflickr.com/123_m.jpg",
                        "height_s": 240,
                        "width_s": 180,
                        "url_m": "https://live.staticflickr.com/123.jpg",
                        "height_m": 500,
                        "width_m": 375,
                        "url_l": "https://live.staticflickr.com/123_b.jpg",
                        "height_l": 1024,
                        "width_l": 768
                    },
                    {
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
                    },
                ]
            },
            "stat": "ok"
        }
    tmp_directory = '/tmp/'
    output_filename = 'flickr_test.tsv'
    monkeypatch.setattr(Flickr.em, "requestContent", mockresult)
    monkeypatch.setattr(Flickr.em.writeToFile, '__defaults__', (tmp_directory,))
    monkeypatch.setattr(Flickr, "FILE", output_filename)
    output_fullpath = os.path.join(tmp_directory, output_filename)
    try:
        os.remove(output_fullpath)
    except:
        print("Could not delete old output.  Perhaps it does not exist yet.")
    expected_records = 2
    actual_records = Flickr.process_images(cur_time, nxt_time, 'potato')
    assert expected_records == actual_records
    expected_filestring = """123\twww.flickr.com/photos/123@N07/123\thttps://live.staticflickr.com/123_b.jpg\thttps://live.staticflickr.com/123_m.jpg\t768\t1024\t\\N\tby-nc-nd\t2.0\tTom-C photographe\twww.flickr.com/photos/123@N07\trpk 10 ans-8\t{"pub_date": "1572340565", "date_taken": "2019-09-07 16:27:59"}\t\\N\tf\tflickr\tflickr\n456\twww.flickr.com/photos/456@N04/456\thttps://live.staticflickr.com/456_b.jpg\thttps://live.staticflickr.com/456_m.jpg\t1024\t768\t\\N\tby-nc-nd\t2.0\tRADIOfotoGRAFIANDO\twww.flickr.com/photos/456@N04\t233 Ordesa sept 2019\t{"pub_date": "1571326372", "date_taken": "2019-09-07 16:26:44", "description": "OLYMPUS DIGITAL CAMERA"}\t[{"name": "amarilla", "provider": "flickr"}]\tf\tflickr\tflickr\n"""
    with open(output_fullpath) as f:
        actual_filestring = f.read()
    assert expected_filestring == actual_filestring


def test_process_images_handles_missing_required_info(monkeypatch):
    cur_time = datetime.strptime('2019-12-01', '%Y-%m-%d')
    nxt_time = datetime.strptime('2019-12-02', '%Y-%m-%d')
    def mockresult(a_url):
        return {
            "photos": {
                "page": 1,
                "pages": 1,
                "perpage": 500,
                "total": "2",
                "photo": [
                    {
                        "id": "123",
                        "owner": "123@N07",
                        "title": "rpk 10 ans-8",
                        "license": "3",
                        "description": {
                            "_content": ""
                        },
                        "dateupload": "1572340565",
                        "datetaken": "2019-09-07 16:27:59",
                        "ownername": "Tom-C photographe",
                        "tags": "",
                        "url_t": "https://live.staticflickr.com/123_t.jpg",
                        "height_t": 100,
                        "width_t": 75,
                        "url_s": "https://live.staticflickr.com/123_m.jpg",
                        "height_s": 240,
                        "width_s": 180,
                        "url_m": "https://live.staticflickr.com/123.jpg",
                        "height_m": 500,
                        "width_m": 375,
                        "url_l": "https://live.staticflickr.com/123_b.jpg",
                        "height_l": 1024,
                        "width_l": 768
                    },
                    {
                        "id": "456",
                        "owner": "456@N04",
                        "title": "233 Ordesa sept 2019",
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
                    },
                ]
            },
            "stat": "ok"
        }
    tmp_directory = '/tmp/'
    output_filename = 'flickr_test.tsv'
    monkeypatch.setattr(Flickr.em, "requestContent", mockresult)
    monkeypatch.setattr(Flickr.em.writeToFile, '__defaults__', (tmp_directory,))
    monkeypatch.setattr(Flickr, "FILE", output_filename)
    output_fullpath = os.path.join(tmp_directory, output_filename)
    try:
        os.remove(output_fullpath)
    except:
        print("Could not delete old output.  Perhaps it does not exist yet.")
    expected_records = 1
    actual_records = Flickr.process_images(cur_time, nxt_time, 'potato')
    assert expected_records == actual_records
    expected_filestring = """123\twww.flickr.com/photos/123@N07/123\thttps://live.staticflickr.com/123_b.jpg\thttps://live.staticflickr.com/123_m.jpg\t768\t1024\t\\N\tby-nc-nd\t2.0\tTom-C photographe\twww.flickr.com/photos/123@N07\trpk 10 ans-8\t{"pub_date": "1572340565", "date_taken": "2019-09-07 16:27:59"}\t\\N\tf\tflickr\tflickr\n"""
    with open(output_fullpath) as f:
        actual_filestring = f.read()
    assert expected_filestring == actual_filestring


def test_process_images_handles_empty_json(monkeypatch):
    cur_time = datetime.strptime('2019-12-01', '%Y-%m-%d')
    nxt_time = datetime.strptime('2019-12-02', '%Y-%m-%d')
    def mockresult(a_url):
        return {}
    monkeypatch.setattr(Flickr.em, "requestContent", mockresult)
    expected_records = 0
    actual_records = Flickr.process_images(cur_time, nxt_time, 'potato')
    assert expected_records == actual_records


def test_process_images_handles_Nonetype(monkeypatch):
    cur_time = datetime.strptime('2019-12-01', '%Y-%m-%d')
    nxt_time = datetime.strptime('2019-12-02', '%Y-%m-%d')
    def mockresult(a_url):
        return None
    expected_records = 0
    actual_records = Flickr.process_images(cur_time, nxt_time, 'potato')
    assert expected_records == actual_records


def test_construct_api_query_string_default():
    cur_time = datetime.strptime('2019-12-01', '%Y-%m-%d')
    nxt_time = datetime.strptime('2019-12-02', '%Y-%m-%d')
    actual_url = Flickr.construct_api_query_string(
        cur_time,
        nxt_time,
        3,
        1
    )
    expected_url = 'https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=notset&min_upload_date=2019-12-01 00:00:00&max_upload_date=2019-12-02 00:00:00&license=3&media=photos&content_type=1&extras=description,license,date_upload,date_taken,owner_name,tags,o_dims,url_t,url_s,url_m,url_l&per_page=500&format=json&nojsoncallback=1&page=1'
    assert actual_url == expected_url


def test_construct_api_query_string_with_switch():
    cur_time = datetime.strptime('2019-12-01', '%Y-%m-%d')
    nxt_time = datetime.strptime('2019-12-02', '%Y-%m-%d')
    actual_url = Flickr.construct_api_query_string(
        cur_time,
        nxt_time,
        3,
        1,
        switch_date=True
    )
    expected_url = 'https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=notset&min_taken_date=2019-12-01 00:00:00&max_taken_date=2019-12-02 00:00:00&license=3&media=photos&content_type=1&extras=description,license,date_upload,date_taken,owner_name,tags,o_dims,url_t,url_s,url_m,url_l&per_page=500&format=json&nojsoncallback=1&page=1'
    assert actual_url == expected_url



def test_extract_data_returns_Nonetype_if_no_image():
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
    actual_row = Flickr.extract_data(data)
    expect_row = None
    assert expect_row == actual_row


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
    actual_tuple = Flickr.get_image_url(data)
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
    actual_tuple = Flickr.get_image_url(data)
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
    actual_tuple = Flickr.get_image_url(data)
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
    actual_tuple = Flickr.get_image_url(data)
    expect_tuple = ('https://live.staticflickr.com/456_m.jpg', 180, 240)
    assert expect_tuple == actual_tuple


def test_extract_data_returns_Nonetype_when_no_license():
    data = {
        "id": "456",
        "owner": "456@N04",
        "title": "233 Ordesa sept 2019",
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
        "url_l": "https://live.staticflickr.com/456_b.jpg",
        "height_l": 768,
        "width_l": 1024
    }
    actual_row = Flickr.extract_data(data)
    expect_row = None
    assert expect_row == actual_row


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
    }
    actual_dict = Flickr.create_meta_data_dict(data)
    expect_dict = {
        'pub_date': '1571326372',
        'date_taken': '2019-09-07 16:26:44',
        'description': 'OLYMPUS DIGITAL CAMERA'
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
    actual_dict = Flickr.create_meta_data_dict(data)
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
    actual_dict = Flickr.create_meta_data_dict(data)
    expect_dict = {}
    assert expect_dict == actual_dict


def test_create_tags_list_makes_tags_list():
    data = {
        "id": "456",
        "tags": "tag1 tag2   tag3  tag3 ",
        "width_l": 1024
    }
    actual_tags_list = Flickr.create_tags_list(data)
    expect_tags_list = [
        {
            'name': 'tag1',
            'provider': 'flickr'
        },
        {
            'name': 'tag2',
            'provider': 'flickr'
        },
        {
            'name': 'tag3',
            'provider': 'flickr'
        }
    ]
    assert len(actual_tags_list) == len(expect_tags_list)
    assert all(
        [element in actual_tags_list for element in expect_tags_list]
    )


def test_create_tags_list_returns_falsy_no_tag_key():
    data = {'id': 'aslkjb'}
    tags_list = Flickr.create_tags_list(data)
    assert not tags_list


def test_create_tags_list_returns_falsy_empty_tags():
    data = {'id': 'aslkjb', 'tags': ''}
    tags_list = Flickr.create_tags_list(data)
    assert not tags_list
