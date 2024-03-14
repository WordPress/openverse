import json
from pathlib import Path
from unittest.mock import patch

from common.licenses import get_license_info
from providers.provider_api_scripts.justtakeitfree import JusttakeitfreeDataIngester


RESOURCES = Path(__file__).parent / "resources/justtakeitfree"

jtif = JusttakeitfreeDataIngester()


class FileSizeHeadResponse:
    def __init__(self, size):
        self.headers = {"Content-Length": size}


def test_get_next_query_params_default_response():
    actual_result = jtif.get_next_query_params(None)
    actual_result.pop("key", None)
    expected_result = {
        "page": 1,
    }
    assert actual_result == expected_result


def test_get_next_query_params_updates_parameters():
    previous_query_params = {
        "page": 1,
    }
    actual_result = jtif.get_next_query_params(previous_query_params)
    actual_result.pop("key", None)

    expected_result = {
        "page": 2,
    }
    assert actual_result == expected_result


def test_get_record_data():
    with open(RESOURCES / "single_item.json") as f:
        resource_json = json.load(f)

    with patch.object(jtif.delayed_requester, "head") as head_patch:
        # Returns None when 404
        head_patch.return_value = FileSizeHeadResponse(100)
        actual_data = jtif.get_record_data(resource_json)

    expected_data = {
        "foreign_landing_url": "https://justtakeitfree.com/photo/2/",
        "url": "https://justtakeitfree.com/photos/2.jpg",
        "foreign_identifier": "2",
        "creator": "Justtakeitfree Free Photos",
        "creator_url": "https://justtakeitfree.com",
        "license_info": get_license_info(
            "https://creativecommons.org/licenses/by/4.0/"
        ),
        "raw_tags": {"Baturyn fortress", "Baturyn citadel", "cossack fortress"},
        "thumbnail_url": "https://justtakeitfree.com/photos/2_800.jpg",
        "filesize": 100,
    }

    assert actual_data == expected_data
