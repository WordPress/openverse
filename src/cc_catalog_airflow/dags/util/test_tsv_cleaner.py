import os
from unittest.mock import patch, call

from common import get_license_info
from util import tsv_cleaner
from util.loader.ingestion_column import check_and_fix_tsv_file

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "test_resources"
)


def test_clean_tsv_cleans_tsv_rows(tmpdir):
    tsv_file_path = os.path.join(RESOURCES, "multi_prov.tsv")

    expected_calls = [
        call(provider="test_provider"),
        call().add_item(
            foreign_landing_url="https://example.com/landing1",
            image_url="https://example.com/image1",
            thumbnail_url="https://example.com/thumbnail1",
            license_info=get_license_info(license_url="https://creativecommons.org/licenses/by/4.0/"),
            foreign_identifier="one",
            width="1000",
            height="500",
            creator="alice",
            creator_url="https://example.com/alice",
            title="title_one",
            meta_data={
                "pub_date": "1557512425",
                "description": "Airport",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
            },
            raw_tags=[
                {"name": "travel", "provider": "test_provider"},
                {"name": "flying", "provider": "test_provider"},
            ],
            watermarked="f",
            source="alice_official",
        ),
        call(provider="next_provider"),
        call().add_item(
            foreign_landing_url="https://example.com/landing2",
            image_url="https://example.com/image2",
            thumbnail_url="https://example.com/thumbnail2",
            license_info=get_license_info(license_url="https://creativecommons.org/licenses/by-nc/4.0/"),
            foreign_identifier="two",
            width="1000",
            height="500",
            creator="bob",
            creator_url="https://example.com/bob",
            title="title_two",
            meta_data={
                "description": "Train",
                "license_url":
                    "https://creativecommons.org/licenses/by-nc/4.0/",
                "raw_license_url":
                    "https://creativecommons.org/licenses/by-nc/4.0/",
            },
            raw_tags=[
                {"name": "travel", "provider": "next_provider"},
                {"name": "rail", "provider": "other_provider"},
            ],
            watermarked="f",
            source="next_provider",
        ),
        call().commit(),
        call().commit(),
    ]

    with patch.object(
        tsv_cleaner.image,
        "ImageStore",
        autospec=True,
    ) as mock_image_store:
        # tsv file does not have ingestion_type column
        check_and_fix_tsv_file(tsv_file_path)
        tsv_cleaner.clean_tsv(tsv_file_path)
    mock_image_store.assert_has_calls(expected_calls)
