import json
import logging
from itertools import pairwise
from types import SimpleNamespace
from unittest import mock

import psycopg2
import pytest

from data_refresh.alter_data import (
    FILTERED_TAG_PROVIDERS,
    alter_data_range,
    get_alter_ranges,
    get_batches,
    get_progress_variable,
)
from tests.test_utils import sql
from tests.test_utils.variable import FakeVariable


PROGRESS_PREFIX = "test_alter_data_progress"
PROGRESS_VARIABLE = get_progress_variable(PROGRESS_PREFIX, 0)


@pytest.fixture(autouse=True)
def fake_variable():
    FakeVariable.values = {}
    with mock.patch("data_refresh.alter_data.Variable", FakeVariable):
        yield FakeVariable


@pytest.fixture
def temp_table(identifier):
    table = f"temp_import_{identifier}"
    conn = psycopg2.connect(sql.POSTGRES_TEST_URI)
    cur = conn.cursor()
    cur.execute(f"DROP TABLE IF EXISTS {table}")
    cur.execute(
        f"CREATE TABLE {table} (id integer PRIMARY KEY, identifier text, tags jsonb)"
    )
    conn.commit()

    yield sql.PostgresRef(cursor=cur, connection=conn), table

    cur.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    cur.close()
    conn.close()


def _insert(postgres, table, rows: dict[int, object]):
    for _id, tags in rows.items():
        postgres.cursor.execute(
            f"INSERT INTO {table} (id, identifier, tags) VALUES (%s, %s, %s)",
            (_id, f"identifier-{_id}", None if tags is None else json.dumps(tags)),
        )
    postgres.connection.commit()


def _tags_by_id(postgres, table) -> dict[int, object]:
    postgres.cursor.execute(f"SELECT id, tags FROM {table} ORDER BY id")
    return dict(postgres.cursor.fetchall())


def _alter(table, id_range, batch_size=None):
    return alter_data_range.function(
        id_range=id_range,
        batch_size=batch_size,
        temp_table=table,
        postgres_conn_id=sql.POSTGRES_CONN_ID,
        progress_prefix=PROGRESS_PREFIX,
        ti=SimpleNamespace(map_index=0),
    )


@pytest.mark.parametrize(
    "tags, expected",
    [
        pytest.param(
            [{"name": "valid", "accuracy": 0.92}],
            [{"name": "valid", "accuracy": 0.92}],
            id="valid_tag_kept",
        ),
        pytest.param(
            [
                {"name": "cc0"},
                {"name": " cc0"},
                {"name": "valid", "accuracy": 0.99},
                {"name": "valid_no_accuracy"},
                {"name": "garbage:=metacrap"},
            ],
            [{"name": "valid", "accuracy": 0.99}, {"name": "valid_no_accuracy"}],
            id="denylisted_and_contains_denylisted",
        ),
        pytest.param(
            [
                {"name": "undefined"},
                {"name": "Creative Commons license"},
                {"name": "public domain"},
                {"name": "domain"},
            ],
            [{"name": "domain"}],
            id="ingestion_denylists",
        ),
        pytest.param(
            [{"name": "By"}, {"name": "bypass"}, {"name": "CC-BY-NC"}],
            [{"name": "bypass"}],
            id="case_insensitive_exact_and_contains",
        ),
        pytest.param(
            [
                {"name": "inaccurate", "accuracy": 0.5},
                {"name": "inaccurate_string", "accuracy": "0.5"},
                {"name": "accurate", "accuracy": 0.999},
                {"name": "threshold", "accuracy": 0.9},
                {"name": "null_accuracy", "accuracy": None},
            ],
            [
                {"name": "accurate", "accuracy": 0.999},
                {"name": "threshold", "accuracy": 0.9},
                {"name": "null_accuracy", "accuracy": None},
            ],
            id="low_accuracy",
        ),
        pytest.param(
            [
                {"name": "word_accuracy", "accuracy": "high"},
                {"name": "comma_accuracy", "accuracy": "0,95"},
                {"accuracy": "high"},
                {"name": "padded_accuracy", "accuracy": " 0.95 "},
                {"name": "exponent_accuracy", "accuracy": "9.5e-1"},
            ],
            [
                {"name": "padded_accuracy", "accuracy": " 0.95 "},
                {"name": "exponent_accuracy", "accuracy": "9.5e-1"},
            ],
            id="non_numeric_string_accuracy",
        ),
        pytest.param(
            [
                {"name": "valid", "provider": "provider1"},
                {"name": "no_provider", "provider": None},
                *[
                    {"name": "invalid", "provider": provider}
                    for provider in FILTERED_TAG_PROVIDERS
                ],
            ],
            [
                {"name": "valid", "provider": "provider1"},
                {"name": "no_provider", "provider": None},
            ],
            id="filtered_providers",
        ),
        pytest.param(
            [{"accuracy": 0.99}, {"name": 5}, {"name": None}, "bare", {"name": "ok"}],
            [{"name": "ok"}],
            id="malformed",
        ),
        pytest.param(
            [{"name": "cc0"}, {"name": "squareformat"}],
            [],
            id="all_tags_filtered",
        ),
        pytest.param(
            [{"name": "b"}, {"name": "uploaded"}, {"name": "a"}, {"name": "c"}],
            [{"name": "b"}, {"name": "a"}, {"name": "c"}],
            id="order_preserved",
        ),
        pytest.param(None, None, id="null_tags"),
        pytest.param([], [], id="empty_tags"),
        pytest.param({"name": "cc0"}, {"name": "cc0"}, id="non_array_tags"),
    ],
)
def test_alter_data_range_filters_tags(temp_table, tags, expected):
    postgres, table = temp_table
    _insert(postgres, table, {1: tags})

    count = _alter(table, (1, 1))

    assert _tags_by_id(postgres, table) == {1: expected}
    assert count == (0 if tags == expected else 1)


