import socket
from datetime import datetime, timedelta
from urllib.parse import urlparse

import boto3
import pytest
from airflow import DAG
from airflow.models.abstractoperator import AbstractOperator
from airflow.operators.python import PythonOperator
from common.constants import POSTGRES_CONN_ID
from common.sql import PGExecuteQueryOperator, PostgresHook

from tests.dags.common.loader.test_s3 import ACCESS_KEY, S3_LOCAL_ENDPOINT, SECRET_KEY


def _delete_bucket(bucket):
    key_list = [{"Key": obj.key} for obj in bucket.objects.all()]
    if len(list(bucket.objects.all())) > 0:
        bucket.delete_objects(Delete={"Objects": key_list})
    bucket.delete()


def pytest_configure(config):
    """
    Dynamically allow the S3 host during testing. This is required because:
    * Docker will use different internal ports depending on what's available
    * Boto3 will open a socket with the IP address directly rather than the hostname
    * We can't add the allow_hosts mark to the empty_s3_bucket fixture directly
        (see: https://github.com/pytest-dev/pytest/issues/1368)
    """
    s3_host = socket.gethostbyname(urlparse(S3_LOCAL_ENDPOINT).hostname)
    config.__socket_allow_hosts = ["s3", "postgres", s3_host]


@pytest.fixture
def empty_s3_bucket(request):
    # Bucket names can't be longer than 63 characters or have strange characters
    bucket_name = f"bucket-{hash(request.node.name)}"
    print(f"{bucket_name=}")
    bucket = boto3.resource(
        "s3",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        endpoint_url=S3_LOCAL_ENDPOINT,
    ).Bucket(bucket_name)

    if bucket.creation_date:
        _delete_bucket(bucket)
    bucket.create()
    yield bucket
    _delete_bucket(bucket)


@pytest.fixture
def identifier(request):
    return f"{hash(request.node.name)}".replace("-", "_")


@pytest.fixture
def image_table(identifier):
    # Parallelized tests need to use distinct database tables
    return f"image_{identifier}"


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
