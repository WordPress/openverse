import json
import logging
import os
from unittest.mock import patch

import wikimedia_commons as wmc

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'tests/resources/wikimedia'
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG,
)


def test_derive_timestamp_pair():
    # Note that the timestamps are derived as if input was in UTC.
    actual_start_ts, actual_end_ts = wmc._derive_timestamp_pair('2018-01-15')
    assert actual_start_ts == '1515974400'
    assert actual_end_ts == '1516060800'


def test_get_image_pages_returns_correctly_with_continue():
    with open(
            os.path.join(RESOURCES, 'response_small_with_continue.json')
    ) as f:
        resp_dict = json.load(f)

    expect_result = {
        '84798633': {
            'pageid': 84798633,
            'title': 'File:Ambassade1.jpg'
        }
    }
    actual_result = wmc._get_image_pages(resp_dict)
    assert actual_result == expect_result


def test_get_image_pages_returns_correctly_with_none_json():
    expect_result = None
    actual_result = wmc._get_image_pages(None)
    assert actual_result == expect_result


def test_get_image_pages_returns_correctly_with_no_pages():
    expect_result = None
    actual_result = wmc._get_image_pages({'batch_complete': ''})
    assert actual_result == expect_result


def test_build_query_params_adds_start_and_end():
    actual_qp = wmc._build_query_params(
        'abc', 'def', default_query_params={}
    )
    assert actual_qp['gaistart'] == 'abc'
    assert actual_qp['gaiend'] == 'def'


def test_build_query_params_leaves_other_keys():
    actual_qp = wmc._build_query_params(
        'abc', 'def', default_query_params={'test': 'value'}
    )
    assert actual_qp['test'] == 'value'


def test_build_query_params_adds_continue():
    actual_qp = wmc._build_query_params(
        'abc',
        'def',
        {'continuetoken': 'next.jpg'},
        default_query_params={'test': 'value'}
    )
    assert actual_qp['continuetoken'] == 'next.jpg'


def test_get_image_batch(monkeypatch):
    with open(
            os.path.join(RESOURCES, 'continuation', 'wmc_pretty1.json')
    ) as f:
        first_response = json.load(f)
    with open(
            os.path.join(RESOURCES, 'continuation', 'wmc_pretty2.json')
    ) as f:
        second_response = json.load(f)
    with open(
            os.path.join(RESOURCES, 'continuation', 'wmc_pretty3.json')
    ) as f:
        third_response = json.load(f)

    def mock_get_response_json(endpoint, retries, query_params, **kwargs):
        continue_one = 'Edvard_Munch_-_Night_in_Nice_(1891).jpg|nowiki|1281339'
        continue_two = 'Niedercunnersdorf_Gartenweg_12.JPG|dewiki|9849507'
        if 'continue' not in query_params:
            return first_response
        elif query_params['gucontinue'] == continue_one:
            return second_response
        elif query_params['gucontinue'] == continue_two:
            return third_response
        else:
            return None

    with open(
            os.path.join(RESOURCES, 'continuation', 'wmc_pretty123.json')
    ) as f:
        expect_image_batch = json.load(f)
    expect_image_batch.pop('continue')
    expect_continue_token = {
        'gaicontinue': (
            "20151031230201|Lancelot_'Capability'_BROWN_-_Wilderness_House_"
            "Moat_Lane_Hampton_Court_Palace_Hampton_Court_London_KT8_9AR.jpg"),
        'continue': 'gaicontinue||'
    }

    monkeypatch.setattr(wmc.delayed_requester, 'get_response_json',
                        mock_get_response_json)
    actual_image_batch, actual_continue_token = wmc._get_image_batch(
        '2019-01-01', '2019-01-02'
    )
    assert actual_image_batch == expect_image_batch
    assert actual_continue_token == expect_continue_token


def test_get_image_batch_returns_correctly_without_continue(monkeypatch):
    with open(
            os.path.join(RESOURCES, 'response_small_missing_continue.json')
    ) as f:
        resp_dict = json.load(f)

    with patch.object(
            wmc.delayed_requester,
            'get_response_json',
            return_value=resp_dict
    ) as mock_response_json:
        actual_result, actual_continue = wmc._get_image_batch(
            '2019-01-01', '2019-01-02', retries=2
        )

    expect_result = resp_dict
    expect_continue = {}

    mock_response_json.assert_called_once()
    assert actual_continue == expect_continue
    assert actual_result == expect_result


def test_merge_response_jsons():
    with open(
            os.path.join(RESOURCES, 'continuation', 'wmc_pretty1.json')
    ) as f:
        left_response = json.load(f)
    with open(
            os.path.join(RESOURCES, 'continuation', 'wmc_pretty2.json')
    ) as f:
        right_response = json.load(f)
    with open(
            os.path.join(RESOURCES, 'continuation', 'wmc_pretty1plus2.json')
    ) as f:
        expect_merged_response = json.load(f)

    actual_merged_response = wmc._merge_response_jsons(
        left_response,
        right_response,
    )
    assert actual_merged_response == expect_merged_response


