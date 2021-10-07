"""
MediaStore is an abstract class, so to test it we
use one of the inheriting classes, ImageStore
"""
import logging
from unittest.mock import patch

import pytest
from common.licenses.licenses import LicenseInfo, get_license_info
from storage import image


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.DEBUG
)

logger = logging.getLogger(__name__)

IMAGE_COLUMN_NAMES = [x.name for x in image.CURRENT_IMAGE_TSV_COLUMNS]

PD_LICENSE_INFO = LicenseInfo(
    "zero", "1.0", "https://creativecommons.org/publicdomain/zero/1.0/", None
)
BY_LICENSE_INFO = LicenseInfo(
    "by", "4.0", "https://creativecommons.org/licenses/by/4.0/", None
)


@pytest.fixture
def setup_env(monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", "/tmp")


def test_MediaStore_uses_OUTPUT_DIR_variable(
    monkeypatch,
):
    testing_output_dir = "/my_output_dir"
    monkeypatch.setenv("OUTPUT_DIR", testing_output_dir)
    image_store = image.ImageStore()
    assert testing_output_dir in image_store._OUTPUT_PATH


def test_MediaStore_falls_back_to_tmp_output_dir_variable(
    monkeypatch,
    setup_env,
):
    monkeypatch.delenv("OUTPUT_DIR")
    image_store = image.ImageStore()
    assert "/tmp" in image_store._OUTPUT_PATH


def test_MediaStore_includes_provider_in_output_file_string():
    image_store = image.ImageStore("test_provider")
    assert type(image_store._OUTPUT_PATH) == str
    assert "test_provider" in image_store._OUTPUT_PATH


def test_MediaStore_includes_media_type_in_output_file_string():
    image_store = image.ImageStore("test_provider")
    assert type(image_store._OUTPUT_PATH) == str
    assert "image" in image_store._OUTPUT_PATH


def test_MediaStore_add_item_flushes_buffer(tmpdir):
    output_file = "testing.tsv"
    tmp_directory = tmpdir
    output_dir = str(tmp_directory)
    tmp_file = tmp_directory.join(output_file)
    tmp_path_full = str(tmp_file)

    image_store = image.ImageStore(
        provider="testing_provider",
        output_file=output_file,
        output_dir=output_dir,
        buffer_length=3,
    )
    image_store.add_item(
        foreign_identifier="01",
        foreign_landing_url="https://images.org/image01",
        image_url="https://images.org/image01.jpg",
        license_info=PD_LICENSE_INFO,
    )
    image_store.add_item(
        foreign_identifier="02",
        foreign_landing_url="https://images.org/image02",
        image_url="https://images.org/image02.jpg",
        license_info=PD_LICENSE_INFO,
    )
    image_store.add_item(
        foreign_identifier="03",
        foreign_landing_url="https://images.org/image03",
        image_url="https://images.org/image03.jpg",
        license_info=PD_LICENSE_INFO,
    )
    image_store.add_item(
        foreign_identifier="04",
        foreign_landing_url="https://images.org/image04",
        image_url="https://images.org/image04.jpg",
        license_info=PD_LICENSE_INFO,
    )
    assert len(image_store._media_buffer) == 1
    with open(tmp_path_full) as f:
        lines = f.read().split("\n")
    assert len(lines) == 4  # recall the last '\n' will create an empty line.


def test_MediaStore_commit_writes_nothing_if_no_lines_in_buffer():
    image_store = image.ImageStore(output_dir="/path/does/not/exist")
    image_store.commit()


def test_MediaStore_produces_correct_total_images():
    image_store = image.ImageStore(provider="testing_provider")
    image_store.add_item(
        foreign_identifier="01",
        foreign_landing_url="https://images.org/image01",
        image_url="https://images.org/image01.jpg",
        license_info=PD_LICENSE_INFO,
    )
    image_store.add_item(
        foreign_identifier="02",
        foreign_landing_url="https://images.org/image02",
        image_url="https://images.org/image02.jpg",
        license_info=PD_LICENSE_INFO,
    )
    image_store.add_item(
        foreign_identifier="03",
        foreign_landing_url="https://images.org/image03",
        image_url="https://images.org/image03.jpg",
        license_info=PD_LICENSE_INFO,
    )
    assert image_store.total_items == 3


def test_MediaStore_clean_media_metadata_does_not_change_required_media_arguments(
    monkeypatch,
):
    image_url = "test_url"
    foreign_landing_url = "foreign_landing_url"
    image_store = image.ImageStore()
    image_data = {
        "license_info": BY_LICENSE_INFO,
        "foreign_landing_url": foreign_landing_url,
        "image_url": image_url,
        "thumbnail_url": None,
        "foreign_identifier": None,
    }
    cleaned_data = image_store.clean_media_metadata(**image_data)

    assert cleaned_data["image_url"] == image_url
    assert cleaned_data["foreign_landing_url"] == foreign_landing_url


def test_MediaStore_clean_media_metadata_adds_provider(
    monkeypatch,
):
    provider = "test_provider"
    image_store = image.ImageStore(provider=provider)
    image_data = {
        "license_info": BY_LICENSE_INFO,
        "foreign_landing_url": None,
        "image_url": None,
    }
    cleaned_data = image_store.clean_media_metadata(**image_data)

    assert cleaned_data["provider"] == provider


def test_MediaStore_clean_media_metadata_removes_license_urls(
    monkeypatch,
):
    image_store = image.ImageStore()
    image_data = {
        "license_info": BY_LICENSE_INFO,
        "foreign_landing_url": None,
        "image_url": None,
        "thumbnail_url": None,
        "foreign_identifier": None,
    }
    cleaned_data = image_store.clean_media_metadata(**image_data)

    assert "license_url" not in cleaned_data
    assert "raw_license_url" not in cleaned_data


def test_MediaStore_clean_media_metadata_replaces_license_url_with_license_info(
    monkeypatch,
):
    image_store = image.ImageStore()
    image_data = {
        "license_info": BY_LICENSE_INFO,
    }
    cleaned_data = image_store.clean_media_metadata(**image_data)

    expected_license = "by"
    expected_version = "4.0"
    assert cleaned_data["license_"] == expected_license
    assert cleaned_data["license_version"] == expected_version
    assert "license_url" not in cleaned_data


def test_MediaStore_clean_media_metadata_adds_license_urls_to_meta_data(
    monkeypatch,
):
    raw_license_url = "raw_license"
    license_url = "https://creativecommons.org/licenses/by-nc-nd/4.0/"
    image_store = image.ImageStore()
    image_data = {
        "license_info": LicenseInfo(
            "by-nc-nd",
            "4.0",
            license_url,
            raw_license_url,
        ),
        "foreign_landing_url": None,
        "image_url": None,
        "thumbnail_url": None,
        "foreign_identifier": None,
        "ingestion_type": "provider_api",
    }
    cleaned_data = image_store.clean_media_metadata(**image_data)

    assert cleaned_data["meta_data"]["license_url"] == license_url
    assert cleaned_data["meta_data"]["raw_license_url"] == raw_license_url


def test_MediaStore_get_image_gets_source(
    monkeypatch,
):
    image_store = image.ImageStore()

    actual_image = image_store._get_image(
        license_info=BY_LICENSE_INFO,
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        filetype=None,
        filesize=None,
        foreign_identifier=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=None,
        category=None,
        watermarked=None,
        source="diff_source",
        ingestion_type=None,
    )
    assert actual_image.source == "diff_source"


def test_MediaStore_sets_source_to_provider_if_source_is_none(
    monkeypatch,
):
    image_store = image.ImageStore(provider="test_provider")

    actual_image = image_store._get_image(
        license_info=BY_LICENSE_INFO,
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        filetype=None,
        filesize=1000,
        foreign_identifier=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=None,
        category=None,
        watermarked=None,
        source=None,
        ingestion_type=None,
    )
    assert actual_image.source == "test_provider"


def test_MediaStore_add_image_replaces_non_dict_meta_data_with_no_license_url():
    image_store = image.ImageStore()

    def item_saver(arg):
        pass

    with patch.object(image_store, "save_item", side_effect=item_saver) as mock_save:
        image_store.add_item(
            license_info=BY_LICENSE_INFO,
            foreign_landing_url="",
            image_url="",
            thumbnail_url=None,
            foreign_identifier=None,
            width=None,
            height=None,
            creator=None,
            creator_url=None,
            title=None,
            meta_data="notadict",
            raw_tags=None,
            watermarked=None,
            source=None,
            ingestion_type=None,
        )
    actual_image = mock_save.call_args[0][0]
    assert actual_image.meta_data == {
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "raw_license_url": None,
    }


def test_MediaStore_add_item_creates_meta_data_with_valid_license_url(
    monkeypatch, setup_env
):
    image_store = image.ImageStore()

    license_url = "https://my.license.url"
    valid_license_url = "https://creativecommons.org/licenses/by/4.0/"

    def item_saver(arg):
        pass

    with patch.object(image_store, "save_item", side_effect=item_saver) as mock_save:
        image_store.add_item(
            license_info=LicenseInfo("by", "4.0", valid_license_url, license_url),
            foreign_landing_url="",
            image_url="",
            thumbnail_url=None,
            foreign_identifier=None,
            width=None,
            height=None,
            creator=None,
            creator_url=None,
            title=None,
            meta_data=None,
            raw_tags=None,
            watermarked=None,
            source=None,
            ingestion_type=None,
        )
        actual_image = mock_save.call_args[0][0]

        assert actual_image.meta_data == {
            "license_url": valid_license_url,
            "raw_license_url": license_url,
        }


def test_MediaStore_add_item_adds_valid_license_url_to_dict_meta_data(
    monkeypatch, setup_env
):
    image_store = image.ImageStore()

    license_url = "https://my.license.url"
    valid_license_url = "https://creativecommons.org/licenses/by/4.0/"

    def item_saver(arg):
        pass

    with patch.object(image_store, "save_item", side_effect=item_saver) as mock_save:
        image_store.add_item(
            license_info=LicenseInfo("by", "4.0", valid_license_url, license_url),
            foreign_landing_url="",
            image_url="",
            thumbnail_url=None,
            foreign_identifier=None,
            width=None,
            height=None,
            creator=None,
            creator_url=None,
            title=None,
            meta_data={"key1": "val1"},
            raw_tags=None,
            watermarked=None,
            source=None,
            ingestion_type=None,
        )
        actual_image = mock_save.call_args[0][0]

        assert actual_image.meta_data == {
            "key1": "val1",
            "license_url": valid_license_url,
            "raw_license_url": license_url,
        }


def test_ImageStore_add_item_fixes_invalid_license_url():
    image_store = image.ImageStore()

    original_url = "https://license/url"
    updated_url = "https://creativecommons.org/licenses/by-nc-sa/2.0/"

    def item_saver(arg):
        pass

    with patch.object(image_store, "save_item", side_effect=item_saver) as mock_save:
        image_store.add_item(
            license_info=LicenseInfo("by-nc-sa", "2.0", updated_url, original_url),
            foreign_landing_url="",
            image_url="",
            meta_data={},
        )
    actual_image = mock_save.call_args[0][0]

    assert actual_image.meta_data == {
        "license_url": updated_url,
        "raw_license_url": original_url,
    }


def test_MediaStore_get_image_enriches_singleton_tags():
    image_store = image.ImageStore("test_provider")

    actual_image = image_store._get_image(
        license_info=get_license_info(
            license_="by-sa",
            license_version="4.0",
            license_url="https://license/url",
        ),
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        filetype=None,
        filesize=None,
        foreign_identifier=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=["lone"],
        category=None,
        watermarked=None,
        source=None,
        ingestion_type=None,
    )

    assert actual_image.tags == [{"name": "lone", "provider": "test_provider"}]


def test_MediaStore_get_image_tag_blacklist():
    raw_tags = [
        "cc0",
        "valid",
        "garbage:=metacrap",
        "uploaded:by=flickrmobile",
        {"name": "uploaded:by=instagram", "provider": "test_provider"},
    ]

    image_store = image.ImageStore("test_provider")

    actual_image = image_store._get_image(
        license_info=get_license_info(
            license_="by",
            license_version="4.0",
        ),
        foreign_landing_url=None,
        image_url=None,
        meta_data=None,
        raw_tags=raw_tags,
        category=None,
        foreign_identifier=None,
        thumbnail_url=None,
        filetype=None,
        filesize=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        watermarked=None,
        ingestion_type=None,
    )

    assert actual_image.tags == [{"name": "valid", "provider": "test_provider"}]


def test_MediaStore_get_image_enriches_multiple_tags():
    image_store = image.ImageStore("test_provider")
    actual_image = image_store._get_image(
        license_info=get_license_info(
            license_url="https://license/url",
            license_="by",
            license_version="4.0",
        ),
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        filetype=None,
        filesize=None,
        foreign_identifier=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=["tagone", "tag2", "tag3"],
        category=None,
        watermarked=None,
        source=None,
        ingestion_type=None,
    )

    assert actual_image.tags == [
        {"name": "tagone", "provider": "test_provider"},
        {"name": "tag2", "provider": "test_provider"},
        {"name": "tag3", "provider": "test_provider"},
    ]


def test_MediaStore_get_image_leaves_preenriched_tags(setup_env):
    image_store = image.ImageStore("test_provider")
    tags = [
        {"name": "tagone", "provider": "test_provider"},
        {"name": "tag2", "provider": "test_provider"},
        {"name": "tag3", "provider": "test_provider"},
    ]

    actual_image = image_store._get_image(
        license_info=get_license_info(
            license_url="https://license/url",
            license_="by",
            license_version="4.0",
        ),
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        filetype=None,
        filesize=None,
        foreign_identifier=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=tags,
        category=None,
        watermarked=None,
        source=None,
        ingestion_type=None,
    )

    assert actual_image.tags == tags


def test_MediaStore_get_image_nones_nonlist_tags():
    image_store = image.ImageStore("test_provider")
    tags = "notalist"

    actual_image = image_store._get_image(
        license_info=get_license_info(
            license_url="https://license/url",
            license_="by",
            license_version="4.0",
        ),
        foreign_landing_url=None,
        image_url=None,
        thumbnail_url=None,
        filetype=None,
        filesize=None,
        foreign_identifier=None,
        width=None,
        height=None,
        creator=None,
        creator_url=None,
        title=None,
        meta_data=None,
        raw_tags=tags,
        category=None,
        watermarked=None,
        source=None,
        ingestion_type=None,
    )

    assert actual_image.tags is None
