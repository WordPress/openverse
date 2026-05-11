import pytest

from common.licenses import LicenseInfo
from providers.provider_api_scripts.saint import SaintDataIngester


ingester = SaintDataIngester()


@pytest.mark.parametrize(
    "previous, expected_result",
    [
        pytest.param(
            None,
            {
                "page": 1,
                "pageSize": 100,
                "api_key": "",
            },
            id="default_response"
        ),
        pytest.param(
            {"page": 42, "pageSize": 100, "api_key": "dummy"},
            {"page": 43, "pageSize": 100, "api_key": "dummy"},
            id="basic_increment",
        ),
    ],
)
def test_get_next_query_params(previous, expected_result):
    actual_result = ingester.get_next_query_params(previous)
    assert actual_result == expected_result


@pytest.mark.parametrize(
    "response_json, expected",
    [
        pytest.param(
            {"data": [{"id": 1}, {"id": 2}]},
            [{"id": 1}, {"id": 2}],
            id="happy_path",
        ),
        pytest.param({}, None, id="empty_dict"),
        pytest.param(None, None, id="None"),
    ],
)
def test_get_batch_data(response_json, expected):
    actual = ingester.get_batch_data(response_json)
    assert actual == expected


@pytest.mark.parametrize(
    "record, expected_data",
    [
        pytest.param({}, None, id="empty_dict"),
        pytest.param(
            {
                "id": 123,
                "title": "A nice POI",
                "PrimaryImage": {
                    "url": "https://saint.tech/images/123.jpg",
                    "width": 800,
                    "height": 600,
                    "license": {
                        "url": "https://creativecommons.org/licenses/by/4.0/"
                    }
                }
            },
            {
                "foreign_landing_url": "https://saint.tech/poi/123",
                "url": "https://saint.tech/images/123.jpg",
                "license_info": LicenseInfo(
                    license="by",
                    version="4.0",
                    url="https://creativecommons.org/licenses/by/4.0/",
                    raw_url="https://creativecommons.org/licenses/by/4.0/",
                ),
                "foreign_identifier": "123",
                "title": "A nice POI",
                "creator": "IMG Saxony-Anhalt",
                "creator_url": "https://saint.tech/en",
                "width": 800,
                "height": 600,
            },
            id="happy_path",
        ),
        pytest.param(
            {
                "id": 123,
                "title": "No image POI"
            },
            None,
            id="no_image",
        ),
        pytest.param(
            {
                "id": 123,
                "PrimaryImage": {
                    "url": "https://saint.tech/images/123.jpg",
                }
            },
            None,
            id="no_license",
        ),
    ],
)
def test_get_record_data(record, expected_data):
    actual_data = ingester.get_record_data(record)
    assert actual_data == expected_data
