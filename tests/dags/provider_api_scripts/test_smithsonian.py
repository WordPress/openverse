import json
import logging
import os
from unittest.mock import call, patch

import provider_api_scripts.smithsonian as si
import pytest
from common.licenses.licenses import LicenseInfo


logger = logging.getLogger(__name__)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.DEBUG
)

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "resources/smithsonian"
)


def _get_resource_json(json_name):
    with open(os.path.join(RESOURCES, json_name)) as f:
        resource_json = json.load(f)
    return resource_json


def test_get_hash_prefixes_with_len_one():
    expect_prefix_list = [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
    ]
    actual_prefix_list = list(si._get_hash_prefixes(1))
    assert actual_prefix_list == expect_prefix_list


@pytest.mark.parametrize(
    "input_int,expect_len,expect_first,expect_last",
    [
        (1, 16, "0", "f"),
        (2, 256, "00", "ff"),
        (3, 4096, "000", "fff"),
        (4, 65536, "0000", "ffff"),
    ],
)
def test_get_hash_prefixes_with_other_len(
    input_int, expect_len, expect_first, expect_last
):
    actual_list = list(si._get_hash_prefixes(input_int))
    assert all("0x" not in h for h in actual_list)
    assert all(
        int(actual_list[i + 1], 16) - int(actual_list[i], 16) == 1
        for i in range(len(actual_list) - 1)
    )
    assert len(actual_list) == expect_len
    assert actual_list[0] == expect_first
    assert actual_list[-1] == expect_last


def test_process_hash_prefix_with_none_response_json():
    endpoint = "https://abc.com/123"
    limit = 100
    hash_prefix = "00"
    retries = 3
    qp = {"q": "abc"}

    patch_get_response_json = patch.object(
        si.delayed_requester, "get_response_json", return_value=None
    )
    patch_build_qp = patch.object(si, "_build_query_params", return_value=qp)
    patch_process_response = patch.object(si, "_process_response_json")
    with patch_get_response_json as mock_get_response_json, patch_build_qp as mock_build_qp, patch_process_response as mock_process_response:
        si._process_hash_prefix(
            hash_prefix, endpoint=endpoint, limit=limit, retries=retries
        )
    mock_process_response.assert_not_called()
    mock_build_qp.assert_called_once_with(0, hash_prefix=hash_prefix)
    mock_get_response_json.assert_called_once_with(
        endpoint, retries=retries, query_params=qp
    )


def test_process_hash_prefix_with_response_json_no_row_count():
    endpoint = "https://abc.com/123"
    limit = 100
    hash_prefix = "00"
    retries = 3
    qp = {"q": "abc"}
    response_json = {"abc": "123"}

    patch_get_response_json = patch.object(
        si.delayed_requester, "get_response_json", return_value=response_json
    )
    patch_build_qp = patch.object(si, "_build_query_params", return_value=qp)
    patch_process_response = patch.object(si, "_process_response_json")
    with patch_get_response_json as mock_get_response_json, patch_build_qp as mock_build_qp, patch_process_response as mock_process_response:
        si._process_hash_prefix(
            hash_prefix, endpoint=endpoint, limit=limit, retries=retries
        )
    mock_process_response.assert_called_with(response_json)
    mock_build_qp.assert_called_once_with(0, hash_prefix=hash_prefix)
    mock_get_response_json.assert_called_once_with(
        endpoint, retries=retries, query_params=qp
    )


def test_process_hash_prefix_with_good_response_json():
    endpoint = "https://abc.com/123"
    limit = 100
    hash_prefix = "00"
    retries = 3
    qp = {"q": "abc"}
    response_json = {"response": {"abc": "123", "rowCount": 150}}

    patch_get_response_json = patch.object(
        si.delayed_requester, "get_response_json", return_value=response_json
    )
    patch_build_qp = patch.object(si, "_build_query_params", return_value=qp)
    patch_process_response = patch.object(si, "_process_response_json", return_value=0)
    with patch_build_qp as mock_build_qp, patch_get_response_json as mock_get_response_json, patch_process_response as mock_process_response:
        si._process_hash_prefix(
            hash_prefix, endpoint=endpoint, limit=limit, retries=retries
        )
    expect_process_response_calls = [call(response_json), call(response_json)]
    expect_build_qp_calls = [
        call(0, hash_prefix=hash_prefix),
        call(limit, hash_prefix=hash_prefix),
    ]
    expect_get_response_json_calls = [
        call(endpoint, retries=retries, query_params=qp),
        call(endpoint, retries=retries, query_params=qp),
    ]
    mock_build_qp.assert_has_calls(expect_build_qp_calls)
    mock_get_response_json.assert_has_calls(expect_get_response_json_calls)
    mock_process_response.assert_has_calls(expect_process_response_calls)