def test_merge_image_pages_left_only_with_gu():
    with open(
            os.path.join(RESOURCES, 'continuation', 'page_44672185_left.json')
    ) as f:
        left_page = json.load(f)
    with open(
            os.path.join(RESOURCES, 'continuation', 'page_44672185_right.json')
    ) as f:
        right_page = json.load(f)
    actual_merged_page = wmc._merge_image_pages(left_page, right_page)
    assert actual_merged_page == left_page


def test_merge_image_pages_left_only_with_gu_backwards():
    with open(
            os.path.join(RESOURCES, 'continuation', 'page_44672185_left.json')
    ) as f:
        left_page = json.load(f)
    with open(
            os.path.join(RESOURCES, 'continuation', 'page_44672185_right.json')
    ) as f:
        right_page = json.load(f)
    actual_merged_page = wmc._merge_image_pages(right_page, left_page)
    assert actual_merged_page == left_page


def test_merge_image_pages_neither_have_gu():
    with open(
            os.path.join(RESOURCES, 'continuation', 'page_44672210_left.json')
    ) as f:
        left_page = json.load(f)
    with open(
            os.path.join(RESOURCES, 'continuation', 'page_44672210_right.json')
    ) as f:
        right_page = json.load(f)
    actual_merged_page = wmc._merge_image_pages(left_page, right_page)
    assert actual_merged_page == left_page


def test_merge_image_pages_neigher_have_gu_backwards():
    with open(
            os.path.join(RESOURCES, 'continuation', 'page_44672210_left.json')
    ) as f:
        left_page = json.load(f)
    with open(
            os.path.join(RESOURCES, 'continuation', 'page_44672210_right.json')
    ) as f:
        right_page = json.load(f)
    actual_merged_page = wmc._merge_image_pages(right_page, left_page)
    assert actual_merged_page == left_page


def test_merge_image_pages_both_have_gu():
    with open(
            os.path.join(RESOURCES, 'continuation', 'page_44672212_left.json')
    ) as f:
        left_page = json.load(f)
    with open(
            os.path.join(RESOURCES, 'continuation', 'page_44672212_right.json')
    ) as f:
        right_page = json.load(f)
    with open(
            os.path.join(
                RESOURCES,
                'continuation',
                'page_44672212_merged.json'
            )
    ) as f:
        expect_merged_page = json.load(f)
    actual_merged_page = wmc._merge_image_pages(left_page, right_page)
    assert actual_merged_page == expect_merged_page


def test_extract_title_gets_cleaned_title():
    image_info = {'extmetadata': {'ObjectName': {'value': 'File:filename.jpg'}}}
    actual_title = wmc._extract_title(image_info)
    expected_title = 'filename'
    assert actual_title == expected_title

    image_info['title'] = 'filename.jpeg'
    actual_title = wmc._extract_title(image_info)
    expected_title = 'filename'
    assert actual_title == expected_title


def test_process_image_data_handles_example_dict():
    with open(os.path.join(RESOURCES, 'image_data_example.json')) as f:
        image_data = json.load(f)

    with patch.object(
            wmc.image_store,
            'add_item',
            return_value=1
    ) as mock_add:
        wmc._process_image_data(image_data)

    mock_add.assert_called_once_with(
        foreign_landing_url=(
            'https://commons.wikimedia.org/w/index.php?curid=81754323'),
        image_url=(
            'https://upload.wikimedia.org/wikipedia/commons/2/25/20120925_'
            'PlozevetBretagne_LoneTree_DSC07971_PtrQs.jpg'),
        license_url='https://creativecommons.org/licenses/by-sa/4.0',
        foreign_identifier=81754323,
        width=5514,
        height=3102,
        creator='PtrQs',
        creator_url='https://commons.wikimedia.org/wiki/User:PtrQs',
        title='20120925 PlozevetBretagne LoneTree DSC07971 PtrQs',
        meta_data={'description': 'SONY DSC', 'global_usage_count': 0,
                    'last_modified_at_source': '2019-09-01 00:38:47',
                    'date_originally_created': '2012-09-25 16:23:02',
                    'categories': [
                        'Coasts of Ploz\u00e9vet', 'No QIC by usr:PtrQs',
                        ('Photographs taken with Minolta AF Zoom '
                            '28-70mm F2.8 G'),
                        'Self-published work', 'Taken with Sony DSLR-A900',
                        'Trees in Finist\u00e8re']}
    )


def test_process_image_data_throws_out_invalid_mediatype(monkeypatch):
    image_data = {'mediatype': 'INVALID'}

    def mock_check_mediatype(image_info):
        return False

    monkeypatch.setattr(wmc, '_check_mediatype', mock_check_mediatype)
    with patch.object(
            wmc.image_store,
            'add_item',
            return_value=1
    ) as mock_add:
        wmc._process_image_data(image_data)

    mock_add.assert_not_called()


