from unittest.mock import patch

import pytest
from airflow.exceptions import AirflowException

from catalog.tests.dags.providers.provider_api_scripts.resources.json_load import (
    make_resource_json_func,
)
from providers.provider_api_scripts.smithsonian import SmithsonianDataIngester


# Set up test class
ingester = SmithsonianDataIngester()
_get_resource_json = make_resource_json_func("smithsonian")


def test_get_hash_prefixes_with_len_one():
    with patch.object(ingester, "hash_prefix_length", 1):
        actual_prefix_list = list(ingester._get_hash_prefixes())
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
    assert actual_prefix_list == expect_prefix_list


def test_alert_new_unit_codes():
    sub_prov_dict = {"sub_prov1": {"a", "c"}, "sub_prov2": {"b"}, "sub_prov3": {"e"}}
    unit_code_set = {"a", "b", "c", "d"}
    with patch.dict(ingester.sub_providers, sub_prov_dict, clear=True):
        actual_codes = ingester._get_new_and_outdated_unit_codes(unit_code_set)
    expected_codes = ({"d"}, {"e"})
    assert actual_codes == expected_codes


@pytest.mark.parametrize(
    "new_unit_codes, outdated_unit_codes",
    [
        ({"d"}, {"e"}),
        ({"d"}, set()),
        (set(), {"e"}),
    ],
)
def test_validate_unit_codes_from_api_raises_exception(
    new_unit_codes, outdated_unit_codes
):
    with patch.object(ingester, "_get_unit_codes_from_api"), patch.object(
        ingester,
        "_get_new_and_outdated_unit_codes",
        return_value=(new_unit_codes, outdated_unit_codes),
    ):
        message = "^\n\\*Updates needed to the SMITHSONIAN_SUB_PROVIDERS dictionary\\**"
        with pytest.raises(AirflowException, match=message):
            ingester.validate_unit_codes_from_api()


def test_validate_unit_codes_from_api():
    with patch.object(ingester, "_get_unit_codes_from_api"), patch.object(
        ingester, "_get_new_and_outdated_unit_codes", return_value=(set(), set())
    ):
        # Validation should run without raising an exception
        ingester.validate_unit_codes_from_api()


