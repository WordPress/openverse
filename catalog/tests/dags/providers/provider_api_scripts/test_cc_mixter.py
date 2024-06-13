"""Run these tests locally with `./ov just test -k cc_mixter`"""

import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from common.licenses import LicenseInfo
from providers.provider_api_scripts.cc_mixter import CcMixterDataIngester


RESOURCES = Path(__file__).parent / "resources/cc_mixter"

# Set up test class
ingester = CcMixterDataIngester()


@pytest.mark.parametrize("bad_number", ["0123", "00123", "0123.0"])
def test_custom_requester_parses_bad_json(bad_number):
    response = Mock(text=f'{{"value": {bad_number}}}')

    with pytest.raises(json.decoder.JSONDecodeError):
        json.loads(response.text)

    assert ingester.delayed_requester._get_json(response) == {"value": 123}


@pytest.mark.parametrize(
    "time_string, expected_ms",
    [
        ("2", 2000),  # one segment
        ("1:2", 62000),  # two segments
        ("1:2:3", 3723000),  # three segments
        ("01:02:03", 3723000),  # leading zeros
    ],
)
def test_durations_converted_to_ms(time_string, expected_ms):
    actual_ms = ingester._get_duration(time_string)
    assert actual_ms == expected_ms


@pytest.mark.parametrize(
    "input_ext, output_ext",
    [
        ([], (None, None)),  # no files
        (["zip"], (None, None)),  # ZIP is not audio so no audio files
        (["flac", "mp3"], ("mp3", ["flac"])),  # MP3 is smaller than FLAC
        (["zip", "flac"], ("flac", [])),  # ZIP is not audio but FLAC is
    ],
)
def test_audio_files(
    input_ext: list[str], output_ext: tuple[str, list[str]] | tuple[None, None]
):
    with (RESOURCES / "single_item.json").open() as f:
        single_item = json.load(f)

    input_files = [
        file
        for file in single_item["files"]
        if file["file_format_info"]["default-ext"] in input_ext
    ]
    input_files.sort(
        key=lambda file: input_ext.index(file["file_format_info"]["default-ext"])
    )

    output_files = ingester._get_audio_files(input_files)
    if output_ext == (None, None):
        assert output_files == output_ext
    else:
        assert output_files[0]["filetype"] == output_ext[0]
        assert [file["filetype"] for file in output_files[1]] == output_ext[1]


def test_get_next_query_params_provides_parameters():
    prev_params = None
    for idx in range(3):
        next_params = ingester.get_next_query_params(prev_params)
        expected_next_params = {"format": "json", "limit": 100, "offset": idx * 100}
        assert next_params == expected_next_params
        prev_params = next_params


@pytest.mark.parametrize(
    "results_len, should_continue",
    [
        (101, True),
        (100, True),
        (99, False),
    ],
)
def test_determines_when_to_continue(results_len: int, should_continue: bool):
    actual_result = ingester.get_should_continue([{}] * results_len)
    assert actual_result == should_continue


def test_get_record_data():
    # Sample code for loading in the sample json
    with (RESOURCES / "single_item.json").open() as f:
        single_item = json.load(f)

    single_record = ingester.get_record_data(single_item)

    with (RESOURCES / "expected_single_record.json").open() as f:
        expected_single_record = json.load(f)
    expected_single_record["license_info"] = LicenseInfo(
        **expected_single_record["license_info"]
    )

    assert single_record == expected_single_record
