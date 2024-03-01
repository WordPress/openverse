"""
MediaStore is an abstract class, so to test it we
use one of the inheriting classes, ImageStore
"""

import logging
from unittest.mock import patch

import pytest

from common import urls
from common.licenses import LicenseInfo, get_license_info
from common.loader import provider_details as prov
from common.storage import image, media


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.DEBUG
)

logger = logging.getLogger(__name__)
# This avoids needing the internet for testing.
urls.tldextract.extract = urls.tldextract.TLDExtract(suffix_list_urls=None)

IMAGE_COLUMN_NAMES = [x.name for x in image.CURRENT_IMAGE_TSV_COLUMNS]

PD_LICENSE_INFO = LicenseInfo(
    "zero", "1.0", "https://creativecommons.org/publicdomain/zero/1.0/", None
)
BY_LICENSE_INFO = LicenseInfo(
    "by", "4.0", "https://creativecommons.org/licenses/by/4.0/", None
)

TEST_FOREIGN_LANDING_URL = "https://wordpress.org/openverese/image"
TEST_IMAGE_URL = "https://wordpress.org/openverese/image.jpg"

TEST_IMAGE_DICT = {
    "foreign_landing_url": None,
    "url": None,
    "thumbnail_url": None,
    "filetype": None,
    "filesize": None,
    "foreign_identifier": None,
    "width": None,
    "height": None,
    "creator": None,
    "creator_url": None,
    "title": None,
    "meta_data": None,
    "raw_tags": None,
    "category": None,
    "watermarked": None,
    "source": None,
    "ingestion_type": None,
}

INT_MAX_PARAMETERIZATION = pytest.mark.parametrize(
    "value, expected",
    [
        (None, None),
        (123, 123),
        (media.PG_INTEGER_MAXIMUM - 1, media.PG_INTEGER_MAXIMUM - 1),
        (media.PG_INTEGER_MAXIMUM, None),
    ],
)

TEST_REQUIRED_FIELDS = {
    "foreign_landing_url": TEST_FOREIGN_LANDING_URL,
    "foreign_identifier": "02",
    "url": TEST_IMAGE_URL,
    "license_info": BY_LICENSE_INFO,
}


