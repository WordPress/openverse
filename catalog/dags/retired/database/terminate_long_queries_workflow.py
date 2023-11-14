"""
# Terminate long-running queries

This DAG runs every fifteen minutes and terminates long-running
queries of a specific query string in the API DB.
"""

import logging
from textwrap import dedent

from airflow import DAG
from airflow.exceptions import AirflowSkipException
from airflow.operators.python import PythonOperator

from common.constants import (
    DAG_DEFAULT_ARGS,
    OPENLEDGER_API_CONN_ID,
    XCOM_PULL_TEMPLATE,
)
from common.slack import send_message
from common.sql import PostgresHook, RETURN_ROW_COUNT


logger = logging.getLogger(__name__)


DAG_ID = "terminate_long_queries"
MAX_ACTIVE = 1

QUERY_TO_TERMINATE = 'SELECT "image"."id", "image"."created_on", "image"."updated_on", "image"."identifier", "image"."foreign_identifier", "image"."title", "image"."foreign_landing_url", "image"."creator", "image"."creator_url", "image"."thumbnail", "image"."provider", "image"."url", "image"."filesize", "image"."filetype", "image"."watermarked", "image"."license", "image"."license_version", "image"."source", "image"."last_synced_with_source", "image"."removed_from_source", "image"."view_count", "image"."tags", "image"."tags_list", "image"."category", "image"."meta_data", "image"."width", "image"."height" FROM "image" ORDER BY "image"."created_on" DESC LIMIT 1000'  # noqa: E501


def _terminate_queries(
    postgres_conn_id,
    query_to_terminate,
):
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=60,  # 1-minute timeout
    )

    terminate_query = dedent(
        f"""
        select pg_terminate_backend(pid)
        from pg_stat_activity
        where pid in (
            select pid from pg_stat_activity
            where query = '{query_to_terminate}');
        """
    )

    return postgres.run(terminate_query, handler=RETURN_ROW_COUNT)


def _report_terminated_query_count(dag_id: str, count: int):
    if count == 0:
        raise AirflowSkipException("No queries matching query string were found.")

    send_message(
        f"{count} queries were terminated.",
        dag_id=dag_id,
        username="Terminate long queries.",
    )


dag = DAG(
    dag_id=DAG_ID,
    default_args=DAG_DEFAULT_ARGS,
    max_active_tasks=MAX_ACTIVE,
    max_active_runs=MAX_ACTIVE,
    catchup=False,
    schedule="*/7 * * * *",  # Every 7 minutes
    tags=["database"],
    render_template_as_native_obj=True,
)

with dag:
    terminate_queries = PythonOperator(
        task_id="terminate_queries",
        python_callable=_terminate_queries,
        op_args=[OPENLEDGER_API_CONN_ID, QUERY_TO_TERMINATE],
    )

    report_query_count = PythonOperator(
        task_id="report_query_count",
        python_callable=_report_terminated_query_count,
        op_kwargs={
            "dag_id": DAG_ID,
            "count": XCOM_PULL_TEMPLATE.format(
                terminate_queries.task_id, "return_value"
            ),
        },
    )

    terminate_queries >> report_query_count