def test_build_query_params():
    hash_prefix = "ff"
    row_offset = 10
    default_params = {"api_key": "pass123", "rows": 10}
    acutal_params = si._build_query_params(
        row_offset, hash_prefix=hash_prefix, default_params=default_params
    )
    expect_params = {
        "api_key": "pass123",
        "rows": 10,
        "q": (
            f"online_media_type:Images AND media_usage:CC0 " f"AND hash:{hash_prefix}*"
        ),
        "start": row_offset,
    }
    assert acutal_params == expect_params
    assert default_params == {"api_key": "pass123", "rows": 10}


def test_process_response_json_with_no_rows_json():
    response_json = {
        "status": 200,
        "responseCode": 1,
        "response": {
            "norows": ["abc", "def"],
            "rowCount": 2,
            "message": "content found",
        },
    }
    patch_process_image_list = patch.object(si, "_process_image_list", return_value=2)

    with patch_process_image_list as mock_process_image_list:
        si._process_response_json(response_json)

    mock_process_image_list.assert_not_called()


def test_process_response_json_uses_required_getters():
    """
    This test only checks for appropriate calls to getter functions
    """
    response_json = {"test key": "test value"}
    row_list = ["row0", "row1"]
    image_lists = [["image", "list", "zero"], ["image", "list", "one"]]
    flu_list = ["flu0", "flu1"]
    title_list = ["title0", "title1"]
    creator_list = ["creator0", "creator1"]
    metadata_list = ["metadata0", "metadata1"]
    tags_list = ["tags0", "tags1"]
    source_list = ["source0", "source1"]

    get_row_list = patch.object(si, "_get_row_list", return_value=row_list)
    process_image_list = patch.object(si, "_process_image_list", return_value=2)
    get_image_list = patch.object(si, "_get_image_list", side_effect=image_lists)
    get_flu = patch.object(si, "_get_foreign_landing_url", side_effect=flu_list)
    get_title = patch.object(si, "_get_title", side_effect=title_list)
    get_creator = patch.object(si, "_get_creator", side_effect=creator_list)
    ext_meta_data = patch.object(si, "_extract_meta_data", side_effect=metadata_list)
    ext_tags = patch.object(si, "_extract_tags", side_effect=tags_list)
    ext_source = patch.object(si, "_extract_source", side_effect=source_list)

    with get_row_list as mock_get_row_list, get_image_list as mock_get_image_list, get_flu as mock_get_foreign_landing_url, get_title as mock_get_title, get_creator as mock_get_creator, ext_meta_data as mock_extract_meta_data, ext_tags as mock_extract_tags, ext_source as mock_extract_source, process_image_list as mock_process_image_list:
        si._process_response_json(response_json)

    getter_calls_list = [call(r) for r in row_list]
    image_processing_call_list = [
        call(
            image_lists[0],
            flu_list[0],
            title_list[0],
            creator_list[0],
            metadata_list[0],
            tags_list[0],
            source_list[0],
        ),
        call(
            image_lists[1],
            flu_list[1],
            title_list[1],
            creator_list[1],
            metadata_list[1],
            tags_list[1],
            source_list[1],
        ),
    ]
    mock_get_row_list.assert_called_once_with(response_json)
    assert mock_process_image_list.mock_calls == image_processing_call_list
    assert mock_get_image_list.mock_calls == getter_calls_list
    assert mock_get_foreign_landing_url.mock_calls == getter_calls_list
    assert mock_get_title.mock_calls == getter_calls_list
    assert mock_get_creator.mock_calls == getter_calls_list
    assert mock_extract_meta_data.mock_calls == getter_calls_list
    assert mock_extract_tags.mock_calls == getter_calls_list
    assert mock_extract_source.mock_calls == [call(m) for m in metadata_list]


