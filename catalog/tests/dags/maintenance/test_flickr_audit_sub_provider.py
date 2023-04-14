from unittest import mock

import pytest
from airflow.exceptions import AirflowSkipException

from maintenance.flickr_audit_sub_provider_workflow import (
    FlickrSubProviderAuditor,
    audit_flickr_sub_providers,
)


auditor = FlickrSubProviderAuditor()


@pytest.mark.parametrize(
    "response_json, expected_institutions",
    (
        (None, None),
        ({"foo": "bar"}, []),
        ({"institutions": {}}, []),
        ({"institutions": {"institution": [{"foo": "bar"}]}}, [{"foo": "bar"}]),
    ),
)
def test_get_institutions(response_json, expected_institutions):
    requester = auditor.requester
    with mock.patch.object(requester, "get_response_json", return_value=response_json):
        assert auditor.get_institutions() == expected_institutions


@pytest.mark.parametrize(
    "response_json, expected_total_count",
    (
        (None, 0),
        ({}, 0),
        ({"photos": {}}, 0),
        ({"photos": {"total": 0}}, 0),
        # 1 record for each license, 8 total records
        ({"photos": {"total": 1}}, 8),
    ),
)
def test_check_for_licensed_images(response_json, expected_total_count):
    requester = auditor.requester
    with mock.patch.object(requester, "get_response_json", return_value=response_json):
        assert auditor.get_cc_image_count("name", "nsid") == expected_total_count


def test_get_new_institutions():
    mock_already_configured_institutions = [
        "24662369@N07",  # Matches 'Already configured' institution
        "35067687@N04",  # Additional test value
    ]
    mock_nsids_to_skip = [
        "61270229@N05",
    ]

    mock_institutions_from_api = [
        # Institutions that should be skipped
        # No name
        {"nsid": "150408343@N02"},
        {"name": {}, "nsid": "150408343@N02"},
        # No nsid
        {"name": {"_content": "Missing NSID"}},
        # Nsid in skip list
        {"name": {"_content": "Skipped NSID"}, "nsid": "61270229@N05"},
        # Already configured in sub-providers
        {"name": {"_content": "Already configured"}, "nsid": "24662369@N07"},
        # This one is mocked to return no CC-licensed images
        {"name": {"_content": "No CC images"}, "nsid": "138361426@N08"},
        # This one is mocked to return only a small number of CC-licensed images
        {"name": {"_content": "Not enough CC images"}, "nsid": "142575440@N02"},
        # Institutions that should be marked for consideration
        # This one is mocked to return CC-licensed_images
        {"name": {"_content": "Institution to consider"}, "nsid": "35128489@N07"},
    ]

    def mock_get_cc_image_count(name, nsid):
        # Mock counts for a few institutions such that they are skipped
        if name == "No CC images":
            return 0  # No cc-licensed images
        if name == "Not enough CC images":
            return 1  # Less than the minimum required number of images

        # All others have enough cc-licensed images
        return 1000

    with (
        mock.patch.object(
            auditor, "get_institutions", return_value=mock_institutions_from_api
        ),
        mock.patch.object(auditor, "get_cc_image_count", new=mock_get_cc_image_count),
    ):
        auditor.current_institutions = mock_already_configured_institutions
        auditor.nsids_to_skip = mock_nsids_to_skip

        actual_institutions = auditor.get_new_institutions_with_cc_licensed_images()
        assert actual_institutions == [
            ("Institution to consider", "35128489@N07", 1000)
        ]


@pytest.mark.parametrize(
    "potential_sub_providers, message",
    (
        # No suggested sub-providers
        pytest.param(
            [],
            "",
            marks=pytest.mark.raises(exception=AirflowSkipException),
        ),
        (
            [("NavyMedicine", "61270229@N05", 1000)],
            "NavyMedicine: 61270229@N05 _(1000 cc-licensed images)_",
        ),
        (
            [
                ("NavyMedicine", "61270229@N05", 1000),
                ("East Riding Archives", "138361426@N08", 2000),
            ],
            "NavyMedicine: 61270229@N05 _(1000 cc-licensed images)_\n"
            "East Riding Archives: 138361426@N08 _(2000 cc-licensed images)_",
        ),
    ),
)
def test_audit_flickr_sub_providers(potential_sub_providers, message):
    with mock.patch(
        "maintenance.flickr_audit_sub_provider_workflow.FlickrSubProviderAuditor.get_new_institutions_with_cc_licensed_images",
        return_value=potential_sub_providers,
    ):
        actual_message = audit_flickr_sub_providers()
        assert message in actual_message
