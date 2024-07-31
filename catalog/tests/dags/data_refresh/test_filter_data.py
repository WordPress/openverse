from unittest import mock

import pytest

from data_refresh.filter_data import (
    DEFAULT_BATCH_SIZE,
    FILTERED_TAG_PROVIDERS,
    filter_data_batch,
    generate_tag_updates,
    get_filter_batches,
)


@pytest.mark.parametrize(
    "tags, expected",
    [
        # Valid tag returns no updates
        ([{"name": "valid", "accuracy": 0.92}], None),
        # Denylisted tags get filtered
        (
            [
                {"name": "cc0"},
                {"name": " cc0"},
                {"name": "valid", "accuracy": 0.99},
                {"name": "valid_no_accuracy"},
                {
                    "name": "garbage:=metacrap",
                },
            ],
            [
                {"name": "valid", "accuracy": 0.99},
                {"name": "valid_no_accuracy"},
            ],
        ),
        # Inaccurate tags are filtered
        (
            [
                {"name": "inaccurate", "accuracy": 0.5},
                {"name": "accurate", "accuracy": 0.999},
            ],
            [{"name": "accurate", "accuracy": 0.999}],
        ),
        # Tags from unvetted providers get filtered
        (
            [
                {"name": "valid", "provider": "provider1"},
                *[
                    {"name": "invalid", "provider": provider}
                    for provider in FILTERED_TAG_PROVIDERS
                ],
            ],
            [{"name": "valid", "provider": "provider1"}],
        ),
    ],
)
def test_generate_tag_updates(tags, expected):
    actual = generate_tag_updates(tags)
    assert actual == expected


@pytest.mark.parametrize(
    "id_bounds, batch_size, expected",
    [
        ((1, 100), 50, [(1, 50), (51, 100)]),
        # None respects default
        ((1, 100), None, [(1, DEFAULT_BATCH_SIZE)]),
    ],
)
def test_get_filter_batches(id_bounds, batch_size, expected):
    actual = get_filter_batches.function(id_bounds, batch_size)
    assert actual == expected


def test_filter_data_batch():
    batch = (50, 100)
    temp_table = "temp_foobar"
    postgres_conn_id = "fake_conn_id"
    sample_data = [
        (50, "aaa", False),
        (51, "bbb", True),
        (52, "ccc", False),
    ]
    with mock.patch("data_refresh.filter_data.PostgresHook") as HookMock, mock.patch(
        "data_refresh.filter_data.generate_tag_updates"
    ) as tag_updates_mock:
        mock_pg = HookMock.return_value
        mock_pg.run.return_value = sample_data
        mock_cursor = (
            mock_pg.get_conn.return_value.cursor.return_value.__enter__.return_value
        )
        tag_updates_mock.side_effect = lambda x: x or None

        count = filter_data_batch.function(
            batch=batch, temp_table=temp_table, postgres_conn_id=postgres_conn_id
        )

        assert count == 1
        assert mock_cursor.execute.call_count == 1
        assert "BETWEEN 50 AND 100" in mock_pg.run.call_args.args[0]