def test_get_row_list_with_no_rows():
    response_json = {"not": "rows"}
    row_list = si._get_row_list(response_json)
    assert row_list == []


@pytest.mark.parametrize(
    "input_row_list,expect_row_list",
    [
        ([], []),
        ("abc", []),  # wrong type
        ({"key": "val"}, []),  # wrong type
        ([{"key", "val"}], [{"key", "val"}]),  # nested dict
        ([{"key1", "val1"}, "abc"], [{"key1", "val1"}, "abc"]),
    ],
)
def test_get_row_list(input_row_list, expect_row_list):
    response_json = {
        "status": 200,
        "responseCode": 1,
        "response": {
            "rows": input_row_list,
            "rowCount": 734,
            "message": "content found",
        },
    }
    actual_row_list = si._get_row_list(response_json)
    assert actual_row_list == expect_row_list


@pytest.mark.parametrize(
    "input_dnr,expect_image_list",
    [
        ({}, []),
        ({"non_media": {"media": ["image1", "image2"]}}, []),
        ({"online_media": "wrong type"}, []),
        ({"online_media": ["wrong", "type"]}, []),
        ({"online_media": {"media": "wrong type"}}, []),
        ({"online_media": {"media": {"wrong": "type"}}}, []),
        (
            {
                "record_ID": "siris_arc_291918",
                "online_media": {"mediaCount": 1, "media": ["image1", "image2"]},
            },
            ["image1", "image2"],
        ),
    ],
)
def test_get_image_list(input_dnr, expect_image_list):
    input_row = {"key": "val"}
    with patch.object(
        si, "_get_descriptive_non_repeating_dict", return_value=input_dnr
    ) as mock_dnr:
        actual_image_list = si._get_image_list(input_row)
    mock_dnr.assert_called_once_with(input_row)
    assert actual_image_list == expect_image_list


@pytest.mark.parametrize(
    "input_dnr,expect_foreign_landing_url",
    [
        ({}, None),
        (
            {
                "guid": "http://fallback.com",
                "unit_code": "NMNHMAMMALS",
                "record_link": "http://chooseme.com",
            },
            "http://chooseme.com",
        ),
        ({"guid": "http://fallback.com"}, "http://fallback.com"),
        ({"no": "urlhere"}, None),
    ],
)
def test_get_foreign_landing_url(input_dnr, expect_foreign_landing_url):
    input_row = {"key": "val"}
    with patch.object(
        si, "_get_descriptive_non_repeating_dict", return_value=input_dnr
    ) as mock_dnr:
        actual_foreign_landing_url = si._get_foreign_landing_url(input_row)
    mock_dnr.assert_called_once_with(input_row)
    assert actual_foreign_landing_url == expect_foreign_landing_url


@pytest.mark.parametrize(
    "input_row,expect_title",
    [
        ({}, None),
        ({"id": "abcde"}, None),
        ({"title": "my Title"}, "my Title"),
        ({"id": "abcde", "title": "my Title"}, "my Title"),
    ],
)
def test_get_title(input_row, expect_title):
    actual_title = si._get_title(input_row)
    assert actual_title == expect_title


