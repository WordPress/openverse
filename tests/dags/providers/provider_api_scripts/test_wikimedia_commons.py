import json
import logging
from pathlib import Path
from unittest.mock import patch

from common.constants import IMAGE
from common.licenses import get_license_info
from providers.provider_api_scripts.wikimedia_commons import (
    WikimediaCommonsDataIngester,
)


RESOURCES = Path(__file__).parent.resolve() / "resources/wikimedia"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s",
    level=logging.DEBUG,
)

wmc = WikimediaCommonsDataIngester(date="2018-01-15")


def test_derive_timestamp_pair():
    # Note that the timestamps are derived as if input was in UTC.
    actual_start_ts, actual_end_ts = wmc.derive_timestamp_pair("2018-01-15")
    assert actual_start_ts == "1515974400"
    assert actual_end_ts == "1516060800"


def test_get_media_pages_returns_correctly_with_continue():
    with open(RESOURCES / "response_small_with_continue.json") as f:
        resp_dict = json.load(f)

    expect_result = {"84798633": {"pageid": 84798633, "title": "File:Ambassade1.jpg"}}
    actual_result = wmc.get_media_pages(resp_dict)
    assert actual_result == expect_result


def test_get_batch_data_returns_correctly_with_pages():
    with open(RESOURCES / "response_small_with_continue.json") as f:
        resp_dict = json.load(f)

    expect_result = [
        {"pageid": 84798633, "title": "File:Ambassade1.jpg"},
    ]
    actual_result = wmc.get_batch_data(resp_dict)
    assert list(actual_result) == expect_result


def test_get_batch_data_returns_correctly_with_none_json():
    expect_result = None
    actual_result = wmc.get_batch_data(None)
    assert actual_result == expect_result


def test_get_batch_data_returns_correctly_with_no_pages():
    expect_result = None
    actual_result = wmc.get_batch_data({"batch_complete": ""})
    assert actual_result == expect_result


def test_get_next_query_params_adds_start_and_end():
    actual_qp = wmc.get_next_query_params(prev_query_params={})
    assert actual_qp["gaistart"] == wmc.start_timestamp
    assert actual_qp["gaiend"] == wmc.end_timestamp


def test_get_next_query_params_adds_continue():
    wmc.continue_token = {"gaicontinue": "200|next.jpg", "continue": "gaicontinue||"}
    actual_qp = wmc.get_next_query_params(
        prev_query_params={},
    )
    assert actual_qp["gaicontinue"] == "200|next.jpg"
    assert actual_qp["continue"] == "gaicontinue||"


def test_get_response_json(monkeypatch):
    with open(RESOURCES / "continuation/wmc_pretty1.json") as f:
        first_response = json.load(f)
    with open(RESOURCES / "continuation/wmc_pretty2.json") as f:
        second_response = json.load(f)
    with open(RESOURCES / "continuation/wmc_pretty3.json") as f:
        third_response = json.load(f)

    def mock_get_response_json(endpoint, retries, query_params, **kwargs):
        continue_one = "Edvard_Munch_-_Night_in_Nice_(1891).jpg|nowiki|1281339"
        continue_two = "Niedercunnersdorf_Gartenweg_12.JPG|dewiki|9849507"
        logging.info(f"Testing with: {query_params}")
        if "continue" not in query_params:
            return first_response
        elif query_params.get("gucontinue") == continue_one:
            return second_response
        elif query_params.get("gucontinue") == continue_two:
            return third_response
        else:
            return None

    with open(RESOURCES / "continuation/wmc_pretty123.json") as f:
        expect_image_batch = json.load(f)
    expect_continue_token = expect_image_batch.pop("continue")

    monkeypatch.setattr(
        wmc.delayed_requester, "get_response_json", mock_get_response_json
    )
    wmc.continue_token = {}
    actual_image_batch = wmc.get_response_json(wmc.get_next_query_params({}))
    assert actual_image_batch == expect_image_batch
    assert wmc.continue_token == expect_continue_token


