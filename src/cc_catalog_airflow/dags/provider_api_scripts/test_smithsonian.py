import json
import logging
import os
from unittest.mock import patch, call

import pytest

import smithsonian as si

logger = logging.getLogger(__name__)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.DEBUG
)

RESOURCES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'tests/resources/smithsonian'
)


def test_get_hash_prefixes_with_len_one():
    expect_prefix_list = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd',
        'e', 'f'
    ]
    actual_prefix_list = list(si._get_hash_prefixes(1))
    assert actual_prefix_list == expect_prefix_list


@pytest.mark.parametrize(
    "input_int,expect_len,expect_first,expect_last",
    [
        (1, 16, '0', 'f'),
        (2, 256, '00', 'ff'),
        (3, 4096, '000', 'fff'),
        (4, 65536, '0000', 'ffff'),
    ],
)
def test_get_hash_prefixes_with_other_len(
        input_int,
        expect_len,
        expect_first,
        expect_last
):
    actual_list = list(si._get_hash_prefixes(input_int))
    assert all('0x' not in h for h in actual_list)
    assert all(
        int(actual_list[i + 1], 16) - int(actual_list[i], 16) == 1
        for i in range(len(actual_list) - 1)
    )
    assert len(actual_list) == expect_len
    assert actual_list[0] == expect_first
    assert actual_list[-1] == expect_last


def test_process_hash_prefix_with_none_response_json():
    endpoint = 'https://abc.com/123'
    limit = 100
    hash_prefix = '00'
    retries = 3
    qp = {'q': 'abc'}

    patch_get_response_json = patch.object(
        si.delayed_requester,
        'get_response_json',
        return_value=None
    )
    patch_build_qp = patch.object(
        si,
        '_build_query_params',
        return_value=qp
    )
    patch_process_response = patch.object(
        si,
        '_process_response_json'
    )
    with\
            patch_get_response_json as mock_get_response_json,\
            patch_build_qp as mock_build_qp,\
            patch_process_response as mock_process_response:
        si._process_hash_prefix(
            hash_prefix,
            endpoint=endpoint,
            limit=limit,
            retries=retries
        )
    mock_process_response.assert_not_called()
    mock_build_qp.assert_called_once_with(0, hash_prefix=hash_prefix)
    mock_get_response_json.assert_called_once_with(
        endpoint,
        retries=retries,
        query_params=qp
    )


def test_process_hash_prefix_with_response_json_no_row_count():
    endpoint = 'https://abc.com/123'
    limit = 100
    hash_prefix = '00'
    retries = 3
    qp = {'q': 'abc'}
    response_json = {'abc': '123'}

    patch_get_response_json = patch.object(
        si.delayed_requester,
        'get_response_json',
        return_value=response_json
    )
    patch_build_qp = patch.object(
        si,
        '_build_query_params',
        return_value=qp
    )
    patch_process_response = patch.object(
        si,
        '_process_response_json'
    )
    with\
            patch_get_response_json as mock_get_response_json,\
            patch_build_qp as mock_build_qp,\
            patch_process_response as mock_process_response:
        si._process_hash_prefix(
            hash_prefix,
            endpoint=endpoint,
            limit=limit,
            retries=retries
        )
    mock_process_response.assert_called_with(response_json)
    mock_build_qp.assert_called_once_with(0, hash_prefix=hash_prefix)
    mock_get_response_json.assert_called_once_with(
        endpoint,
        retries=retries,
        query_params=qp
    )


def test_process_hash_prefix_with_good_response_json():
    endpoint = 'https://abc.com/123'
    limit = 100
    hash_prefix = '00'
    retries = 3
    qp = {'q': 'abc'}
    response_json = {
        'response': {
            'abc': '123',
            'rowCount': 150
        }
    }

    patch_get_response_json = patch.object(
        si.delayed_requester,
        'get_response_json',
        return_value=response_json
    )
    patch_build_qp = patch.object(
        si,
        '_build_query_params',
        return_value=qp
    )
    patch_process_response = patch.object(
        si,
        '_process_response_json',
        return_value=0
    )
    with\
            patch_build_qp as mock_build_qp,\
            patch_get_response_json as mock_get_response_json,\
            patch_process_response as mock_process_response:
        si._process_hash_prefix(
            hash_prefix,
            endpoint=endpoint,
            limit=limit,
            retries=retries
        )
    expect_process_response_calls = [call(response_json), call(response_json)]
    expect_build_qp_calls = [
        call(0, hash_prefix=hash_prefix),
        call(limit, hash_prefix=hash_prefix)
    ]
    expect_get_response_json_calls = [
        call(endpoint, retries=retries, query_params=qp),
        call(endpoint, retries=retries, query_params=qp)
    ]
    mock_build_qp.assert_has_calls(expect_build_qp_calls)
    mock_get_response_json.assert_has_calls(expect_get_response_json_calls)
    mock_process_response.assert_has_calls(expect_process_response_calls)


