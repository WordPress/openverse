"""
# Add license URL

Add `license_url` to all rows that have `NULL` in their `meta_data` fields.
This PR sets the meta_data value to  "{license_url: https://... }", where the
url is constructed from the `license` and `license_version` columns.

This is a maintenance DAG that should be run once. If all the null values in
the `meta_data` column are updated, the DAG will only run the first and the
last step, logging the statistics.
"""

import csv
import logging
from datetime import timedelta
from tempfile import NamedTemporaryFile
from textwrap import dedent

from airflow.decorators import dag, task
from airflow.models.abstractoperator import AbstractOperator
from airflow.models.param import Param
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from psycopg2._json import Json

from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID
from common.licenses import get_license_info_from_license_pair
from common.slack import send_message
from common.sql import RETURN_ROW_COUNT, PostgresHook
from providers.provider_dag_factory import AWS_CONN_ID, OPENVERSE_BUCKET


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
def get_license_groups(dag_task: AbstractOperator = None) -> list[tuple[str, str]]:
    """
    Get license groups of rows that don't have a `license_url` in their
    `meta_data` field.

    :return: List of (license, version) tuples.
    """

    select_query = dedent("""
        SELECT license, license_version, count(identifier)
        FROM image WHERE meta_data->>'license_url' IS NULL
        GROUP BY license, license_version
    """)
    license_groups = run_sql(select_query, dag_task=dag_task)

    total_nulls = sum(group[2] for group in license_groups)
    licenses_detailed = "\n".join(
        f"{group[0]} \t{group[1]} \t{group[2]}" for group in license_groups
    )

    message = f"""
Starting `{DAG_ID}` DAG. Found {len(license_groups)} license groups with {total_nulls}
records without `license_url` in `meta_data` left.\nCount per license-version:
{licenses_detailed}
    """
    send_message(
        message,
        username="Airflow DAG Data Normalization - license_url",
        dag_id=DAG_ID,
    )

    return [(group[0], group[1]) for group in license_groups]


@task(max_active_tis_per_dag=1)
def update_license_url(
    license_group: tuple[str, str],
    batch_size: int,
    dag_task: AbstractOperator = None,
) -> int:
    """
    Add license_url to meta_data batching all records with the same license.

    :param license_group: tuple of license and version
    :param batch_size: number of records to update in one update statement
    :param dag_task: automatically passed by Airflow, used to set the execution timeout.
    """
    license_, version = license_group
    *_, license_url = get_license_info_from_license_pair(license_, version)
    if license_url is None:
        logger.warning(f"No license pair ({license_}, {version}) in the license map.")
        return 0

    logging.info(
        f"Will add `license_url` in `meta_data` for records with license "
        f"{license_} {version} to {license_url}."
    )
    license_url_dict = {"license_url": license_url}

    # Merge existing metadata with the new license_url
    update_query = dedent(
        f"""
        UPDATE image
        SET meta_data = ({Json(license_url_dict)}::jsonb || meta_data), updated_on = now()
        WHERE identifier IN (
            SELECT identifier
            FROM image
            WHERE license = '{license_}' AND license_version = '{version}'
                AND meta_data->>'license_url' IS NULL
            LIMIT {batch_size}
            FOR UPDATE SKIP LOCKED
        );
        """
    )
    total_updated = 0
    updated_count = 1
    while updated_count:
        updated_count = run_sql(
            update_query,
            log_sql=total_updated == 0,
            method="run",
            handler=RETURN_ROW_COUNT,
            autocommit=True,
            dag_task=dag_task,
        )
        total_updated += updated_count
    logger.info(f"Updated {total_updated} rows with {license_url}.")

    return total_updated


@task
def final_report(updated, dag_task: AbstractOperator = None):
    """
    Check for null in `meta_data` and send a message to Slack with the statistics
    of the DAG run.

    :param updated: total number of records updated
    :param dag_task: automatically passed by Airflow, used to set the execution timeout.
    """
    total_updated = sum(updated)
    query = "SELECT COUNT(*) from image WHERE meta_data->>'license_url' IS NULL"
    null_counts = run_sql(query, method="get_first", dag_task=dag_task)[0]

    message = f"""
    `{DAG_ID}` DAG run completed. Updated {total_updated} records with `license_url` in the
    `meta_data` field. {null_counts} records left pending.
    """
    send_message(
        message,
        username="Airflow DAG Data Normalization - license_url",
        dag_id=DAG_ID,
    )


@task
def save_to_s3(
    invalid_items, aws_conn_id: str = AWS_CONN_ID, s3_bucket: str = OPENVERSE_BUCKET
):
    """
    Save the records with invalid license pairs to S3.
    :param aws_conn_id: AWS connection id
    :param invalid_items: The list of dictionaries with the invalid items
    :param s3_bucket: S3 bucket
    """
    if not invalid_items:
        return

    s3_key = "invalid_items.tsv"

    with NamedTemporaryFile(mode="w+", encoding="utf-8") as f:
        tsv_writer = csv.DictWriter(
            f, delimiter="\t", fieldnames=["license", "license_version", "identifier"]
        )
        tsv_writer.writeheader()
        for item in invalid_items:
            tsv_writer.writerow(item)
        f.seek(0)
        logger.info(f"Uploading the invalid items to {s3_bucket}:{s3_key}")
        with open(f.name) as fp:
            logger.info(fp.read())
        s3 = S3Hook(aws_conn_id=aws_conn_id)
        s3.load_file(f.name, s3_key, bucket_name=s3_bucket, replace=True)


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
    license_groups = get_license_groups()
    updated = update_license_url.partial(batch_size="{{ params.batch_size }}").expand(
        license_group=license_groups
    )
    # save_to_s3(invalid_items)
    final_report(updated)


add_license_url()