@pytest.mark.parametrize(
    "input_is,input_ft,expect_creator",
    [
        ({}, {}, None),
        ({"name": ["Alice"]}, {}, None),
        ({"name": "alice"}, {}, None),
        ({"name": [{"type": ["personal", "main"], "nocontent": "Alice"}]}, {}, None),
        ({"name": [{"type": "personal_main", "nocontent": "Alice"}]}, {}, None),
        ({"noname": [{"type": "personal_main", "content": "Alice"}]}, {}, None),
        ({"name": [{"label": "personal_main", "content": "Alice"}]}, {}, None),
        ({"name": [{"type": "impersonal_main", "content": "Alice"}]}, {}, None),
        (
            {"name": [{"type": "personal_main", "content": "Alice"}]},
            {"name": "Bob"},
            "Alice",
        ),
        (
            {"name": [{"type": "personal_main", "content": "Alice"}]},
            {"name": ["Bob"]},
            "Alice",
        ),
        (
            {"name": [{"type": "personal_main", "content": "Alice"}]},
            {"name": [{"label": "Creator", "nocontent": "Bob"}]},
            "Alice",
        ),
        (
            {"name": [{"type": "personal_main", "content": "Alice"}]},
            {"name": [{"nolabel": "Creator", "content": "Bob"}]},
            "Alice",
        ),
        (
            {"name": [{"type": "personal_main", "content": "Alice"}]},
            {"name": [{"label": "NotaCreator", "content": "Bob"}]},
            "Alice",
        ),
        (
            {"name": [{"type": "personal_main", "content": "Alice"}]},
            {"noname": [{"label": "Creator", "content": "Bob"}]},
            "Alice",
        ),
        (
            {"name": [{"type": "personal_main", "content": "Alice"}]},
            {"name": [{"label": "Creator", "content": "Bob"}]},
            "Bob",
        ),
        (
            {},
            {
                "name": [
                    {"label": "Designer", "content": "Alice"},
                    {"label": "Creator", "content": "Bob"},
                ]
            },
            "Bob",
        ),
        (
            {},
            {
                "name": [
                    {"label": "AFTER", "content": "Bob"},
                    {"label": "Designer", "content": "Alice"},
                ]
            },
            "Alice",
        ),
        (
            {},
            {
                "name": [
                    {"label": "AFTER", "content": "Bob"},
                    {"label": "DESIGNER", "content": "Alice"},
                ]
            },
            "Alice",
        ),
        (
            {
                "name": [
                    {"type": "personal_main", "content": "Alice"},
                    {"type": "corporate_subj", "content": "Zoological Park"},
                ]
            },
            {
                "name": [
                    {"label": "Creator", "content": "Bob"},
                    {"label": "Subject", "content": "Zoological Park"},
                ]
            },
            "Bob",
        ),
    ],
)
def test_get_creator(input_is, input_ft, expect_creator):
    creator_types = {"creator": 0, "designer": 1, "after": 3}
    input_row = {"test": "row"}
    get_is = patch.object(si, "_get_indexed_structured_dict", return_value=input_is)
    get_ft = patch.object(si, "_get_freetext_dict", return_value=input_ft)
    with get_is as mock_is, get_ft as mock_ft:
        actual_creator = si._get_creator(input_row, creator_types=creator_types)

    mock_is.assert_called_once_with(input_row)
    mock_ft.assert_called_once_with(input_row)
    assert actual_creator == expect_creator


@pytest.mark.parametrize(
    "input_ft,input_dnr,expect_description",
    [
        ({}, {}, None),
        ({"notes": [{"label": "notthis", "content": "blah"}]}, {}, None),
        ({"notes": "notalist"}, {}, None),
        ({"notes": [{"label": "Summary", "content": "blah"}]}, {}, "blah"),
        (
            {
                "notes": [
                    {"label": "Description", "content": "blah"},
                    {"label": "Summary", "content": "blah"},
                    {"label": "Description", "content": "blah"},
                ]
            },
            {},
            "blah blah blah",
        ),
        (
            {
                "notes": [
                    {"label": "notDescription", "content": "blah"},
                    {"label": "Summary", "content": "blah"},
                    {"label": "Description", "content": "blah"},
                ]
            },
            {},
            "blah blah",
        ),
    ],
)
def test_ext_meta_data_description(input_ft, input_dnr, expect_description):
    description_types = {"description", "summary"}
    input_row = {"test": "row"}
    get_dnr = patch.object(
        si, "_get_descriptive_non_repeating_dict", return_value=input_dnr
    )
    get_ft = patch.object(si, "_get_freetext_dict", return_value=input_ft)
    with get_dnr as mock_dnr, get_ft as mock_ft:
        meta_data = si._extract_meta_data(
            input_row, description_types=description_types
        )
    actual_description = meta_data.get("description")
    mock_dnr.assert_called_once_with(input_row)
    mock_ft.assert_called_once_with(input_row)
    assert actual_description == expect_description


