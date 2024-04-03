import logging
from datetime import datetime, timedelta

import pytest
from psycopg2.errors import QueryCanceled

from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID
from common.sql import PGExecuteQueryOperator, PostgresHook
from tests.conftest import mark_extended


logger = logging.getLogger(__name__)


DEFAULT_TIMEOUT = timedelta(hours=1).total_seconds()
default_timeout_msg = (
    f"DAG_DEFAULT_ARGS sets the default task execution timeout to "
    f"{DAG_DEFAULT_ARGS['execution_timeout']}. Testing for {DEFAULT_TIMEOUT} seconds."
)
HAPPY_TIMEOUT_PARAMETERS = [
    pytest.param("pg_operator_happy", 2.0, id="pg_operator_happy"),
    pytest.param("pg_hook_happy", 7_200.0, id="pg_hook_happy"),
    pytest.param("pg_hook_no_timeout", DEFAULT_TIMEOUT, id="pg_hook_no_timeout"),
    pytest.param("pg_operator_mapped", 60.0, id="pg_operator_mapped"),
]


# PostgresHook works with or without explicit connection id, and with override conn id
# Testing mainly for documentation purposes
@pytest.mark.parametrize(
    "sql, timeout, expected_result",
    [
        pytest.param("select 1;", None, (1,), id="select_1_no_timeout"),
        pytest.param(
            ["select 1;", "select 2;"],
            None,
            [None, (1,), (2,)],
            id="select_list_none_timeout",
        ),
        pytest.param(
            ["select 1;", "select 2;"],
            0,
            [None, (1,), (2,)],
            id="select_list_zero_timeout",
        ),
        pytest.param("select 1;", 10, (1,), id="select_1_with_timeout"),
        pytest.param(
            ["select 1;", "select 2;"],
            10,
            [None, (1,), (2,)],
            id="select_list_with_timeout",
        ),
    ],
)
def test_PostgresHook_init_defaults(sql, timeout, expected_result):
    pg = PostgresHook()
    assert pg.postgres_conn_id == POSTGRES_CONN_ID
    assert pg.default_statement_timeout == DEFAULT_TIMEOUT, default_timeout_msg
    assert pg.run(sql=sql, statement_timeout=timeout) == expected_result


def test_PostgresHook_conn_id_only_defaults():
    pg = PostgresHook("gibberish")
    assert pg.postgres_conn_id == "gibberish"
    assert pg.default_statement_timeout == DEFAULT_TIMEOUT, default_timeout_msg


@pytest.mark.parametrize(
    "conn_id, timeout, expected_results",
    [
        pytest.param(None, None, (POSTGRES_CONN_ID, DEFAULT_TIMEOUT), id="both_None"),
        pytest.param(
            "xyzqwerty", None, ("xyzqwerty", DEFAULT_TIMEOUT), id="override_connection"
        ),
        pytest.param(None, 60, (POSTGRES_CONN_ID, 60), id="override_timeout"),
        pytest.param("xyzqwerty", 60, ("xyzqwerty", 60), id="override_both"),
    ],
)
def test_PostgresHook_init_connection(conn_id, timeout, expected_results):
    (expected_conn_id, expected_timeout) = expected_results
    pg = PostgresHook(conn_id, timeout)
    assert pg.postgres_conn_id == expected_conn_id
    assert pg.default_statement_timeout == expected_timeout


# PostgresHook gets the database to stop the query and raise an error if the query runs
# too long.
@pytest.mark.parametrize(
    "statement_timeout, default_timeout",
    [
        pytest.param(None, 1, id="default_timeout_only"),
        pytest.param(1, None, id="statement_timeout_only"),
        pytest.param(1, 30, id="statement_timeout_shorter"),
    ],
)
def test_pgdb_raises_cancel_error(statement_timeout, default_timeout):
    with pytest.raises(QueryCanceled):
        hook = PostgresHook(
            default_statement_timeout=default_timeout,
        )
        start_time = datetime.now()
        hook.run("select pg_sleep(3600);", statement_timeout=statement_timeout)
        end_time = datetime.now()
        assert (end_time - start_time) < timedelta(seconds=2)


# PostgresHook.get_execution_timeout returns the correct number of seconds.
# Trusting Airflow controls on what the execution_timeout can be.
# Accessing from the dag object itself independent of any run status.
@pytest.mark.parametrize("task_id, expected_result", HAPPY_TIMEOUT_PARAMETERS)
def test_PostgresHook_get_execution_timeout_happy_tasks(
    mock_timeout_dag, task_id, expected_result
):
    task = mock_timeout_dag.get_task(task_id)
    actual_result = PostgresHook.get_execution_timeout(task)
    assert actual_result == expected_result


def test_PostgresHook_get_execution_timeout_no_task(caplog):
    actual_result = PostgresHook.get_execution_timeout(None)
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert "No task supplied, using default timeout of 3600.0s" in caplog.text
    assert actual_result == DEFAULT_TIMEOUT


# PGExecuteQueryOperator passes the correct default timeout to the hook.
@pytest.mark.parametrize(
    "execution_timeout, expected_result",
    [
        pytest.param(timedelta(seconds=2), 2.0, id="2s_timeout"),
        pytest.param(timedelta(hours=2), 7_200, id="2h_timeout"),
        pytest.param(None, DEFAULT_TIMEOUT, id="no_timeout"),
    ],
)
def test_operator_passes_correct_timeout(execution_timeout, expected_result):
    operator = PGExecuteQueryOperator(
        task_id="test_task_id",
        sql="SELECT NOW();",
        execution_timeout=execution_timeout,
    )
    actual_result = operator.get_db_hook().default_statement_timeout
    assert actual_result == expected_result


# Happy path DAG runs without error (Each task is a test case)
# This generates a warning about running a dag without an explicit data interval being
# deprecated, but I haven't found a way to get it through with this function.
@mark_extended
def test_happy_paths_dag(mock_timeout_dag):
    mock_timeout_dag.test()


@pytest.fixture(scope="session")
def happy_dag_run(mock_timeout_dag):
    exec_dt = datetime.now()
    interval = timedelta(hours=1)
    return mock_timeout_dag.create_dagrun(
        run_id=f"happy_dag_testing_{exec_dt.strftime('%y%m%d%H%M%S')}",
        state="queued",
        execution_date=exec_dt,
        data_interval=(exec_dt - (2 * interval), exec_dt - interval),
    )


# Same timeout setting test as above, but this time in the context of an instantiated
# dag run.
@pytest.mark.parametrize("task_id, expected_timeout", HAPPY_TIMEOUT_PARAMETERS)
def test_use_task_not_task_instance(task_id, expected_timeout, happy_dag_run):
    with pytest.raises(AttributeError):
        execution_timeout = happy_dag_run.get_task_instance(task_id).execution_timeout
    execution_timeout = PostgresHook.get_execution_timeout(
        happy_dag_run.get_dag().get_task(task_id)
    )
    assert execution_timeout == expected_timeout


def test_run_statement_timeout():
    pg = PostgresHook(default_statement_timeout=10)
    pg.run_statement_timeout()
    actual = pg.run(sql="show statement_timeout;", statement_timeout=0)
    assert actual == ("10s",)