@pytest.mark.parametrize(
    "input_int, expect_len, expect_first, expect_last",
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
    with patch.object(ingester, "hash_prefix_length", input_int):
        actual_list = list(ingester._get_hash_prefixes())

    assert all("0x" not in h for h in actual_list)
    assert all(
        int(actual_list[i + 1], 16) - int(actual_list[i], 16) == 1
        for i in range(len(actual_list) - 1)
    )
    assert len(actual_list) == expect_len
    assert actual_list[0] == expect_first
    assert actual_list[-1] == expect_last


def test_get_next_query_params_first_call():
    hash_prefix = "ff"
    actual_params = ingester.get_next_query_params(
        prev_query_params=None, hash_prefix=hash_prefix
    )
    actual_params.pop("api_key")  # Omitting the API key
    expected_params = {
        "q": f"online_media_type:Images AND media_usage:CC0 AND hash:{hash_prefix}*",
        "start": 0,
        "rows": 1000,
    }
    assert actual_params == expected_params


def test_get_next_query_params_updates_parameters():
    previous_query_params = {
        "api_key": "pass123",
        "q": "online_media_type:Images AND media_usage:CC0 AND hash:ff*",
        "start": 0,
        "rows": 1000,
    }
    actual_params = ingester.get_next_query_params(previous_query_params)
    expected_params = {
        "api_key": "pass123",
        "q": "online_media_type:Images AND media_usage:CC0 AND hash:ff*",
        "start": 1000,
        "rows": 1000,
    }
    assert actual_params == expected_params


@pytest.mark.parametrize(
    "input_row, field, expected_dict",
    [
        # field: descriptiveNonRepeating
        ({}, "descriptiveNonRepeating", {}),
        ({"content": {"key": {"key2", "val2"}}}, "descriptiveNonRepeating", {}),
        (
            {"noncontent": {"descriptiveNonRepeating": {"key2": "val2"}}},
            "descriptiveNonRepeating",
            {},
        ),
        (
            {"content": {"descriptiveNonRepeating": {"key2": "val2"}}},
            "descriptiveNonRepeating",
            {"key2": "val2"},
        ),
        # field: indexedStructured
        ({}, "indexedStructured", {}),
        ({"content": {"key": {"key2", "val2"}}}, "indexedStructured", {}),
        (
            {"noncontent": {"indexedStructured": {"key2": "val2"}}},
            "indexedStructured",
            {},
        ),
        (
            {"content": {"indexedStructured": {"key2": "val2"}}},
            "indexedStructured",
            {"key2": "val2"},
        ),
        # field: freetext
        ({}, "freetext", {}),
        ({"content": {"key": {"key2", "val2"}}}, "freetext", {}),
        ({"noncontent": {"freetext": {"key2": "val2"}}}, "freetext", {}),
        ({"content": {"freetext": {"key2": "val2"}}}, "freetext", {"key2": "val2"}),
    ],
)
def test_content_dict(input_row, field, expected_dict):
    actual_dict = ingester._get_content_dict(input_row, field)
    assert actual_dict == expected_dict


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
    assert ingester._check_type(default_input, required_type) == default_input


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
    assert ingester._check_type(good_input, required_type) == good_input


@pytest.mark.parametrize(
    "required_type,good_indices,default",
    [
        (str, (0, 1), ""),
        (int, (2, 3, 16), 0),  # Boolean value is treated as an int
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
        assert ingester._check_type(bad_input, required_type) == default


@pytest.mark.parametrize(
    "input_dnr, expect_image_list",
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
        ingester, "_get_content_dict", return_value=input_dnr
    ) as mock_dnr:
        actual_image_list = ingester._get_image_list(input_row)
    mock_dnr.assert_called_once_with(input_row, "descriptiveNonRepeating")
    assert actual_image_list == expect_image_list


def test_get_media_type():
    actual_type = ingester.get_media_type(record={})
    assert actual_type == "image"


@pytest.mark.parametrize(
    "input_dnr, expect_foreign_landing_url",
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
        ingester, "_get_content_dict", return_value=input_dnr
    ) as mock_dnr:
        actual_foreign_landing_url = ingester._get_foreign_landing_url(input_row)
    mock_dnr.assert_called_once_with(input_row, "descriptiveNonRepeating")
    assert actual_foreign_landing_url == expect_foreign_landing_url


@pytest.mark.parametrize(
    "input_is, input_ft, expected_creator",
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
def test_get_creator(input_is, input_ft, expected_creator):
    creator_types = {"creator": 0, "designer": 1, "after": 3}
    input_row = {
        "test": "row",
        "content": {"freetext": input_ft, "indexedStructured": input_is},
    }
    with patch.object(ingester, "creator_types", creator_types):
        actual_creator = ingester._get_creator(input_row)

    assert actual_creator == expected_creator


@pytest.mark.parametrize(
    "input_ft, input_dnr, expected_description",
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
def test_ext_meta_data_description(input_ft, input_dnr, expected_description):
    description_types = {"description", "summary"}
    input_row = {
        "test": "row",
        "content": {"freetext": input_ft, "descriptiveNonRepeating": input_dnr},
    }
    with patch.object(ingester, "description_types", description_types):
        meta_data = ingester._extract_meta_data(input_row)
    actual_description = meta_data.get("description")

    assert actual_description == expected_description


@pytest.mark.parametrize(
    "input_ft, input_dnr, expected_label_text",
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
def test_ext_meta_data_label_text(input_ft, input_dnr, expected_label_text):
    input_row = {
        "test": "row",
        "content": {"freetext": input_ft, "descriptiveNonRepeating": input_dnr},
    }
    meta_data = ingester._extract_meta_data(input_row)
    actual_label_text = meta_data.get("label_text")

    assert actual_label_text == expected_label_text


@pytest.mark.parametrize(
    "input_ft, input_dnr, expected_meta_data",
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
def test_extract_meta_data_dnr_fields(input_ft, input_dnr, expected_meta_data):
    input_row = {
        "test": "row",
        "content": {"freetext": input_ft, "descriptiveNonRepeating": input_dnr},
    }
    actual_meta_data = ingester._extract_meta_data(input_row)

    assert actual_meta_data == expected_meta_data


@pytest.mark.parametrize(
    "input_is, expect_tags",
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
    get_is = patch.object(ingester, "_get_content_dict", return_value=input_is)
    with get_is as mock_is:
        actual_tags = ingester._extract_tags(input_row)
    mock_is.assert_called_once_with(input_row, "indexedStructured")
    assert actual_tags == expect_tags


@pytest.mark.parametrize(
    "input_media, expected_image_data",
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
                    "content": "",
                },
            ],
            [],
        ),
        (
            [
                {
                    "thumbnail": "https://thumbnail.one",
                    "idsId": "",
                    "usage": {"access": "CC0"},
                    "guid": "http://gu.id.one",
                    "type": "Images",
                    "content": "https://image.url.one",
                }
            ],
            [],
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
                    "type": "Images",
                    "content": "https://image.url.two",
                },
            ],
            [
                {
                    "foreign_identifier": "id_one",
                    "url": "https://image.url.one",
                },
                {
                    "foreign_identifier": "id_two",
                    "url": "https://image.url.two",
                },
            ],
        ),
    ],
)
def test_process_image_list(input_media, expected_image_data):
    shared_image_data = {
        "foreign_landing_url": "https://foreignlanding.url",
        "title": "The Title",
        "license_info": ingester.license_info,
        "creator": "Alice",
        "meta_data": {"unit_code": "NMNHBOTANY"},
        "source": "smithsonian_national_museum_of_natural_history",
        "raw_tags": ["tag", "list"],
    }
    expected_result = [(img | shared_image_data) for img in expected_image_data]
    actual_image_data = ingester._get_associated_images(input_media, shared_image_data)
    assert actual_image_data == expected_result


def test_get_record_data():
    data = _get_resource_json("actual_record_data.json")
    actual_data = ingester.get_record_data(data)
    expected_data = [
        {
            "url": "https://collections.nmnh.si.edu/media/?irn=15814382",
            "foreign_identifier": "https://collections.nmnh.si.edu/media/?irn=15814382",
            "foreign_landing_url": "http://n2t.net/ark:/65665/34857ca78-9195-4156-849b-1ec47f7cd1ce",
            "title": "Passerculus sandwichensis nevadensis",
            "license_info": ingester.license_info,
            "source": "smithsonian_national_museum_of_natural_history",
            "creator": "Seymour H. Levy",
            "meta_data": {
                "unit_code": "NMNHBIRDS",
                "data_source": "NMNH - Vertebrate Zoology - Birds Division",
            },
            "raw_tags": [
                "1950s",
                "Animals",
                "Birds",
                "United States",
                "Pinal",
                "North America",
                "Arizona",
            ],
        }
    ]

    assert actual_data == expected_data
