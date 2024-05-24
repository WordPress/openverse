import pytest

from ingestion_server import queries


def _join_seq(seq):
    # Quick and dirty solution because as_string requires a database context
    # which we don't want to have to construct cause that's a huge PITA to do
    # just to check that two strings are equal.
    # Lifted from: https://github.com/psycopg/psycopg2/issues/747#issuecomment-662857306
    parts = str(seq).split("'")
    return "".join([p for i, p in enumerate(parts) if i % 2 == 1])


@pytest.mark.parametrize(
    "upstream_table, downstream_table",
    [
        ("sample_table", "sample_table"),
        ("audioset_view", "audioset"),
    ],
)
@pytest.mark.parametrize(
    "approach, limit, limit_expected",
    [
        ("basic", None, False),
        ("advanced", None, False),
        ("basic", "100000", True),
        ("advanced", "100000", True),
    ],
)
def test_get_copy_data_query(
    upstream_table, downstream_table, approach, limit, limit_expected
):
    actual = queries.get_copy_data_query(
        upstream_table, downstream_table, ["col1", "col2"], approach, limit
    )
    as_string = _join_seq(actual.seq).replace("\\n", "\n").strip()
    assert ("LIMIT 100000" in as_string) == limit_expected
