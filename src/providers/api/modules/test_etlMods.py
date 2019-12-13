import etlMods
import json

def test_create_tsv_list_row_returns_none_if_missing_foreign_landing_url():
    expect_row = None
    actual_row = etlMods.create_tsv_list_row(
        foreign_identifier='a',
        image_url = 'a',
        license_ = 'abc'
    )
    assert expect_row == actual_row

def test_create_tsv_list_row_returns_none_if_missing_license():
    expect_row = None
    actual_row = etlMods.create_tsv_list_row(
        foreign_identifier='a',
        image_url = 'a',
        foreign_landing_url = 'www.testurl.com'
    )
    assert expect_row == actual_row

def test_create_tsv_list_row_returns_none_if_missing_image_url():
    expect_row = None
    actual_row = etlMods.create_tsv_list_row(
        foreign_identifier='a',
        foreign_landing_url = 'www.testurl.com',
        license_ = 'abc'
    )
    assert expect_row == actual_row

def test_create_tsv_list_row_casts_to_strings():
    meta_data = {'key1': 'value1', 'key2': 'value2'}
    tags = [
        {'name': 'valuea', 'provider': 'valueb'},
        {'name': 'aname', 'provider': 'aprovider'}
    ]
    height = 234
    width = 102314

    actual_row = etlMods.create_tsv_list_row(
        foreign_landing_url = 'www.testurl.comk',
        image_url = 'a',
        license_ = 'abc',
        width = width,
        height = height,
        meta_data = meta_data,
        tags = tags
    )
    assert all([type(element) == str for element in actual_row])


def test_create_tsv_list_row_handles_empty_dict_and_tags():
    meta_data = {}
    tags = []

    actual_row = etlMods.create_tsv_list_row(
        foreign_landing_url = 'www.testurl.comk',
        image_url = 'a',
        license_ = 'abc',
        meta_data = meta_data,
        tags = tags
    )
    actual_meta_data, actual_tags = actual_row[12], actual_row[13]
    expect_meta_data, expect_tags = '\\N', '\\N'
    assert expect_meta_data == actual_meta_data
    assert expect_tags == actual_tags


def test_create_tsv_list_row_turns_empty_into_nullchar():
    req_args_dict = {
        'foreign_landing_url': 'landing_page.com',
        'image_url': 'imageurl.com',
        'license_': 'testlicense',
    }
    args_dict = {
        'foreign_identifier': None,
        'thumbnail': None,
        'width': None,
        'height': None,
        'filesize': None,
        'license_version': None,
        'creator': None,
        'creator_url': None,
        'title': None,
        'meta_data': None,
        'tags': None,
        'watermarked': 'f',
        'provider': None,
        'source': None
    }
    args_dict.update(req_args_dict)

    actual_row = etlMods.create_tsv_list_row(
        **args_dict
    )
    expect_row = [
        '\\N',
        'landing_page.com',
        'imageurl.com',
        '\\N',
        '\\N',
        '\\N',
        '\\N',
        'testlicense',
        '\\N',
        '\\N',
        '\\N',
        '\\N',
        '\\N',
        '\\N',
        'f',
        '\\N',
        '\\N'
    ]


def test_create_tsv_list_row_properly_places_entries():
    req_args_dict = {
        'foreign_landing_url': 'landing_page.com',
        'image_url': 'imageurl.com',
        'license_': 'testlicense',
    }
    args_dict = {
        'foreign_identifier': 'foreign_id',
        'thumbnail': 'thumbnail.com',
        'width': 200,
        'height': 500,
        'license_version': '1.0',
        'creator': 'tyler',
        'creator_url': 'creatorurl.com',
        'title': 'agreatpicture',
        'meta_data': {'description': 'cat picture'},
        'tags': [{'name': 'tag1', 'provider': 'testing'}],
        'watermarked': 'f',
        'provider': 'testing',
        'source': 'testing'
    }
    args_dict.update(req_args_dict)

    actual_row = etlMods.create_tsv_list_row(
        **args_dict
    )
    expect_row = [
        'foreign_id',
        'landing_page.com',
        'imageurl.com',
        'thumbnail.com',
        '200',
        '500',
        '\\N',
        'testlicense',
        '1.0',
        'tyler',
        'creatorurl.com',
        'agreatpicture',
        '{"description": "cat picture"}',
        '[{"name": "tag1", "provider": "testing"}]',
        'f',
        'testing',
        'testing'
    ]
    assert expect_row == actual_row