def test_get_response_json_returns_correctly_without_continue(monkeypatch):
    with open(RESOURCES / "response_small_missing_continue.json") as f:
        resp_dict = json.load(f)

    wmc.continue_token = {}
    with patch.object(
        wmc.delayed_requester, "get_response_json", return_value=resp_dict
    ) as mock_response_json:
        actual_result = wmc.get_response_json(wmc.get_next_query_params({}))

    expect_result = resp_dict
    expect_continue = {}

    mock_response_json.assert_called_once()
    assert wmc.continue_token == expect_continue
    assert actual_result == expect_result


def test_merge_response_jsons():
    with open(RESOURCES / "continuation/wmc_pretty1.json") as f:
        left_response = json.load(f)
    with open(RESOURCES / "continuation/wmc_pretty2.json") as f:
        right_response = json.load(f)
    with open(RESOURCES / "continuation/wmc_pretty1plus2.json") as f:
        expect_merged_response = json.load(f)

    actual_merged_response = wmc.merge_response_jsons(
        left_response,
        right_response,
    )
    assert actual_merged_response == expect_merged_response


def test_merge_media_pages_left_only_with_gu():
    with open(RESOURCES / "continuation/page_44672185_left.json") as f:
        left_page = json.load(f)
    with open(RESOURCES / "continuation/page_44672185_right.json") as f:
        right_page = json.load(f)
    actual_merged_page = wmc.merge_media_pages(left_page, right_page)
    assert actual_merged_page == left_page


def test_merge_media_pages_left_only_with_gu_backwards():
    with open(RESOURCES / "continuation/page_44672185_left.json") as f:
        left_page = json.load(f)
    with open(RESOURCES / "continuation/page_44672185_right.json") as f:
        right_page = json.load(f)
    actual_merged_page = wmc.merge_media_pages(right_page, left_page)
    assert actual_merged_page == left_page


def test_merge_media_pages_neither_have_gu():
    with open(RESOURCES / "continuation/page_44672210_left.json") as f:
        left_page = json.load(f)
    with open(RESOURCES / "continuation/page_44672210_right.json") as f:
        right_page = json.load(f)
    actual_merged_page = wmc.merge_media_pages(left_page, right_page)
    assert actual_merged_page == left_page


def test_merge_media_pages_neigher_have_gu_backwards():
    with open(RESOURCES / "continuation/page_44672210_left.json") as f:
        left_page = json.load(f)
    with open(RESOURCES / "continuation/page_44672210_right.json") as f:
        right_page = json.load(f)
    actual_merged_page = wmc.merge_media_pages(right_page, left_page)
    assert actual_merged_page == left_page


def test_merge_media_pages_both_have_gu():
    with open(RESOURCES / "continuation/page_44672212_left.json") as f:
        left_page = json.load(f)
    with open(RESOURCES / "continuation/page_44672212_right.json") as f:
        right_page = json.load(f)
    with open(RESOURCES / "continuation/page_44672212_merged.json") as f:
        expect_merged_page = json.load(f)
    actual_merged_page = wmc.merge_media_pages(left_page, right_page)
    assert actual_merged_page == expect_merged_page


def test_extract_title_gets_cleaned_title():
    image_info = {"extmetadata": {"ObjectName": {"value": "File:filename.jpg"}}}
    actual_title = wmc.extract_title(image_info)
    expected_title = "filename"
    assert actual_title == expected_title

    image_info["title"] = "filename.jpeg"
    actual_title = wmc.extract_title(image_info)
    expected_title = "filename"
    assert actual_title == expected_title


