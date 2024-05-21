"""
# Add license URL

Add `license_url` to rows without one in their `meta_data` fields.
This PR merges the `meta_data` value with "{license_url: https://... }", where the
url is constructed from the `license` and `license_version` columns.

This is a maintenance DAG that should be run once.
"""

import logging
from datetime import timedelta
from textwrap import dedent

from airflow.decorators import dag, task
from airflow.models.abstractoperator import AbstractOperator
from airflow.models.param import Param
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from psycopg2._json import Json

from common import slack
from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID
from common.licenses import get_license_info_from_license_pair
from common.sql import PostgresHook
from database.batched_update.constants import DAG_ID as BATCHED_UPDATE_DAG_ID


DAG_ID = "add_license_url"

logger = logging.getLogger(__name__)


def run_sql(
    sql: str,
    log_sql: bool = True,
    method: str = "get_records",
    handler: callable = None,
    autocommit: bool = False,
    postgres_conn_id: str = POSTGRES_CONN_ID,
    dag_task: AbstractOperator = None,
):
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(dag_task),
        log_sql=log_sql,
    )
    if method == "get_records":
        return postgres.get_records(sql)
    elif method == "get_first":
        return postgres.get_first(sql)
    else:
        return postgres.run(sql, autocommit=autocommit, handler=handler)


@task
def get_license_groups(query: str, ti=None) -> list[tuple[str, str]]:
    """
    Get license groups of rows that don't have a `license_url` in their
    `meta_data` field.

    :return: List of (license, version) tuples.
    """
    license_groups = run_sql(query, dag_task=ti.task)

    total_nulls = sum(group[2] for group in license_groups)
    licenses_detailed = "\n".join(
        # License, version, count
        f"{group[0]} \t{group[1]} \t{group[2]:.0f}"
        for group in license_groups
    )

    message = f"""
Starting `{DAG_ID}` DAG. Found {len(license_groups):.0f} license groups with {total_nulls:.0f}
records without `license_url` in `meta_data` left.\nCount per license-version:
{licenses_detailed}
    """
    slack.send_message(
        message,
        username="Airflow DAG Data Normalization - license_url",
        dag_id=DAG_ID,
    )

    return [(group[0], group[1]) for group in license_groups]


def get_license_conf(license_info):
    license_, license_version, license_url = license_info
    license_url_dict = {"license_url": license_url}
    query_id = f"add_license_url_{license_}_{license_version}"
    for char_to_remove in [".", "-"]:
        query_id = query_id.replace(char_to_remove, "_")

    conf = {
        "query_id": query_id,
        "table_name": "image",
        "select_query": (
            f"WHERE license = '{license_}' AND license_version = '{license_version}' "
            f"AND meta_data->>'license_url' IS NULL"
        ),
        # Merge existing metadata with the new license_url
        "update_query": f"SET meta_data = ({Json(license_url_dict)}::jsonb || meta_data), updated_on = now()",
        "update_timeout": 259200,  # 3 days in seconds
        "dry_run": False,
        "resume_update": False,
    }
    return conf


@task
def get_license_groups_confs(license_groups, batch_size: int) -> list[dict]:
    confs = []
    for license_, license_version in license_groups:
        license_info = get_license_info_from_license_pair(license_, license_version)
        if license_info is None:
            logger.warning(
                f"No license pair ({license_}, {license_version}) "
                f"in the license map. Skipping."
            )
            continue

        confs.append({"batch_size": batch_size} | get_license_conf(license_info))
    return confs


@dag(
    dag_id=DAG_ID,
    schedule=None,
    catchup=False,
    tags=["data_normalization"],
    doc_md=__doc__,
    default_args={
        **DAG_DEFAULT_ARGS,
        "retries": 0,
        "execution_timeout": timedelta(hours=5),
    },
    render_template_as_native_obj=True,
    params={
        "batch_size": Param(
            default=10_000,
            type="integer",
            description="The number of records to update per batch.",
        ),
    },
)
def add_license_url():
    query = dedent("""
        SELECT license, license_version, count(identifier)
        FROM image WHERE meta_data->>'license_url' IS NULL
        GROUP BY license, license_version
    """)

    license_groups = get_license_groups(query)

    TriggerDagRunOperator.partial(
        task_id="trigger_batched_update",
        trigger_dag_id=BATCHED_UPDATE_DAG_ID,
        wait_for_completion=True,
        execution_timeout=timedelta(hours=5),
        max_active_tis_per_dag=1,
        retries=0,
    ).expand(
        conf=get_license_groups_confs(
            license_groups=license_groups, batch_size="{{ params.batch_size }}"
        )
    )


add_license_url()