def test_build_query_params():
    hash_prefix = 'ff'
    row_offset = 10
    default_params = {
        'api_key': 'pass123',
        'rows': 10
    }
    acutal_params = si._build_query_params(
        row_offset,
        hash_prefix=hash_prefix,
        default_params=default_params
    )
    expect_params = {
        'api_key': 'pass123',
        'rows': 10,
        'q': f'online_media_type:Images AND media_usage:CC0 AND hash:{hash_prefix}*',
        'start': row_offset
    }
    assert acutal_params == expect_params
    assert default_params == {
        'api_key': 'pass123',
        'rows': 10
    }


def test_process_response_json_with_no_rows_json():
    response_json = {
        'status': 200,
        'responseCode': 1,
        'response': {
            'norows': ['abc', 'def'],
            'rowCount': 2,
            'message': 'content found'
        }
    }
    patch_process_image_list = patch.object(
        si,
        '_process_image_list',
        return_value=2
    )

    with patch_process_image_list as mock_process_image_list:
        si._process_response_json(response_json)

    mock_process_image_list.assert_not_called()


def test_process_response_json_uses_required_getters():
    """
    This test only checks for appropriate calls to getter functions
    """
    response_json = {'test key': 'test value'}
    row_list = ['row0', 'row1']
    image_lists = [['image', 'list', 'zero'], ['image', 'list', 'one']]
    flu_list = ['flu0', 'flu1']
    title_list = ['title0', 'title1']
    creator_list = ['creator0', 'creator1']
    metadata_list = ['metadata0', 'metadata1']
    tags_list = ['tags0', 'tags1']

    get_row_list = patch.object(si, '_get_row_list', return_value=row_list)
    process_image_list = patch.object(
        si, '_process_image_list', return_value=2
    )
    get_image_list = patch.object(
        si, '_get_image_list', side_effect=image_lists
    )
    get_flu = patch.object(
        si, '_get_foreign_landing_url', side_effect=flu_list
    )
    get_title = patch.object(si, '_get_title', side_effect=title_list)
    get_creator = patch.object(si, '_get_creator', side_effect=creator_list)
    ext_meta_data = patch.object(
        si, '_extract_meta_data', side_effect=metadata_list
    )
    ext_tags = patch.object(si, '_extract_tags', side_effect=tags_list)

    with\
            get_row_list as mock_get_row_list,\
            get_image_list as mock_get_image_list,\
            get_flu as mock_get_foreign_landing_url,\
            get_title as mock_get_title,\
            get_creator as mock_get_creator,\
            ext_meta_data as mock_extract_meta_data,\
            ext_tags as mock_extract_tags,\
            process_image_list as mock_process_image_list:
        si._process_response_json(response_json)

    getter_calls_list = [call(r) for r in row_list]
    image_processing_call_list = [
        call(
            image_lists[0],
            flu_list[0],
            title_list[0],
            creator_list[0],
            metadata_list[0],
            tags_list[0]
        ),
        call(
            image_lists[1],
            flu_list[1],
            title_list[1],
            creator_list[1],
            metadata_list[1],
            tags_list[1]
        )
    ]
    mock_get_row_list.assert_called_once_with(response_json)
    assert mock_process_image_list.mock_calls == image_processing_call_list
    assert mock_get_image_list.mock_calls == getter_calls_list
    assert mock_get_foreign_landing_url.mock_calls == getter_calls_list
    assert mock_get_title.mock_calls == getter_calls_list
    assert mock_get_creator.mock_calls == getter_calls_list
    assert mock_extract_meta_data.mock_calls == getter_calls_list
    assert mock_extract_tags.mock_calls == getter_calls_list


def test_get_row_list_with_no_rows():
    response_json = {'not': 'rows'}
    row_list = si._get_row_list(response_json)
    assert row_list == []
