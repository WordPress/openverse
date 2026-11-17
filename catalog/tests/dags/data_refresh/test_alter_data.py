import json

import psycopg2
import pytest

from data_refresh.alter_data import (
    DEFAULT_BATCH_SIZE,
    FILTERED_TAG_PROVIDERS,
    alter_data_batch,
    get_alter_batches,
)
from tests.test_utils import sql


@pytest.fixture
def temp_table(request):
    table = f"temp_import_{abs(hash(request.node.name))}"
    conn = psycopg2.connect(sql.POSTGRES_TEST_URI)
    cur = conn.cursor()
    cur.execute(f"DROP TABLE IF EXISTS {table}")
    cur.execute(f"CREATE TABLE {table} (id integer PRIMARY KEY, tags jsonb)")
    conn.commit()

    yield sql.PostgresRef(cursor=cur, connection=conn), table

    cur.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    cur.close()
    conn.close()


def _insert(postgres, table, rows: dict[int, object]):
    for _id, tags in rows.items():
        postgres.cursor.execute(
            f"INSERT INTO {table} (id, tags) VALUES (%s, %s)",
            (_id, None if tags is None else json.dumps(tags)),
        )
    postgres.connection.commit()


def _tags_by_id(postgres, table) -> dict[int, object]:
    postgres.cursor.execute(f"SELECT id, tags FROM {table} ORDER BY id")
    return dict(postgres.cursor.fetchall())


def _alter(table, batch):
    return alter_data_batch.function(
        batch=batch, temp_table=table, postgres_conn_id=sql.POSTGRES_CONN_ID
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
def test_alter_data_batch_filters_tags(temp_table, tags, expected):
    postgres, table = temp_table
    _insert(postgres, table, {1: tags})

    count = _alter(table, (1, 1))

    assert _tags_by_id(postgres, table) == {1: expected}
    assert count == (0 if tags == expected else 1)


def test_alter_data_batch_only_updates_rows_in_batch(temp_table):
    postgres, table = temp_table
    bad, good = [{"name": "cc0"}, {"name": "cat"}], [{"name": "cat"}]
    _insert(postgres, table, {1: bad, 2: bad, 3: good, 4: bad})

    count = _alter(table, (2, 3))

    assert count == 1
    assert _tags_by_id(postgres, table) == {1: bad, 2: good, 3: good, 4: bad}


@pytest.mark.parametrize(
    "id_bounds, batch_size, expected",
    [
        ((1, 100), 50, [(1, 50), (51, 100)]),
        ((1, 101), 50, [(1, 50), (51, 100), (101, 150)]),
        ((7, 7), 50, [(7, 56)]),
        # None respects default
        ((1, 100), None, [(1, DEFAULT_BATCH_SIZE)]),
    ],
)
def test_get_alter_batches(id_bounds, batch_size, expected):
    actual = get_alter_batches.function(id_bounds, batch_size)
    assert actual == expected
