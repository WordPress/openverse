import logging

import pytest

from common import urls
from common.licenses import LicenseInfo
from common.storage import image


logger = logging.getLogger(__name__)


PD_LICENSE_INFO = LicenseInfo(
    "zero", "1.0", "https://creativecommons.org/publicdomain/zero/1.0/", None
)
BY_LICENSE_INFO = LicenseInfo(
    "by", "4.0", "https://creativecommons.org/licenses/by/4.0/", None
)


@pytest.fixture
def setup_env(monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", "/tmp")


def test_ImageStore_add_item_adds_realistic_image_to_buffer(setup_env):
    image_store = image.ImageStore(provider="testing_provider")
    image_store.add_item(
        foreign_identifier="01",
        foreign_landing_url="https://images.org/image01",
        url="https://images.org/image01.jpg",
        license_info=PD_LICENSE_INFO,
    )
    assert len(image_store._media_buffer) == 1


def test_ImageStore_add_item_adds_multiple_images_to_buffer(
    setup_env,
):
    image_store = image.ImageStore(provider="testing_provider")
    image_store.add_item(
        foreign_identifier="01",
        foreign_landing_url="https://images.org/image01",
        url="https://images.org/image01.jpg",
        license_info=PD_LICENSE_INFO,
    )
    image_store.add_item(
        foreign_identifier="02",
        foreign_landing_url="https://images.org/image02",
        url="https://images.org/image02.jpg",
        license_info=PD_LICENSE_INFO,
    )
    image_store.add_item(
        foreign_identifier="03",
        foreign_landing_url="https://images.org/image03",
        url="https://images.org/image03.jpg",
        license_info=PD_LICENSE_INFO,
    )
    image_store.add_item(
        foreign_identifier="04",
        foreign_landing_url="https://images.org/image04",
        url="https://images.org/image04.jpg",
        license_info=PD_LICENSE_INFO,
    )
    assert len(image_store._media_buffer) == 4


def test_ImageStore_get_image_places_given_args(
    monkeypatch,
):
    image_store = image.ImageStore(provider="testing_provider")
    args_dict = {
        "foreign_landing_url": "https://landing_page.com",
        "url": "https://imageurl.com",
        "license_info": BY_LICENSE_INFO,
        "foreign_identifier": "foreign_id",
        "thumbnail_url": "https://thumbnail.com",
        "filetype": "svg",
        "filesize": 1000,
        "width": 200,
        "height": 500,
        "creator": "tyler",
        "creator_url": "https://creatorurl.com",
        "title": "agreatpicture",
        "meta_data": {"description": "cat picture"},
        "raw_tags": [{"name": "tag1", "provider": "testing"}],
        "category": "photograph",
        "watermarked": "f",
        "source": "testing_source",
        "ingestion_type": "provider_api",
    }

    def mock_get_source(source, provider):
        return source

    monkeypatch.setattr(image_store, "_get_source", mock_get_source)

    def mock_enrich_tags(tags):
        return tags

    monkeypatch.setattr(image_store, "_enrich_tags", mock_enrich_tags)

    actual_image = image_store._get_image(**args_dict)
    args_dict["tags"] = args_dict.pop("raw_tags")
    args_dict["provider"] = "testing_provider"
    args_dict["filesize"] = 1000
    args_dict["license_"] = args_dict.get("license_info").license
    args_dict["license_version"] = args_dict.pop("license_info").version

    assert actual_image == image.Image(**args_dict)


@pytest.fixture
def default_image_args(
    setup_env,
):
    return dict(
        foreign_identifier="01",
        foreign_landing_url="https://image.org",
        url="https://image.org",
        thumbnail_url=None,
        filetype=None,
        width=None,
        height=None,
        filesize=None,
        license_="cc0",
        license_version="1.0",
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        tags=None,
        category=None,
        watermarked=None,
        provider=None,
        source=None,
        ingestion_type="provider_api",
    )


def test_create_tsv_row_non_none_if_req_fields(
    default_image_args,
    setup_env,
):
    image_store = image.ImageStore()
    test_image = image.Image(**default_image_args)
    actual_row = image_store._create_tsv_row(test_image)
    assert actual_row is not None


@pytest.mark.parametrize(
    "missing_field",
    [
        "foreign_landing_url",
        "license_",
        "license_version",
        "url",
    ],
)
def test_create_tsv_row_none_if_missing_required(
    default_image_args,
    setup_env,
    missing_field,
):
    image_store = image.ImageStore()
    image_args = default_image_args
    image_args[missing_field] = None
    test_image = image.Image(**image_args)
    expect_row = None
    actual_row = image_store._create_tsv_row(test_image)
    assert expect_row == actual_row


def test_create_tsv_row_handles_empty_dict_and_tags(
    default_image_args,
    setup_env,
):
    image_store = image.ImageStore()
    meta_data = {}
    tags = []
    image_args = default_image_args
    image_args["meta_data"] = meta_data
    image_args["tags"] = tags
    test_image = image.Image(**image_args)

    actual_row = image_store._create_tsv_row(test_image).split("\t")
    actual_meta_data, actual_tags = actual_row[12], actual_row[13]
    expect_meta_data, expect_tags = "\\N", "\\N"
    assert expect_meta_data == actual_meta_data
    assert expect_tags == actual_tags


def test_create_tsv_row_turns_empty_into_nullchar(
    default_image_args,
    setup_env,
):
    image_store = image.ImageStore()
    image_args = default_image_args
    image_args["ingestion_type"] = None
    test_image = image.Image(**image_args)

    actual_row = image_store._create_tsv_row(test_image).split("\t")
    assert (
        all(
            [
                actual_row[i] == "\\N"
                for i in [3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 16, 17]
            ]
        )
        is True
    )
    assert actual_row[-1] == "\\N\n"


def test_create_tsv_row_properly_places_entries(setup_env, monkeypatch):
    def mock_validate_url(url_string):
        return url_string

    image_store = image.ImageStore()
    monkeypatch.setattr(urls, "validate_url_string", mock_validate_url)

    req_args_dict = {
        "foreign_identifier": "foreign_id",
        "foreign_landing_url": "https://landing_page.com",
        "url": "http://imageurl.com",
        "license_": "testlicense",
        "license_version": "1.0",
    }
    args_dict = {
        "thumbnail_url": "http://thumbnail.com",
        "filetype": "png",
        "width": 200,
        "height": 500,
        "filesize": None,
        "creator": "tyler",
        "creator_url": "https://creatorurl.com",
        "title": "agreatpicture",
        "meta_data": {"description": "cat picture"},
        "tags": [{"name": "tag1", "provider": "testing"}],
        "category": "digitized_artwork",
        "watermarked": "f",
        "provider": "testing_provider",
        "source": "testing_source",
        "ingestion_type": "provider_api",
    }
    args_dict.update(req_args_dict)

    test_image = image.Image(**args_dict)
    actual_row = image_store._create_tsv_row(test_image)
    expect_row = (
        "\t".join(
            [
                "foreign_id",
                "https://landing_page.com",
                "http://imageurl.com",
                "http://thumbnail.com",
                "png",
                "\\N",
                "testlicense",
                "1.0",
                "tyler",
                "https://creatorurl.com",
                "agreatpicture",
                '{"description": "cat picture"}',
                '[{"name": "tag1", "provider": "testing"}]',
                "digitized_artwork",
                "f",
                "testing_provider",
                "testing_source",
                "provider_api",
                "200",
                "500",
            ]
        )
        + "\n"
    )
    assert expect_row == actual_row