@pytest.mark.parametrize(
    "input_ft,input_dnr,expect_label_text",
    [
        ({}, {}, None),
        ({"notes": [{"label": "notthis", "content": "blah"}]}, {}, None),
        ({"notes": "notalist"}, {}, None),
        ({"notes": [{"label": "Label Text", "content": "blah"}]}, {}, "blah"),
        (
            {
                "notes": [
                    {"label": "Label Text", "content": "blah"},
                    {"label": "Summary", "content": "halb"},
                    {"label": "Description", "content": "halb"},
                ]
            },
            {},
            "blah",
        ),
    ],
)
def test_ext_meta_data_label_text(input_ft, input_dnr, expect_label_text):
    input_row = {"test": "row"}
    get_dnr = patch.object(
        si, "_get_descriptive_non_repeating_dict", return_value=input_dnr
    )
    get_ft = patch.object(si, "_get_freetext_dict", return_value=input_ft)
    with get_dnr as mock_dnr, get_ft as mock_ft:
        meta_data = si._extract_meta_data(input_row)
    actual_label_text = meta_data.get("label_text")
    mock_dnr.assert_called_once_with(input_row)
    mock_ft.assert_called_once_with(input_row)
    assert actual_label_text == expect_label_text


@pytest.mark.parametrize(
    "input_ft,input_dnr,expect_meta_data",
    [
        ({"nothing": "here"}, {"nothing_to": "see"}, {}),
        ({}, {"unit_code": "SIA"}, {"unit_code": "SIA"}),
        (
            {},
            {"data_source": "Smithsonian Institution Archives"},
            {"data_source": "Smithsonian Institution Archives"},
        ),
    ],
)
def test_extract_meta_data_dnr_fields(input_ft, input_dnr, expect_meta_data):
    input_row = {"test": "row"}
    get_dnr = patch.object(
        si, "_get_descriptive_non_repeating_dict", return_value=input_dnr
    )
    get_ft = patch.object(si, "_get_freetext_dict", return_value=input_ft)
    with get_dnr as mock_dnr, get_ft as mock_ft:
        actual_meta_data = si._extract_meta_data(input_row)
    mock_dnr.assert_called_once_with(input_row)
    mock_ft.assert_called_once_with(input_row)
    assert actual_meta_data == expect_meta_data


@pytest.mark.parametrize(
    "input_is,expect_tags",
    [
        ({}, []),
        ({"nothing": "here"}, []),
        (
            {
                "date": ["", ""],
                "place": ["Indian Ocean"],
            },
            ["Indian Ocean"],
        ),
        (
            {
                "date": ["2000s"],
                "object_type": ["Holotypes", "Taxonomic type specimens"],
                "topic": ["Paleogeneral", "Protists"],
                "place": ["Indian Ocean"],
            },
            [
                "2000s",
                "Holotypes",
                "Taxonomic type specimens",
                "Paleogeneral",
                "Protists",
                "Indian Ocean",
            ],
        ),
    ],
)
def test_extract_tags(input_is, expect_tags):
    input_row = {"test": "row"}
    get_is = patch.object(si, "_get_indexed_structured_dict", return_value=input_is)
    with get_is as mock_is:
        actual_tags = si._extract_tags(input_row)
    mock_is.assert_called_once_with(input_row)
    assert actual_tags == expect_tags


@pytest.mark.parametrize(
    "input_row,expect_dnr_dict",
    [
        ({}, {}),
        ({"content": {"key": {"key2", "val2"}}}, {}),
        ({"noncontent": {"descriptiveNonRepeating": {"key2": "val2"}}}, {}),
        ({"content": {"descriptiveNonRepeating": {"key2": "val2"}}}, {"key2": "val2"}),
    ],
)
def test_get_descriptive_non_repeating_dict(input_row, expect_dnr_dict):
    actual_dnr_dict = si._get_descriptive_non_repeating_dict(input_row)
    assert actual_dnr_dict == expect_dnr_dict


@pytest.mark.parametrize(
    "input_row,expect_ind_struc_dict",
    [
        ({}, {}),
        ({"content": {"key": {"key2", "val2"}}}, {}),
        ({"noncontent": {"indexedStructured": {"key2": "val2"}}}, {}),
        ({"content": {"indexedStructured": {"key2": "val2"}}}, {"key2": "val2"}),
    ],
)
def test_get_indexed_structured_dict(input_row, expect_ind_struc_dict):
    actual_ind_struc_dict = si._get_indexed_structured_dict(input_row)
    assert actual_ind_struc_dict == expect_ind_struc_dict


