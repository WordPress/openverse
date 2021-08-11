import json
import logging
import os
from unittest.mock import patch

import jamendo
from common.licenses.licenses import LicenseInfo

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'tests/resources/jamendo'
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG,
)


def test_get_image_pages_returns_correctly_with_none_json():
    expect_result = None
    with patch.object(
            jamendo.delayed_requester,
            'get_response_json',
            return_value=None
    ):
        actual_result = jamendo._get_batch_json()
    assert actual_result == expect_result


def test_get_image_pages_returns_correctly_with_no_results():
    expect_result = None
    with patch.object(
            jamendo.delayed_requester,
            'get_response_json',
            return_value={}
    ):
        actual_result = jamendo._get_batch_json()
    assert actual_result == expect_result


def test_get_query_params_adds_offset():
    actual_qp = jamendo._get_query_params(
        offset=200
    )
    assert actual_qp['offset'] == 200


def test_get_query_params_leaves_other_keys():
    actual_qp = jamendo._get_query_params(
        offset=200, default_query_params={'test': 'value'}
    )
    assert actual_qp['test'] == 'value'
    assert len(actual_qp.keys()) == 2


def test_get_items():
    with open(os.path.join(RESOURCES, 'page1.json')) as f:
        first_response = json.load(f)
    with patch.object(
            jamendo,
            '_get_batch_json',
            side_effect=[first_response, []]
    ):
        expected_image_count = 4
        actual_image_count = jamendo._get_items()
        assert expected_image_count == actual_image_count


def test_process_item_batch_handles_example_batch():
    with open(os.path.join(RESOURCES, 'audio_data_example.json')) as f:
        items_batch = [json.load(f)]
    with patch.object(
            jamendo.audio_store,
            'add_item',
            return_value=1
    ) as mock_add:
        jamendo._process_item_batch(items_batch)
        mock_add.assert_called_once()
        _, actual_call_args = mock_add.call_args_list[0]
        expected_call_args = {
            'audio_set': 'Opera I',
            'audio_url': 'https://mp3d.jamendo.com/download/track/732/mp32/',
            'category': 'music',
            'creator': 'Haeresis',
            'creator_url': 'https://www.jamendo.com/artist/92/haeresis',
            'duration': 144000,
            'foreign_identifier': '732',
            'foreign_landing_url': 'https://www.jamendo.com/track/732',
            'genres': [],
            'license_info': LicenseInfo(
                license='by-nc',
                version='2.0',
                url='https://creativecommons.org/licenses/by-nc/2.0/',
                raw_url='http://creativecommons.org/licenses/by-nc/2.0/'
            ),
            'meta_data': {'downloads': 0,
                          'listens': 5616,
                          'playlists': 0,
                          'release_date': '2005-04-12'},
            'raw_tags': ['instrumental', 'speed_medium'],
            'set_position': 6,
            'set_thumbnail': 'https://usercontent.jamendo.com?type=album&id=119&width=200&trackid=732',
            'set_url': 'https://www.jamendo.com/album/119/opera-i',
            'thumbnail_url': 'https://usercontent.jamendo.com?type=album&id=119&width=200&trackid=732',
            'title': 'Thoughtful'
        }
        assert actual_call_args == expected_call_args


def test_extract_audio_data_returns_none_when_media_data_none():
    actual_image_info = jamendo._extract_audio_data(None)
    expected_image_info = None
    assert actual_image_info is expected_image_info


def test_extract_audio_data_returns_none_when_no_foreign_id():
    with open(os.path.join(RESOURCES, 'audio_data_example.json')) as f:
        audio_data = json.load(f)
        audio_data.pop('shareurl', None)
    actual_image_info = jamendo._extract_audio_data(audio_data)
    expected_image_info = None
    assert actual_image_info is expected_image_info


def test_extract_audio_data_falls_back_on_audio_url_when_download_not_available():
    """
    We use the URL from `audiodownload` only if download is allowed, and there is
    download URL. Otherwise, we try to get URL from `audio_url`
    """
    AUDIO_D_URL = 'https://mp3d.jamendo.com/download/track/732/mp32/'
    AUDIO_URL = 'https://mp3d.jamendo.com/?trackid=732&format=mp32&from=' \
                'WftSCtIfbfXP90c1jNqsfw%3D%3D%7CNzgGctbCMB1xAW8bJE5uEw%3D%3D'
    with open(os.path.join(RESOURCES, 'audio_data_example.json')) as f:
        audio_data = json.load(f)
    actual_image_info = jamendo._extract_audio_data(audio_data)['audio_url']
    expected_image_download_url = AUDIO_D_URL
    assert actual_image_info == expected_image_download_url

    audio_data['audiodownload_allowed'] = False
    actual_image_info = jamendo._extract_audio_data(audio_data)['audio_url']
    expected_image_download_url = AUDIO_URL
    assert actual_image_info == expected_image_download_url

    audio_data['audiodownload_allowed'] = True
    audio_data.pop('audiodownload', None)
    actual_image_info = jamendo._extract_audio_data(audio_data)['audio_url']
    expected_image_download_url = AUDIO_URL
    assert actual_image_info == expected_image_download_url


