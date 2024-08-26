from common.licenses import LicenseInfo
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester
from providers.provider_api_scripts.time_delineated_provider_data_ingester import (
    TimeDelineatedProviderDataIngester,
)


_license_info = (
    "cc0",
    "1.0",
    "https://creativecommons.org/publicdomain/zero/1.0/",
    None,
)
LICENSE_INFO = LicenseInfo(*_license_info)
AUDIO_PROVIDER = "mock_audio_provider"
IMAGE_PROVIDER = "mock_image_provider"
ENDPOINT = "http://mock-api/endpoint"
HEADERS = {"api_key": "mock_api_key"}
DEFAULT_QUERY_PARAMS = {"has_image": 1, "page": 1}

# Constants used for time delineated ingester
MAX_RECORDS = 10_000
DIVISION_THRESHOLD = 100_000
MIN_DIVISIONS = 12
MAX_DIVISIONS = 20


class MockProviderDataIngesterMixin:
    """
    A simple concrete ProviderDataIngester class for testing purposes.

    Excludes ``get_media_type`` to allow for testing implementations
    that do not require it (single media type providers).
    """

    providers = {"audio": AUDIO_PROVIDER, "image": IMAGE_PROVIDER}
    endpoint = ENDPOINT

    def get_next_query_params(self, prev_query_params):
        if prev_query_params is None:
            return DEFAULT_QUERY_PARAMS
        return {**prev_query_params, "page": prev_query_params["page"] + 1}

    def get_batch_data(self, response_json):
        if response_json:
            return response_json.get("data")
        return None

    def get_record_data(self, record):
        data = {
            "foreign_identifier": record["id"],
            "foreign_landing_url": record["foreign_landing_url"],
            "media_type": record["media_type"],
            "license_info": LICENSE_INFO,
            "url": record["url"],
        }
        return data


class MockProviderDataIngester(MockProviderDataIngesterMixin, ProviderDataIngester):
    def get_media_type(self, record):
        return record["media_type"]


class MockImageOnlyProviderDataIngester(
    MockProviderDataIngesterMixin, ProviderDataIngester
):
    providers = {"image": IMAGE_PROVIDER}


class MockAudioOnlyProviderDataIngester(
    MockProviderDataIngesterMixin, ProviderDataIngester
):
    providers = {"audio": AUDIO_PROVIDER}


class IncorrectlyConfiguredMockProviderDataIngester(
    MockProviderDataIngesterMixin, ProviderDataIngester
):
    """Used for testing default method implementations."""

    # Do not configure ``get_media_type`` to test the failure case
    # for the default implementation


class MockTimeDelineatedProviderDataIngester(
    MockProviderDataIngesterMixin, TimeDelineatedProviderDataIngester
):
    providers = {"image": IMAGE_PROVIDER}
    max_records = MAX_RECORDS
    division_threshold = DIVISION_THRESHOLD
    min_divisions = MIN_DIVISIONS
    max_divisions = MAX_DIVISIONS

    def get_next_query_params(self, prev_query_params):
        return DEFAULT_QUERY_PARAMS

    def get_record_count_from_response(self, response_json):
        if response_json:
            return response_json.get("count")
        return 0

    def get_timestamp_query_params(self, start, end, **kwargs):
        return {"start_ts": start, "end_ts": end}


# Expected result of calling `get_batch_data` with `response_success.json`
EXPECTED_BATCH_DATA = [
    {
        "id": 100,
        "media_type": "image",
        "title": "Title 100",
        "url": "https://openaccess-cdn.clevelandart.org/1916.586.a/1916.586.a_web.jpg",  # noqa: E501
        "foreign_landing_url": "https://clevelandart.org/art/1916.586.a",
    },
    {
        "id": 101,
        "media_type": "audio",
        "title": "Title 101",
        "url": "https://openaccess-cdn.clevelandart.org/1335.1917/1335.1917_web.jpg",  # noqa: E501
        "foreign_landing_url": "https://clevelandart.org/art/1335.1917",
    },
    {
        "id": 102,
        "media_type": "image",
        "title": "Title 102",
        "url": "https://openaccess-cdn.clevelandart.org/1915.534/1915.534_web.jpg",  # noqa: E501
        "foreign_landing_url": "https://clevelandart.org/art/1915.534",
    },
]

# Sample record data containing multiple records
MOCK_RECORD_DATA_LIST = [
    {
        "foreign_identifier": 101,
        "foreign_landing_url": "https://commons.wikimedia.org/w/index.php?curid=120786580",
        "media_type": "audio",
        "license_info": LICENSE_INFO,
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Nl-Javaanse_herten.ogg",  # noqa: E501
    },
    {
        "foreign_identifier": 100,
        "foreign_landing_url": "https://commons.wikimedia.org/w/index.php?curid=81754323",
        "media_type": "image",
        "license_info": LICENSE_INFO,
        "url": "https://upload.wikimedia.org/wikipedia/commons/2/25/20120925_PlozevetBretagne_LoneTree_DSC07971_PtrQs.jpg",  # noqa: E501
    },
]
