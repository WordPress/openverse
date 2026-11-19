import pytest

from common.sql import PostgresHook
from maintenance.add_license_url import get_license_conf


@pytest.fixture
def table():
    name = "test_add_license_url"
    pg = PostgresHook()
    pg.run(
        f"CREATE TABLE {name} (meta_data jsonb, updated_on timestamp);"
        f"""INSERT INTO {name} VALUES ('{{"foo": "bar"}}', NULL);""",
        handler=None,
    )
    yield name
    pg.run(f"DROP TABLE {name};", handler=None)


@pytest.mark.parametrize(
    "license_url",
    [
        "https://creativecommons.org/licenses/by/4.0/",
        "https://example.com/it's-a-license/",
    ],
)
def test_update_query_merges_license_url_into_meta_data(license_url, table):
    conf = get_license_conf(("by", "4.0", license_url))
    pg = PostgresHook()

    pg.run(f"UPDATE {table} {conf['update_query']};", handler=None)

    assert pg.get_first(f"SELECT meta_data FROM {table};") == (
        {"foo": "bar", "license_url": license_url},
    )