@pytest.fixture
def setup_env(monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", "/tmp")


def test_MediaStore_uses_OUTPUT_DIR_variable(
    monkeypatch,
):
    testing_output_dir = "/my_output_dir"
    monkeypatch.setenv("OUTPUT_DIR", testing_output_dir)
    image_store = image.ImageStore()
    assert testing_output_dir in image_store.output_path


def test_MediaStore_falls_back_to_tmp_output_dir_variable(
    monkeypatch,
    setup_env,
):
    monkeypatch.delenv("OUTPUT_DIR")
    image_store = image.ImageStore()
    assert "/tmp" in image_store.output_path


def test_MediaStore_includes_provider_in_output_file_string():
    image_store = image.ImageStore("test_provider")
    assert isinstance(image_store.output_path, str)
    assert "test_provider" in image_store.output_path


def test_MediaStore_includes_media_type_in_output_file_string():
    image_store = image.ImageStore("test_provider")
    assert isinstance(image_store.output_path, str)
    assert "image" in image_store.output_path


def test_MediaStore_includes_tsvsuffix_if_provided():
    image_store = image.ImageStore("test_provider", tsv_suffix="foo")
    assert isinstance(image_store.output_path, str)
    assert image_store.output_path.endswith("_foo.tsv")


def test_MediaStore_add_item_flushes_buffer(tmpdir):
    image_store = image.ImageStore(
        provider="testing_provider",
        buffer_length=3,
    )
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
    assert len(image_store._media_buffer) == 1
    with open(image_store.output_path) as f:
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
    assert image_store.total_items == 3


def test_MediaStore_clean_media_metadata_does_not_change_required_media_arguments(
    monkeypatch,
):
    image_store = image.ImageStore()
    image_data = {
        **TEST_REQUIRED_FIELDS,
        "filetype": None,
        "thumbnail_url": None,
        "category": None,
    }
    cleaned_data = image_store.clean_media_metadata(**image_data)

    assert cleaned_data["url"] == TEST_IMAGE_URL
    assert cleaned_data["foreign_landing_url"] == TEST_FOREIGN_LANDING_URL


def test_MediaStore_clean_media_metadata_adds_provider(monkeypatch):
    provider = "test_provider"
    image_store = image.ImageStore(provider=provider)
    image_data = {
        **TEST_REQUIRED_FIELDS,
        "filetype": None,
        "category": None,
    }
    cleaned_data = image_store.clean_media_metadata(**image_data)

    assert cleaned_data["provider"] == provider


def test_MediaStore_clean_media_metadata_removes_license_urls(monkeypatch):
    image_store = image.ImageStore()
    image_data = {
        **TEST_REQUIRED_FIELDS,
        "thumbnail_url": None,
        "filetype": None,
        "category": None,
    }
    cleaned_data = image_store.clean_media_metadata(**image_data)

    assert "license_url" not in cleaned_data
    assert "raw_license_url" not in cleaned_data


def test_MediaStore_clean_media_metadata_replaces_license_url_with_license_info(
    monkeypatch,
):
    image_store = image.ImageStore()
    image_data = {
        **TEST_REQUIRED_FIELDS,
        "filetype": None,
        "category": None,
    }
    cleaned_data = image_store.clean_media_metadata(**image_data)

    expected_license = "by"
    expected_version = "4.0"
    assert cleaned_data["license_"] == expected_license
    assert cleaned_data["license_version"] == expected_version
    assert "license_url" not in cleaned_data


def test_MediaStore_clean_media_metadata_adds_default_provider_category(monkeypatch):
    image_store = image.ImageStore(provider=prov.CLEVELAND_DEFAULT_PROVIDER)
    image_data = {
        **TEST_REQUIRED_FIELDS,
        "filetype": None,
        "category": None,
    }
    cleaned_data = image_store.clean_media_metadata(**image_data)

    assert cleaned_data["category"] == prov.ImageCategory.DIGITIZED_ARTWORK


def test_MediaStore_clean_media_metadata_does_not_replace_category_with_default(
    monkeypatch,
):
    image_store = image.ImageStore(provider=prov.CLEVELAND_DEFAULT_PROVIDER)
    image_data = {
        **TEST_REQUIRED_FIELDS,
        "filetype": None,
        "category": prov.ImageCategory.PHOTOGRAPH,
    }
    cleaned_data = image_store.clean_media_metadata(**image_data)

    assert cleaned_data["category"] == prov.ImageCategory.PHOTOGRAPH


@pytest.mark.parametrize(
    "field", ("foreign_identifier", "foreign_landing_url", "url", "license_info")
)
def test_MediaStore_clean_media_metadata_raises_when_missing_required_field(
    field,
):
    image_store = image.ImageStore()
    image_data = {
        **TEST_REQUIRED_FIELDS,
        field: None,  # Override the test field with None
    }
    with pytest.raises(ValueError, match=f"Record missing required field: `{field}`"):
        image_store.clean_media_metadata(**image_data)


def test_MediaStore_clean_media_metadata_adds_license_urls_to_meta_data(monkeypatch):
    raw_license_url = "raw_license"
    license_url = "https://creativecommons.org/licenses/by-nc-nd/4.0/"
    image_store = image.ImageStore()
    image_data = {
        **TEST_REQUIRED_FIELDS,
        "license_info": LicenseInfo(
            "by-nc-nd",
            "4.0",
            license_url,
            raw_license_url,
        ),
        "filetype": None,
        "thumbnail_url": None,
        "ingestion_type": "provider_api",
        "category": None,
    }
    cleaned_data = image_store.clean_media_metadata(**image_data)

    assert cleaned_data["meta_data"]["license_url"] == license_url
    assert cleaned_data["meta_data"]["raw_license_url"] == raw_license_url


@pytest.mark.parametrize(
    "input_url, remove_slashes, expected",
    [
        ("https://www.example.com/", True, "https://www.example.com"),
        ("https://www.example.com", True, "https://www.example.com"),
        ("https://www.example.com/", False, "https://www.example.com/"),
        ("https://www.example.com", False, "https://www.example.com"),
    ],
)
def test_MediaStore_clean_media_strips_url_trailing_slashes(
    input_url, remove_slashes, expected
):
    image_store = image.ImageStore(strip_url_trailing_slashes=remove_slashes)
    test_data = {
        "foreign_landing_url": input_url,
        "url": input_url,
        "thumbnail_url": input_url,
        "creator_url": input_url,
    }
    image_data = TEST_IMAGE_DICT | TEST_REQUIRED_FIELDS | test_data
    cleaned_data = image_store.clean_media_metadata(**image_data)

    for key in test_data:
        assert cleaned_data[key] == expected


def test_MediaStore_get_image_gets_source(monkeypatch):
    image_store = image.ImageStore()

    actual_image = image_store._get_image(
        license_info=BY_LICENSE_INFO,
        foreign_landing_url=TEST_FOREIGN_LANDING_URL,
        url=TEST_IMAGE_URL,
        thumbnail_url=None,
        filetype=None,
        filesize=None,
        foreign_identifier="02",
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


def test_MediaStore_sets_source_to_provider_if_source_is_none(monkeypatch):
    image_store = image.ImageStore(provider="test_provider")

    actual_image = image_store._get_image(
        license_info=BY_LICENSE_INFO,
        foreign_landing_url=TEST_FOREIGN_LANDING_URL,
        url=TEST_IMAGE_URL,
        thumbnail_url=None,
        filetype=None,
        filesize=1000,
        foreign_identifier="02",
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
            foreign_landing_url=TEST_FOREIGN_LANDING_URL,
            url=TEST_IMAGE_URL,
            thumbnail_url=None,
            foreign_identifier="02",
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
            foreign_landing_url=TEST_FOREIGN_LANDING_URL,
            url=TEST_IMAGE_URL,
            thumbnail_url=None,
            foreign_identifier="02",
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
            foreign_landing_url=TEST_FOREIGN_LANDING_URL,
            url=TEST_IMAGE_URL,
            foreign_identifier="02",
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


def test_MediaStore_add_item_fixes_invalid_license_url():
    image_store = image.ImageStore()

    original_url = "https://license/url"
    updated_url = "https://creativecommons.org/licenses/by-nc-sa/2.0/"

    def item_saver(arg):
        pass

    with patch.object(image_store, "save_item", side_effect=item_saver) as mock_save:
        image_store.add_item(
            license_info=LicenseInfo("by-nc-sa", "2.0", updated_url, original_url),
            foreign_landing_url=TEST_FOREIGN_LANDING_URL,
            url=TEST_IMAGE_URL,
            foreign_identifier="02",
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
        foreign_landing_url=TEST_FOREIGN_LANDING_URL,
        url=TEST_IMAGE_URL,
        thumbnail_url=None,
        filetype=None,
        filesize=None,
        foreign_identifier="02",
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
        foreign_landing_url=TEST_FOREIGN_LANDING_URL,
        url=TEST_IMAGE_URL,
        meta_data=None,
        raw_tags=raw_tags,
        category=None,
        foreign_identifier="02",
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
        foreign_landing_url=TEST_FOREIGN_LANDING_URL,
        url=TEST_IMAGE_URL,
        thumbnail_url=None,
        filetype=None,
        filesize=None,
        foreign_identifier="02",
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
        foreign_landing_url=TEST_FOREIGN_LANDING_URL,
        url=TEST_IMAGE_URL,
        thumbnail_url=None,
        filetype=None,
        filesize=None,
        foreign_identifier="02",
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
        foreign_landing_url=TEST_FOREIGN_LANDING_URL,
        url=TEST_IMAGE_URL,
        thumbnail_url=None,
        filetype=None,
        filesize=None,
        foreign_identifier="02",
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


# Extracts `jpg` extension from the url.
# Converts `jpeg` to `jpg` to use the standard extension.
# Extracts `tif` extension, and converts it to the standard, `tiff`.
# Does not use extracted extension if it's not a valid image extension.
# Uses the `filetype` even if the `url` extension is different.
@pytest.mark.parametrize(
    "filetype, url, expected_filetype",
    [
        (None, "https://example.com/image.jpg", "jpg"),
        (None, "https://example.com/image.jpeg", "jpg"),
        (None, "https://example.com/image.tif", "tiff"),
        (None, "https://example.com/image.mp3", None),
        ("jpeg", "https://example.com/image.gif", "jpg"),
    ],
)
def test_MediaStore_validates_filetype(filetype, url, expected_filetype):
    image_store = image.MockImageStore("test_provider")
    test_image_args = TEST_IMAGE_DICT | {
        "license_info": BY_LICENSE_INFO,
        "foreign_landing_url": "https://example.com/image.html",
        "foreign_identifier": "image1",
        "url": url,
        "filetype": filetype,
    }
    test_image_args.pop("thumbnail_url")
    image_store.add_item(**test_image_args)
    cleaned_data = image_store.clean_media_metadata(**test_image_args)
    assert cleaned_data["filetype"] == expected_filetype


@INT_MAX_PARAMETERIZATION
def test_MediaStore_validate_integer(value, expected):
    image_store = image.MockImageStore("test_provider")
    actual = image_store._validate_integer(value)
    assert actual == expected


@INT_MAX_PARAMETERIZATION
def test_MediaStore_validates_filesize(value, expected):
    image_store = image.MockImageStore("test_provider")
    test_image_args = TEST_IMAGE_DICT | {
        "license_info": BY_LICENSE_INFO,
        "foreign_landing_url": "https://example.com/image.html",
        "foreign_identifier": "image1",
        "url": TEST_IMAGE_URL,
        "filesize": value,
    }
    test_image_args.pop("thumbnail_url")
    image_store.add_item(**test_image_args)
    cleaned_data = image_store.clean_media_metadata(**test_image_args)
    assert cleaned_data["filesize"] == expected


def test_get_source_preserves_given_both():
    expect_source = "Source"
    actual_source = image.MockImageStore._get_source(expect_source, "test_provider")
    assert actual_source == expect_source


def test_get_source_preserves_source_without_provider():
    input_provider, expect_source = None, "Source"
    actual_source = image.MockImageStore._get_source(expect_source, input_provider)
    assert actual_source == expect_source


def test_get_source_fills_source_if_none_given():
    input_provider, input_source = "Provider", None
    actual_source = image.MockImageStore._get_source(input_source, input_provider)
    expect_source = "Provider"
    assert actual_source == expect_source


def test_get_source_nones_if_none_given():
    actual_source = image.MockImageStore._get_source(None, None)
    assert actual_source is None