def test_get_image_info_dict():
    with open(os.path.join(RESOURCES, 'image_data_example.json')) as f:
        image_data = json.load(f)

    with open(
            os.path.join(RESOURCES, 'image_info_from_example_data.json')
    ) as f:
        expect_image_info = json.load(f)

    actual_image_info = wmc._get_image_info_dict(image_data)

    assert actual_image_info == expect_image_info


def test_check_mediatype_with_valid_image_info():
    with open(
            os.path.join(RESOURCES, 'image_info_from_example_data.json')
    ) as f:
        image_info = json.load(f)

    valid_mediatype = wmc._check_mediatype(image_info)
    assert valid_mediatype is True


def test_check_mediatype_with_invalid_mediatype_in_image_info():
    with open(
            os.path.join(RESOURCES, 'image_info_from_example_data.json')
    ) as f:
        image_info = json.load(f)

    image_info.update(mediatype='INVALIDTYPE')

    valid_mediatype = wmc._check_mediatype(image_info)
    assert valid_mediatype is False


def test_extract_creator_info_handles_plaintext():
    with open(os.path.join(RESOURCES, 'image_info_artist_string.json')) as f:
        image_info = json.load(f)
    actual_creator, actual_creator_url = wmc._extract_creator_info(image_info)
    expect_creator = 'Artist Name'
    expect_creator_url = None
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_extract_creator_info_handles_well_formed_link():
    with open(os.path.join(RESOURCES, 'image_info_artist_link.json')) as f:
        image_info = json.load(f)
    actual_creator, actual_creator_url = wmc._extract_creator_info(image_info)
    expect_creator = 'link text'
    expect_creator_url = 'https://test.com/linkspot'
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_extract_creator_info_handles_div_with_no_link():
    with open(os.path.join(RESOURCES, 'image_info_artist_div.json')) as f:
        image_info = json.load(f)
    actual_creator, actual_creator_url = wmc._extract_creator_info(image_info)
    expect_creator = 'Jona Lendering'
    expect_creator_url = None
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_extract_creator_info_handles_internal_wc_link():
    with open(
            os.path.join(RESOURCES, 'image_info_artist_internal_link.json')
    ) as f:
        image_info = json.load(f)
    actual_creator, actual_creator_url = wmc._extract_creator_info(image_info)
    expect_creator = 'NotaRealUser'
    expect_creator_url = (
        'https://commons.wikimedia.org/w/index.php?title=User:NotaRealUser&'
        'action=edit&redlink=1')
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_extract_creator_info_handles_link_as_partial_text():
    with open(
            os.path.join(RESOURCES, 'image_info_artist_partial_link.json')
    ) as f:
        image_info = json.load(f)
    actual_creator, actual_creator_url = wmc._extract_creator_info(image_info)
    expect_creator = 'Jeff & Brian from Eastbourne'
    expect_creator_url = 'https://www.flickr.com/people/16707908@N07'
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_get_license_url_finds_license_url():
    with open(
            os.path.join(RESOURCES, 'image_info_from_example_data.json')
    ) as f:
        image_info = json.load(f)

    expect_license_url = 'https://creativecommons.org/licenses/by-sa/4.0'
    actual_license_url = wmc._get_license_url(image_info)
    assert actual_license_url == expect_license_url


def test_get_license_url_handles_missing_license_url():
    with open(
            os.path.join(RESOURCES, 'image_info_artist_partial_link.json')
    ) as f:
        image_info = json.load(f)
    expect_license_url = None
    actual_license_url = wmc._get_license_url(image_info)
    assert actual_license_url == expect_license_url


def test_get_license_url_handles_cc0_license():
    with open(
            os.path.join(RESOURCES, 'image_info_cc0.json')
    ) as f:
        image_info = json.load(f)
    expect_license_url = 'https://creativecommons.org/publicdomain/zero/1.0/'
    actual_license_url = wmc._get_license_url(image_info)
    assert actual_license_url == expect_license_url


def test_create_meta_data_scrapes_text_from_html_description():
    with open(
            os.path.join(RESOURCES, 'image_data_html_description.json')
    ) as f:
        image_data = json.load(f)
    expect_description = (
        'Identificatie Titel(s):  Allegorie op kunstenaar Francesco Mazzoli, '
        'bekend als Parmigianino')
    actual_description = wmc._create_meta_data_dict(image_data)['description']
    assert actual_description == expect_description


def test_create_meta_data_tallies_global_usage_count():
    with open(
            os.path.join(
                RESOURCES,
                'continuation',
                'page_44672185_left.json')
    ) as f:
        image_data = json.load(f)
    actual_gu = wmc._create_meta_data_dict(image_data)['global_usage_count']
    expect_gu = 3
    assert actual_gu == expect_gu


def test_create_meta_data_tallies_zero_global_usage_count():
    with open(
            os.path.join(
                RESOURCES,
                'continuation',
                'page_44672185_right.json')
    ) as f:
        image_data = json.load(f)
    actual_gu = wmc._create_meta_data_dict(image_data)['global_usage_count']
    expect_gu = 0
    assert actual_gu == expect_gu
