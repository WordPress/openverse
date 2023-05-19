from pathlib import Path
from unittest.mock import call, patch

from common import tsv_cleaner
from common.licenses import LicenseInfo
from common.storage import image


RESOURCES = Path(__file__).parent.resolve() / "test_resources"

by_nc_license = LicenseInfo(
    license="by-nc",
    version="4.0",
    url="https://creativecommons.org/licenses/by-nc/4.0/",
    raw_url="https://creativecommons.org/licenses/by-nc/4.0/",
)
by_license = LicenseInfo(
    license="by",
    version="4.0",
    url="https://creativecommons.org/licenses/by/4.0/",
    raw_url="https://creativecommons.org/licenses/by/4.0/",
)


def test_clean_tsv_cleans_tsv_rows(tmpdir):
    tsv_file_path = RESOURCES / "multi_prov.tsv"

    expected_calls = [
        call(provider="test_provider"),
        call().add_item(
            foreign_landing_url="https://example.com/landing1",
            url="https://example.com/image1",
            thumbnail_url="https://example.com/thumbnail1",
            license_info=by_license,
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
            ingestion_type="provider_api",
        ),
        call(provider="next_provider"),
        call().add_item(
            foreign_landing_url="https://example.com/landing2",
            url="https://example.com/image2",
            thumbnail_url="https://example.com/thumbnail2",
            license_info=by_nc_license,
            foreign_identifier="two",
            width="1000",
            height="500",
            creator="bob",
            creator_url="https://example.com/bob",
            title="title_two",
            meta_data={
                "description": "Train",
                "license_url": "https://creativecommons.org/licenses/by-nc/4.0/",
                "raw_license_url": "https://creativecommons.org/licenses/by-nc/4.0/",
            },
            raw_tags=[
                {"name": "travel", "provider": "next_provider"},
                {"name": "rail", "provider": "other_provider"},
            ],
            watermarked="f",
            source="next_provider",
            ingestion_type="provider_api",
        ),
        call().commit(),
        call().commit(),
    ]

    with patch.object(
        image,
        "ImageStore",
        autospec=True,
    ) as mock_image_store:
        tsv_cleaner.clean_tsv(tsv_file_path)
    for i, expected_call in enumerate(expected_calls):
        assert mock_image_store.mock_calls[i] == expected_call