@pytest.mark.parametrize(
    "input_row,expect_freetext_dict",
    [
        ({}, {}),
        ({"content": {"key": {"key2", "val2"}}}, {}),
        ({"noncontent": {"freetext": {"key2": "val2"}}}, {}),
        ({"content": {"freetext": {"key2": "val2"}}}, {"key2": "val2"}),
    ],
)
def test_get_freetext_dict(input_row, expect_freetext_dict):
    actual_freetext_dict = si._get_freetext_dict(input_row)
    assert actual_freetext_dict == expect_freetext_dict


@pytest.mark.parametrize(
    "required_type,default_input",
    [
        (str, ""),
        (int, 0),
        (float, 0.0),
        (complex, 0j),
        (list, []),
        (tuple, ()),
        (dict, {}),
        (set, set()),
        (bool, False),
        (bytes, b""),
    ],
)
def test_check_type_with_defaults(required_type, default_input):
    assert si._check_type(default_input, required_type) == default_input


@pytest.mark.parametrize(
    "required_type,good_input",
    [
        (str, "abc"),
        (int, 5),
        (float, 1.2),
        (complex, 3 + 2j),
        (list, ["a", 2, 0, False]),
        (tuple, (1, 0, False)),
        (dict, {"key": "val", "f": False}),
        (set, {1, False, "abc"}),
        (bool, True),
        (bytes, b"abc"),
    ],
)
def test_check_type_with_truthy_good_inputs(required_type, good_input):
    assert si._check_type(good_input, required_type) == good_input


@pytest.mark.parametrize(
    "required_type,good_indices,default",
    [
        (str, (0, 1), ""),
        (int, (2, 3), 0),
        (float, (4, 5), 0.0),
        (complex, (6, 7), 0j),
        (list, (8, 9), []),
        (tuple, (10, 11), ()),
        (dict, (12, 13), {}),
        (set, (14, 15), set()),
        (bool, (16, 17), False),
        (bytes, (18, 19), b""),
    ],
)
def test_check_type_with_bad_inputs(required_type, good_indices, default):
    bad_input_list = [
        "abc",
        "",
        5,
        0,
        1.2,
        0.0,
        3 + 2j,
        0j,
        ["a", 2],
        [],
        (1, 2),
        (),
        {"key": "val"},
        {},
        {1, "abc"},
        set(),
        True,
        False,
        b"abc",
        b"",
    ]
    for i in sorted(good_indices, reverse=True):
        del bad_input_list[i]
    for bad_input in bad_input_list:
        assert si._check_type(bad_input, required_type) == default


