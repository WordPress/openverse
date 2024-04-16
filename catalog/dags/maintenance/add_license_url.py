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


def get_null_counts(
    dag_task: AbstractOperator,
    postgres_conn_id: str = POSTGRES_CONN_ID,
) -> int:
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(dag_task),
    )
    nulls_count = postgres.get_first(
        dedent("SELECT COUNT(*) from image WHERE meta_data->>'license_url' IS NULL")
    )[0]
    return nulls_count


@task
def get_license_groups(
    dag_task: AbstractOperator = None, postgres_conn_id: str = POSTGRES_CONN_ID
) -> list[tuple[str, str]]:
    """
    Get license groups of rows that don't have a `license_url` in their
    `meta_data` field.

    :return: List of (license, version) tuples.
    """
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(dag_task),
    )

    select_query = dedent("""
        SELECT license, license_version, count(identifier)
        FROM image WHERE meta_data->>'license_url' IS NULL
        GROUP BY license, license_version
    """)
    license_groups = postgres.get_records(select_query)

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


@task
def update_license_url(
    license_group: tuple[str, str],
    batch_size: int,
    dag_task: AbstractOperator = None,
    postgres_conn_id: str = POSTGRES_CONN_ID,
) -> int:
    """
    Add license_url to meta_data batching all records with the same license.

    :param license_group: tuple of license and version
    :param batch_size: number of records to update in one update statement
    :param dag_task: automatically passed by Airflow, used to set the execution timeout
    :param postgres_conn_id: Postgres connection id
    """

    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(dag_task),
    )
    license_, version = license_group
    *_, license_url = get_license_info_from_license_pair(license_, version)
    license_url_dict = {"license_url": license_url}
    total_updated = 0

    if license_url is None:
        logger.warning(f"No license pair ({license_}, {version}) in the license map.")
        return 0

    logging.info(
        f"Will update license_url in `meta_data` for {license_} {version}"
        f"to {license_url}."
    )

    # Merge existing metadata with the new license_url
    update_query = dedent(
        f"""
        UPDATE image
        SET meta_data = ({Json(license_url_dict)}::jsonb || meta_data)
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

    updated_count = 1
    while updated_count:
        updated_count = postgres.run(
            update_query, autocommit=True, handler=RETURN_ROW_COUNT
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
    null_counts = get_null_counts(dag_task)
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
    updated = update_license_url.expand(
        license_group=license_groups, batch_size="{{ params.batch_size }}"
    )
    # save_to_s3(invalid_items)
    final_report(updated)


add_license_url()
