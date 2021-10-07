import os
from collections import namedtuple
from unittest.mock import patch

import psycopg2
import pytest
from util.loader import smithsonian_unit_codes as si


POSTGRES_TEST_URI = os.getenv("AIRFLOW_CONN_POSTGRES_OPENLEDGER_TESTING")
POSTGRES_CONN_ID = os.getenv("TEST_CONN_ID")
SI_UNIT_CODE_TABLE = "test_unit_code_table"


CREATE_TABLE_QUERY = (
    f"CREATE TABLE IF NOT EXISTS public.{SI_UNIT_CODE_TABLE} ("
    f"new_unit_code character varying(80),"
    f"action character varying(40));"
)


@pytest.fixture
def postgres_with_test_unit_code_table():
    Postgres = namedtuple("Postgres", ["cursor", "connection"])
    conn = psycopg2.connect(POSTGRES_TEST_URI)
    cur = conn.cursor()
    drop_command = f"DROP TABLE IF EXISTS {SI_UNIT_CODE_TABLE}"
    cur.execute(drop_command)
    conn.commit()
    create_command = CREATE_TABLE_QUERY
    cur.execute(create_command)
    conn.commit()

    yield Postgres(cursor=cur, connection=conn)

    cur.execute(drop_command)
    cur.close()
    conn.commit()
    conn.close()


def test_alert_new_unit_codes():
    unit_code_set = {"a", "b", "c", "d"}
    sub_prov_dict = {"sub_prov1": {"a", "c"}, "sub_prov2": {"b"}, "sub_prov3": {"e"}}

    assert si.get_new_and_outdated_unit_codes(unit_code_set, sub_prov_dict) == (
        {"d"},
        {"e"},
    )


@pytest.mark.enable_socket
def test_alert_unit_codes_from_api(postgres_with_test_unit_code_table):
    postgres_conn_id = POSTGRES_CONN_ID
    unit_code_table = SI_UNIT_CODE_TABLE

    with patch.object(
        si, "get_new_and_outdated_unit_codes", return_value=({"d"}, {"e"})
    ) as mock_get_unit_codes:
        with pytest.raises(Exception):
            si.alert_unit_codes_from_api(postgres_conn_id, unit_code_table)

    mock_get_unit_codes.assert_called()

    postgres_with_test_unit_code_table.cursor.execute(
        f"SELECT * FROM {unit_code_table};"
    )

    actual_rows = postgres_with_test_unit_code_table.cursor.fetchall()
    postgres_with_test_unit_code_table.connection.commit()

    assert len(actual_rows) == 2
    assert ("d", "add") in actual_rows
    assert ("e", "delete") in actual_rows
