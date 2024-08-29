from pathlib import Path
from unittest import mock

import pytest
import smart_open.s3

from data_augmentation.rekognition import add_rekognition_labels, constants
from data_augmentation.rekognition.label_mapping import LABEL_MAPPING
from data_augmentation.rekognition.types import ParseResults


TEST_PREFIX = "image_analysis_labels.jsonl"
SAMPLE_LABEL = sorted(LABEL_MAPPING.keys())[0]
SAMPLE_JSON = (Path(__file__).parent / "sample_labels.json").read_text()
DEFAULT_ARGS = {
    "s3_bucket": constants.S3_BUCKET,
    "s3_prefix": TEST_PREFIX,
    "in_memory_buffer_size": 1000,
    "file_buffer_size": smart_open.s3.DEFAULT_BUFFER_SIZE,
    "postgres_conn_id": "shim",
}


patch_insert_tags = mock.patch.object(add_rekognition_labels, "_insert_tags")
patch_variable = mock.patch.object(add_rekognition_labels, "Variable")


@pytest.mark.parametrize(
    "labels, expected",
    [
        # Empty case
        ([], []),
        # Standard label creation
        (
            [
                {"Name": "Dog", "Confidence": 99.8},
                {"Name": "Cat", "Confidence": 77.7},
            ],
            [
                {"name": "Dog", "accuracy": 0.998, "provider": "rekognition"},
                {"name": "Cat", "accuracy": 0.777, "provider": "rekognition"},
            ],
        ),
        # Mapped label creation
        (
            [{"Name": SAMPLE_LABEL, "Confidence": 99.8}],
            [
                {
                    "name": LABEL_MAPPING[SAMPLE_LABEL],
                    "accuracy": 0.998,
                    "provider": "rekognition",
                }
            ],
        ),
    ],
)
def test_process_labels(labels, expected):
    actual = add_rekognition_labels._process_labels(labels)
    assert actual == expected


@mock.patch("smart_open.open")
@patch_insert_tags
@patch_variable
def test_parse_and_insert_labels_parse(mock_variable, mock_insert_tags, mock_file):
    mock_variable.get.return_value = None
    mock_file.return_value.__enter__.return_value.readline.side_effect = [
        SAMPLE_JSON,
        '{"image_uuid": "b840de61-fb9d-4ec5-9572-8d778875869f", "response": {"Labels": []}}',
        "this line should fail!",
        "",
    ]
    actual = add_rekognition_labels.parse_and_insert_labels.function(**DEFAULT_ARGS)

    assert actual == ParseResults(3, 1, ["this line should fail!"])
    mock_insert_tags.assert_called_once()
    assert (
        # Check the first image UUID
        # Args list -> list to insert -> first tuple -> first element
        mock_insert_tags.call_args.args[0][0][0]
        == "b840de61-fb9d-4ec5-9572-8d778875869f"
    )

    # Variable should not have been set since the buffer was not reached,
    # but it should have been deleted after the file was processed
    mock_variable.set.assert_not_called()
    mock_variable.delete.assert_called_once()


@pytest.mark.parametrize(
    "known_offset, in_memory_buffer_size, expected_insert_call_count, expected_processed, expected_skipped",
    [
        (0, 100, 2, 200, 1),
        (0, 10, 20, 200, 1),
        # Known offsets based on actual results from testing
        (231319, 100, 1, 75, 1),
        (332571, 100, 1, 25, 1),
    ],
)
@patch_insert_tags
@patch_variable
def test_parse_and_insert_labels_buffer_config(
    mock_variable,
    mock_insert_tags,
    known_offset,
    in_memory_buffer_size,
    expected_insert_call_count,
    expected_processed,
    expected_skipped,
):
    mock_variable.get.return_value = known_offset
    actual = add_rekognition_labels.parse_and_insert_labels.function(
        **{**DEFAULT_ARGS, "in_memory_buffer_size": in_memory_buffer_size}
    )

    assert actual == ParseResults(expected_processed, expected_skipped, [])
    assert mock_insert_tags.call_count == expected_insert_call_count
    assert mock_variable.set.call_count == expected_insert_call_count - 1
    mock_variable.delete.assert_called_once()