def test_alter_data_range_only_updates_rows_in_range(temp_table):
    postgres, table = temp_table
    bad, good = [{"name": "cc0"}, {"name": "cat"}], [{"name": "cat"}]
    _insert(postgres, table, {1: bad, 2: bad, 3: good, 4: bad})

    count = _alter(table, (2, 3))

    assert count == 1
    assert _tags_by_id(postgres, table) == {1: bad, 2: good, 3: good, 4: bad}


@pytest.mark.parametrize("batch_size", [1, 2, 10])
def test_alter_data_range_updates_every_batch(temp_table, batch_size):
    postgres, table = temp_table
    bad, good = [{"name": "cc0"}, {"name": "cat"}], [{"name": "cat"}]
    _insert(postgres, table, {_id: bad for _id in range(1, 6)})

    count = _alter(table, (1, 5), batch_size)

    assert count == 5
    assert _tags_by_id(postgres, table) == {_id: good for _id in range(1, 6)}


def test_alter_data_range_resumes_after_a_failed_batch(temp_table, fake_variable):
    postgres, table = temp_table
    bad, good = [{"name": "cc0"}, {"name": "cat"}], [{"name": "cat"}]
    _insert(postgres, table, {_id: bad for _id in range(1, 6)})

    real_set, calls = fake_variable.set, []

    def fail_on_second_batch(*args, **kwargs):
        real_set(*args, **kwargs)
        calls.append(args)
        if len(calls) == 2:
            raise RuntimeError("The database went away")

    with mock.patch.object(fake_variable, "set", fail_on_second_batch):
        with pytest.raises(RuntimeError):
            _alter(table, (1, 5), batch_size=2)

    assert fake_variable.get(PROGRESS_VARIABLE, deserialize_json=True) == {
        "next_start": 5,
        "altered": 4,
    }
    # Make a committed row look unaltered, to show that the retry skips it
    postgres.cursor.execute(
        f"UPDATE {table} SET tags = %s WHERE id = 1", (json.dumps(bad),)
    )
    postgres.connection.commit()

    count = _alter(table, (1, 5), batch_size=2)

    assert count == 5
    assert _tags_by_id(postgres, table) == {
        1: bad,
        **{_id: good for _id in range(2, 6)},
    }
    assert PROGRESS_VARIABLE not in fake_variable.values


def test_alter_data_range_logs_altered_identifiers(temp_table, caplog):
    postgres, table = temp_table
    _insert(postgres, table, {1: [{"name": "cc0"}], 2: [{"name": "cat"}]})

    with caplog.at_level(logging.DEBUG, logger="data_refresh.alter_data"):
        _alter(table, (1, 2))

    assert "Filtered tags for identifier-1" in caplog.text
    assert "identifier-2" not in caplog.text


@pytest.mark.parametrize(
    "id_bounds, range_count, expected",
    [
        ((1, 100), 2, [(1, 50), (51, 100)]),
        ((1, 101), 2, [(1, 51), (52, 101)]),
        ((1, 10), 3, [(1, 4), (5, 8), (9, 10)]),
        # Never more ranges than ids
        ((7, 8), 8, [(7, 7), (8, 8)]),
        ((7, 7), 8, [(7, 7)]),
        # An empty table has no id bounds
        ((None, None), 8, []),
    ],
)
def test_get_alter_ranges(id_bounds, range_count, expected):
    assert (
        get_alter_ranges.function(id_bounds, PROGRESS_PREFIX, range_count) == expected
    )


def test_get_alter_ranges_stays_under_map_length():
    ranges = get_alter_ranges.function((1, 947_411_826), PROGRESS_PREFIX)

    assert len(ranges) == 8
    assert ranges[0][0] == 1
    assert ranges[-1][1] == 947_411_826
    assert all(end + 1 == start for (_, end), (start, _) in pairwise(ranges))


def test_get_alter_ranges_drops_earlier_progress(fake_variable):
    fake_variable.set(PROGRESS_VARIABLE, {"next_start": 50}, serialize_json=True)

    get_alter_ranges.function((1, 100), PROGRESS_PREFIX)

    assert fake_variable.values == {}


@pytest.mark.parametrize(
    "id_range, batch_size, expected",
    [
        ((1, 100), 50, [(1, 50), (51, 100)]),
        ((1, 101), 50, [(1, 50), (51, 100), (101, 101)]),
        ((7, 7), 50, [(7, 7)]),
    ],
)
def test_get_batches(id_range, batch_size, expected):
    assert get_batches(id_range, batch_size) == expected