def test_extract_audio_data_returns_none_when_no_audio_url():
    with open(os.path.join(RESOURCES, 'audio_data_example.json')) as f:
        audio_data = json.load(f)
        audio_data.pop('audio', None)
        audio_data['audiodownload_allowed'] = False
    actual_audio_info = jamendo._extract_audio_data(audio_data)
    assert actual_audio_info is None


def test_extract_audio_data_returns_none_when_no_license():
    with open(os.path.join(RESOURCES, 'audio_data_example.json')) as f:
        audio_data = json.load(f)
        audio_data.pop('license_ccurl', None)
    actual_audio_info = jamendo._extract_audio_data(audio_data)
    assert actual_audio_info is None


def test_get_audio_set_info():
    with open(os.path.join(RESOURCES, 'audio_data_example.json')) as f:
        audio_data = json.load(f)
    actual_audio_set_info = jamendo._get_audio_set_info(audio_data)
    expected_audio_set_info = (
        'Opera I',
        6,
        'https://www.jamendo.com/album/119/opera-i',
        'https://usercontent.jamendo.com?type=album&id=119&width=200&trackid=732'
    )
    assert actual_audio_set_info == expected_audio_set_info


def test_get_creator_data():
    with open(os.path.join(RESOURCES, 'audio_data_example.json')) as f:
        audio_data = json.load(f)
    actual_creator, actual_creator_url = jamendo._get_creator_data(audio_data)
    expected_creator = 'Haeresis'
    expected_creator_url = 'https://www.jamendo.com/artist/92/haeresis'

    assert actual_creator == expected_creator
    assert actual_creator_url == expected_creator_url


def test_get_creator_data_handles_no_url():
    with open(os.path.join(RESOURCES, 'audio_data_example.json')) as f:
        audio_data = json.load(f)
    audio_data.pop('artist_idstr', None)
    expected_creator = 'Haeresis'

    actual_creator, actual_creator_url = jamendo._get_creator_data(audio_data)
    assert actual_creator == expected_creator
    assert actual_creator_url is None


def test_get_creator_data_returns_none_when_no_artist():
    with open(os.path.join(RESOURCES, 'audio_data_example.json')) as f:
        audio_data = json.load(f)
    audio_data.pop('artist_name', None)
    actual_creator, actual_creator_url = jamendo._get_creator_data(audio_data)

    assert actual_creator is None
    assert actual_creator_url is None


def test_extract_audio_data_handles_example_dict():
    with open(os.path.join(RESOURCES, 'audio_data_example.json')) as f:
        audio_data = json.load(f)

    actual_image_info = jamendo._extract_audio_data(audio_data)
    expected_image_info = {
        'audio_set': 'Opera I',
        'audio_url': 'https://mp3d.jamendo.com/download/track/732/mp32/',
        'category': 'music',
        'creator': 'Haeresis',
        'creator_url': 'https://www.jamendo.com/artist/92/haeresis',
        'duration': 144000,
        'foreign_identifier': '732',
        'foreign_landing_url': 'https://www.jamendo.com/track/732',
        'genres': [],
        'license_info': LicenseInfo(
            license='by-nc',
            version='2.0',
            url='https://creativecommons.org/licenses/by-nc/2.0/',
            raw_url='http://creativecommons.org/licenses/by-nc/2.0/'
        ),
        'meta_data': {'downloads': 0,
                      'listens': 5616,
                      'playlists': 0,
                      'release_date': '2005-04-12'},
        'raw_tags': ['instrumental', 'speed_medium'],
        'set_position': 6,
        'set_thumbnail': 'https://usercontent.jamendo.com?type=album&id=119&width=200&trackid=732',
        'set_url': 'https://www.jamendo.com/album/119/opera-i',
        'thumbnail_url': 'https://usercontent.jamendo.com?type=album&id=119&width=200&trackid=732',
        'title': 'Thoughtful'
    }
    assert actual_image_info == expected_image_info


def test_get_tags():
    item_data = {
        "musicinfo": {
            "vocalinstrumental": "vocal",
            "gender": "male",
            "speed": "medium",
            "tags": {
                "genres": [
                    "pop",
                    "rock"
                ],
                "instruments": [],
                "vartags": [
                    "engage"
                ]
            }
        }
    }
    expected_tags = ['vocal', 'male', 'speed_medium', 'engage']
    actual_tags = jamendo._get_tags(item_data)
    assert expected_tags == actual_tags
