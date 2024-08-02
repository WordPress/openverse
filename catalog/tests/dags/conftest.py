from datetime import datetime, timedelta
from unittest import mock

import pytest
from airflow import DAG
from airflow.models.abstractoperator import AbstractOperator
from airflow.operators.python import PythonOperator
from requests import Response

from common.constants import POSTGRES_CONN_ID, SQLInfo
from common.sql import PGExecuteQueryOperator, PostgresHook
from oauth2 import oauth2


FAKE_OAUTH_PROVIDER_NAME = "fakeprovider"


def _var_get_replacement(*args, **kwargs):
    values = {
        oauth2.OAUTH2_TOKEN_KEY: {
            FAKE_OAUTH_PROVIDER_NAME: {
                "access_token": "fakeaccess",
                "refresh_token": "fakerefresh",
            }
        },
        oauth2.OAUTH2_AUTH_KEY: {FAKE_OAUTH_PROVIDER_NAME: "fakeauthtoken"},
        oauth2.OAUTH2_PROVIDERS_KEY: {
            FAKE_OAUTH_PROVIDER_NAME: {
                "client_id": "fakeclient",
                "client_secret": "fakesecret",
            }
        },
    }
    return values[args[0]]


@pytest.fixture
def identifier(request):
    return f"{hash(request.node.name)}".replace("-", "_")


@pytest.fixture
def image_table(identifier):
    # Parallelized tests need to use distinct database tables
    return f"image_{identifier}"


@pytest.fixture
def sql_info(
    image_table,
    identifier,
) -> SQLInfo:
    return SQLInfo(
        media_table=image_table,
        metrics_table=f"image_popularity_metrics_{identifier}",
        standardized_popularity_fn=f"standardized_image_popularity_{identifier}",
        popularity_percentile_fn=f"image_popularity_percentile_{identifier}",
    )


TEST_SQL = "SELECT PG_SLEEP(1);"


def timed_pg_hook_sleeper(
    task,
    statement_timeout: float = None,
):
    pg = PostgresHook(
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
        conn_id=POSTGRES_CONN_ID,
    )
    pg.run(sql=TEST_SQL, statement_timeout=statement_timeout)


def mapped_select_pg_hook(
    select_val: int,
    task: AbstractOperator,
):
    pg = PostgresHook(
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
        conn_id=POSTGRES_CONN_ID,
    )
    return pg.run(f"select {select_val};")


def create_pg_timeout_tester_dag():
    with DAG(
        dag_id="a_pg_timeout_tester",
        schedule=None,
        doc_md="DAG to test query timeouts in postgres",
        start_date=datetime(2023, 1, 1),
    ) as dag:
        pg_operator_happy = PGExecuteQueryOperator(
            task_id="pg_operator_happy",
            retries=0,
            conn_id=POSTGRES_CONN_ID,
            sql=TEST_SQL,
            execution_timeout=timedelta(seconds=2),
            doc_md="Custom PG operator, with query finished before execution timeout",
        )
        pg_hook_happy = PythonOperator(
            task_id="pg_hook_happy",
            retries=0,
            python_callable=timed_pg_hook_sleeper,
            execution_timeout=timedelta(hours=2),
            doc_md="Custom PG hook, with query finished before execution timeout",
        )
        pg_hook_no_timeout = PythonOperator(
            task_id="pg_hook_no_timeout",
            retries=0,
            python_callable=timed_pg_hook_sleeper,
            doc_md="Custom PG hook, with no execution timeout",
        )
        pg_operator_mapped = PythonOperator.partial(
            task_id="pg_operator_mapped",
            retries=0,
            execution_timeout=timedelta(minutes=1),
            doc_md="Custom PG operator, mapped to list",
            python_callable=mapped_select_pg_hook,
        ).expand(op_args=[(1,), (2,)])
        [pg_operator_happy, pg_hook_happy, pg_hook_no_timeout, pg_operator_mapped]
    return dag


@pytest.fixture(scope="session")
def mock_timeout_dag():
    return create_pg_timeout_tester_dag()


@pytest.fixture(scope="session")
def mock_pg_hook_task(mock_timeout_dag) -> PythonOperator:
    return mock_timeout_dag.get_task("pg_hook_happy")


@pytest.fixture
def oauth_provider_var_mock():
    with mock.patch("oauth2.oauth2.Variable") as MockVariable:
        MockVariable.get.side_effect = _var_get_replacement
        yield MockVariable


def _make_response(*args, **kwargs):
    """
    Mock the request used during license URL validation.

    Most times the results of this function are expected to end with a `/`, so if the
    URL provided does not we add it.
    """
    response: Response = mock.Mock(spec=Response)
    if args:
        response.ok = True
        url = args[0]
        if isinstance(url, str) and not url.endswith("/"):
            url += "/"
        response.url = url
    return response


@pytest.fixture(autouse=True)
def requests_get_mock():
    """
    Mock request.get calls that occur during testing.

    This is primarily done by the `common.urls.rewrite_redirected_url` function.
    """
    with mock.patch("common.urls.requests_get", autospec=True) as mock_get:
        mock_get.side_effect = _make_response
        yield


@pytest.fixture
def freeze_time(monkeypatch):
    """
    Patch the `datetime.datetime.now` function to return a fixed, settable time.

    This effectively freezes time.
    https://stackoverflow.com/a/28073449 CC BY-SA 3.0
    """
    import datetime

    original = datetime.datetime

    class FreezeMeta(type):
        def __instancecheck__(self, instance):
            if isinstance(instance, (original, Freeze)):
                return True

    class Freeze(datetime.datetime):
        __metaclass__ = FreezeMeta

        @classmethod
        def freeze(cls, val):
            cls.frozen = val

        @classmethod
        def now(cls):
            return cls.frozen

        @classmethod
        def delta(cls, timedelta=None, **kwargs):
            """Move time fwd/bwd by the delta."""
            from datetime import timedelta as td

            if not timedelta:
                timedelta = td(**kwargs)
            cls.frozen += timedelta

    monkeypatch.setattr(datetime, "datetime", Freeze)
    Freeze.freeze(original.now())
    return Freeze