@pytest.mark.parametrize(
    "input_media,expect_calls",
    [
        ([], []),
        (
            [
                {
                    "thumbnail": "https://thumbnail.one",
                    "idsId": "id_one",
                    "usage": {"access": "CC0"},
                    "guid": "http://gu.id.one",
                    "type": "Images",
                    "content": "https://image.url.one",
                },
                {
                    "thumbnail": "https://thumbnail.two",
                    "idsId": "id_two",
                    "usage": {"access": "CC0"},
                    "guid": "http://gu.id.two",
                    "type": "Images",
                    "content": "https://image.url.two",
                },
            ],
            [
                call(
                    foreign_landing_url="https://foreignlanding.url",
                    image_url="https://image.url.one",
                    thumbnail_url="https://thumbnail.one",
                    license_info=LicenseInfo(
                        "cc0",
                        "1.0",
                        "https://creativecommons.org/publicdomain/zero/1.0/",
                        "https://license.url",
                    ),
                    foreign_identifier="id_one",
                    title="The Title",
                    creator="Alice",
                    meta_data={"unit_code": "NMNHBOTANY"},
                    raw_tags=["tag", "list"],
                    source="smithsonian_national_museum_of_natural_history",
                ),
                call(
                    foreign_landing_url="https://foreignlanding.url",
                    image_url="https://image.url.two",
                    thumbnail_url="https://thumbnail.two",
                    license_info=LicenseInfo(
                        "cc0",
                        "1.0",
                        "https://creativecommons.org/publicdomain/zero/1.0/",
                        "https://license.url",
                    ),
                    foreign_identifier="id_two",
                    title="The Title",
                    creator="Alice",
                    meta_data={"unit_code": "NMNHBOTANY"},
                    raw_tags=["tag", "list"],
                    source="smithsonian_national_museum_of_natural_history",
                ),
            ],
        ),
        (
            [
                {
                    "thumbnail": "https://thumbnail.one",
                    "idsId": "id_one",
                    "usage": {"access": "CC-BY"},
                    "guid": "http://gu.id.one",
                    "type": "Images",
                    "content": "https://image.url.one",
                },
                {
                    "thumbnail": "https://thumbnail.two",
                    "idsId": "id_two",
                    "usage": {"access": "CC0"},
                    "guid": "http://gu.id.two",
                    "type": "Images",
                    "content": "https://image.url.two",
                },
            ],
            [
                call(
                    foreign_landing_url="https://foreignlanding.url",
                    image_url="https://image.url.two",
                    thumbnail_url="https://thumbnail.two",
                    license_info=LicenseInfo(
                        "cc0",
                        "1.0",
                        "https://creativecommons.org/publicdomain/zero/1.0/",
                        "https://license.url",
                    ),
                    foreign_identifier="id_two",
                    title="The Title",
                    creator="Alice",
                    meta_data={"unit_code": "NMNHBOTANY"},
                    raw_tags=["tag", "list"],
                    source="smithsonian_national_museum_of_natural_history",
                )
            ],
        ),
        (
            [
                {
                    "thumbnail": "https://thumbnail.one",
                    "idsId": "id_one",
                    "usage": {"access": "CC0"},
                    "guid": "http://gu.id.one",
                    "type": "Images",
                    "content": "https://image.url.one",
                },
                {
                    "thumbnail": "https://thumbnail.two",
                    "idsId": "id_two",
                    "usage": {"access": "CC0"},
                    "guid": "http://gu.id.two",
                    "type": "Audio",
                    "content": "https://image.url.two",
                },
            ],
            [
                call(
                    foreign_landing_url="https://foreignlanding.url",
                    image_url="https://image.url.one",
                    thumbnail_url="https://thumbnail.one",
                    license_info=LicenseInfo(
                        "cc0",
                        "1.0",
                        "https://creativecommons.org/publicdomain/zero/1.0/",
                        "https://license.url",
                    ),
                    foreign_identifier="id_one",
                    title="The Title",
                    creator="Alice",
                    meta_data={"unit_code": "NMNHBOTANY"},
                    raw_tags=["tag", "list"],
                    source="smithsonian_national_museum_of_natural_history",
                )
            ],
        ),
    ],
)
def test_process_image_list(input_media, expect_calls):
    with patch.object(si.image_store, "add_item", return_value=10) as mock_add_item:
        si._process_image_list(
            input_media,
            foreign_landing_url="https://foreignlanding.url",
            title="The Title",
            creator="Alice",
            meta_data={"unit_code": "NMNHBOTANY"},
            tags=["tag", "list"],
            source="smithsonian_national_museum_of_natural_history",
            license_url="https://license.url",
        )
    assert expect_calls == mock_add_item.mock_calls


def test_process_image_data_with_sub_provider():
    response = _get_resource_json("sub_provider_example.json")
    with patch.object(si.image_store, "add_item", return_value=100) as mock_add_item:
        total_images = si._process_response_json(response)

    expect_meta_data = {
        "unit_code": "SIA",
        "data_source": "Smithsonian Institution Archives",
    }

    mock_add_item.assert_called_once_with(
        foreign_landing_url=None,
        image_url="https://ids.si.edu/ids/deliveryService?id=SIA-SIA2010-2358",
        thumbnail_url=(
            "https://ids.si.edu/ids/deliveryService?id=SIA-SIA2010-" "2358&max=150"
        ),
        license_info=(
            LicenseInfo(
                "cc0",
                "1.0",
                "https://creativecommons.org/publicdomain/zero/1.0/",
                "https://creativecommons.org/publicdomain/zero/1.0/",
            )
        ),
        foreign_identifier="SIA-SIA2010-2358",
        creator="Gruber, Martin A",
        title=(
            "Views of the National Zoological Park in Washington, DC, "
            "showing Elephant"
        ),
        meta_data=expect_meta_data,
        raw_tags=["1920s", "1910s", "Archival materials", "Photographs", "Animals"],
        source="smithsonian_institution_archives",
    )
    assert total_images == 100