def test_get_record_data_handles_example_dict():
    """
    Converts sample json data to correct image metadata,
    and calls `add_item` once for a valid image.
    """
    with open(RESOURCES / "image_data_example.json") as f:
        media_data = json.load(f)

    record_data = wmc.get_record_data(media_data)

    expected_license_info = get_license_info(
        license_url="https://creativecommons.org/licenses/by-sa/4.0"
    )
    assert record_data == {
        "foreign_landing_url": (
            "https://commons.wikimedia.org/w/index.php?curid=81754323"
        ),
        "foreign_identifier": 81754323,
        "image_url": (
            "https://upload.wikimedia.org/wikipedia/commons/2/25/20120925_"
            "PlozevetBretagne_LoneTree_DSC07971_PtrQs.jpg"
        ),
        "license_info": expected_license_info,
        "width": 5514,
        "height": 3102,
        "creator": "PtrQs",
        "creator_url": "//commons.wikimedia.org/wiki/User:PtrQs",
        "title": "20120925 PlozevetBretagne LoneTree DSC07971 PtrQs",
        "filetype": "jpg",
        "filesize": 11863148,
        "meta_data": {
            "description": "SONY DSC",
            "global_usage_count": 0,
            "date_originally_created": "2012-09-25 16:23:02",
            "last_modified_at_source": "2019-09-01 00:38:47",
            "categories": [
                "Coasts of Ploz\u00e9vet",
                "No QIC by usr:PtrQs",
                "Photographs taken with Minolta AF Zoom " "28-70mm F2.8 G",
                "Self-published work",
                "Taken with Sony DSLR-A900",
                "Trees in Finist\u00e8re",
            ],
        },
        "media_type": "image",
    }


def test_get_record_data_throws_out_invalid_mediatype(monkeypatch):
    media_data = {"mediatype": "INVALID"}
    data = wmc.get_record_data(media_data)
    assert data is None


def test_extract_media_info_dict():
    with open(RESOURCES / "image_data_example.json") as f:
        media_data = json.load(f)

    with open(RESOURCES / "image_info_from_example_data.json") as f:
        expect_image_info = json.load(f)

    actual_image_info = wmc.extract_media_info_dict(media_data)

    assert actual_image_info == expect_image_info


def test_extract_mediatype_with_valid_image_info():
    with open(RESOURCES / "image_info_from_example_data.json") as f:
        image_info = json.load(f)

    valid_mediatype = wmc.extract_media_type(image_info)
    assert valid_mediatype == IMAGE


def test_extract_mediatype_with_invalid_mediatype_in_image_info():
    with open(RESOURCES / "image_info_from_example_data.json") as f:
        image_info = json.load(f)

    image_info["mediatype"] = "INVALIDTYPE"

    valid_mediatype = wmc.extract_media_type(image_info)
    assert valid_mediatype is None


def test_extract_creator_info_handles_plaintext():
    with open(RESOURCES / "image_info_artist_string.json") as f:
        image_info = json.load(f)
    actual_creator, actual_creator_url = wmc.extract_creator_info(image_info)
    expect_creator = "Artist Name"
    expect_creator_url = None
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_extract_creator_info_handles_well_formed_link():
    with open(RESOURCES / "image_info_artist_link.json") as f:
        image_info = json.load(f)
    actual_creator, actual_creator_url = wmc.extract_creator_info(image_info)
    expect_creator = "link text"
    expect_creator_url = "https://test.com/linkspot"
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_extract_creator_info_handles_div_with_no_link():
    with open(RESOURCES / "image_info_artist_div.json") as f:
        image_info = json.load(f)
    actual_creator, actual_creator_url = wmc.extract_creator_info(image_info)
    expect_creator = "Jona Lendering"
    expect_creator_url = None
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_extract_creator_info_handles_internal_wc_link():
    with open(RESOURCES / "image_info_artist_internal_link.json") as f:
        image_info = json.load(f)
    actual_creator, actual_creator_url = wmc.extract_creator_info(image_info)
    expect_creator = "NotaRealUser"
    expect_creator_url = (
        "//commons.wikimedia.org/w/index.php?title=User:NotaRealUser&"
        "action=edit&redlink=1"
    )
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_extract_creator_info_handles_link_as_partial_text():
    with open(RESOURCES / "image_info_artist_partial_link.json") as f:
        image_info = json.load(f)
    actual_creator, actual_creator_url = wmc.extract_creator_info(image_info)
    expect_creator = "Jeff & Brian from Eastbourne"
    expect_creator_url = "https://www.flickr.com/people/16707908@N07"
    assert expect_creator == actual_creator
    assert expect_creator_url == actual_creator_url


def test_extract_license_info_finds_license_url():
    with open(RESOURCES / "image_info_from_example_data.json") as f:
        image_info = json.load(f)

    expect_license_url = "https://creativecommons.org/licenses/by-sa/4.0/"
    actual_license_url = wmc.extract_license_info(image_info).url
    assert actual_license_url == expect_license_url


def test_extract_license_url_handles_missing_license_url():
    with open(RESOURCES / "image_info_artist_partial_link.json") as f:
        image_info = json.load(f)
    expect_license_url = None
    actual_license_url = wmc.extract_license_info(image_info).url
    assert actual_license_url == expect_license_url


def test_create_meta_data_scrapes_text_from_html_description():
    with open(RESOURCES / "image_data_html_description.json") as f:
        media_data = json.load(f)
    expect_description = (
        "Identificatie Titel(s):  Allegorie op kunstenaar Francesco Mazzoli, "
        "bekend als Parmigianino"
    )
    actual_description = wmc.create_meta_data_dict(media_data)["description"]
    assert actual_description == expect_description


def test_create_meta_data_tallies_global_usage_count():
    with open(RESOURCES / "continuation/page_44672185_left.json") as f:
        media_data = json.load(f)
    actual_gu = wmc.create_meta_data_dict(media_data)["global_usage_count"]
    expect_gu = 3
    assert actual_gu == expect_gu


def test_create_meta_data_tallies_zero_global_usage_count():
    with open(RESOURCES / "continuation/page_44672185_right.json") as f:
        media_data = json.load(f)
    actual_gu = wmc.create_meta_data_dict(media_data)["global_usage_count"]
    expect_gu = 0
    assert actual_gu == expect_gu


def test_get_audio_record_data_parses_ogg_streams():
    with open(RESOURCES / "audio_filedata_ogg.json") as f:
        file_metadata = json.load(f)
    original_data = {"media_url": "myurl.com", "meta_data": {}}
    actual_parsed_data = wmc.get_audio_record_data(original_data, file_metadata)

    expected_parsed_data = {
        "audio_url": "myurl.com",
        "bit_rate": 112000,
        "sample_rate": 48000,
        "meta_data": {"channels": 2},
    }
    assert actual_parsed_data.items() >= expected_parsed_data.items()


def test_get_audio_record_data_parses_wav_audio_data():
    with open(RESOURCES / "audio_filedata_wav.json") as f:
        file_metadata = json.load(f)
    original_data = {"media_url": "myurl.com", "meta_data": {}}
    actual_parsed_data = wmc.get_audio_record_data(original_data, file_metadata)

    expected_parsed_data = {
        "audio_url": "myurl.com",
        "bit_rate": 768000,
        "sample_rate": 48000,
        "meta_data": {"channels": 1},
    }
    assert actual_parsed_data.items() >= expected_parsed_data.items()


def test_get_audio_record_data_parses_wav_audio_data_missing_streams():
    with open(RESOURCES / "audio_filedata_wav.json") as f:
        file_metadata = json.load(f)
    original_data = {"media_url": "myurl.com", "meta_data": {}}
    # Remove any actual audio metadata
    file_metadata["metadata"] = (
        file_metadata["metadata"][:5] + file_metadata["metadata"][6:]
    )
    actual_parsed_data = wmc.get_audio_record_data(original_data, file_metadata)
    expected_parsed_data = {
        "audio_url": "myurl.com",
        "meta_data": {},
    }
    # No data is available, so nothing should be added
    assert actual_parsed_data.items() >= expected_parsed_data.items()


def test_get_audio_record_data_parses_wav_invalid_bit_rate():
    with open(RESOURCES / "audio_filedata_wav.json") as f:
        file_metadata = json.load(f)
    original_data = {"media_url": "myurl.com", "meta_data": {}}
    # Set the bit rate higher than the int max
    file_metadata["metadata"][5]["value"][3]["value"][0]["value"][3][
        "value"
    ] = 4294967294
    expected_parsed_data = {
        "audio_url": "myurl.com",
        "bit_rate": None,
        "sample_rate": 48000,
        "meta_data": {"channels": 1},
    }
    actual_parsed_data = wmc.get_audio_record_data(original_data, file_metadata)
    assert actual_parsed_data.items() >= expected_parsed_data.items()
