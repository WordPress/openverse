"""
# Add license URL

Add `license_url` to all rows that have `NULL` in their `meta_data` fields.
This PR sets the meta_data value to  "{license_url: https://... }", where the
url is constructed from the `license` and `license_version` columns.

This is a maintenance DAG that should be run once. If all the null values in
the `meta_data` column are updated, the DAG will only run the first and the
last step, logging the statistics.
"""
import logging
from datetime import timedelta
from textwrap import dedent
from typing import Literal

from airflow.models import DAG
from airflow.models.abstractoperator import AbstractOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID, XCOM_PULL_TEMPLATE
from common.licenses.constants import get_reverse_license_path_map
from common.loader.sql import RETURN_ROW_COUNT
from common.slack import send_message
from common.sql import PostgresHook
from psycopg2._json import Json


DAG_ID = "add_license_url"
UPDATE_LICENSE_URL = "update_license_url"
FINAL_REPORT = "final_report"

ALERT_EMAIL_ADDRESSES = ""

logger = logging.getLogger(__name__)

base_url = "https://creativecommons.org/"


def get_null_counts(
    postgres_conn_id: str,
    task: AbstractOperator,
) -> int:
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
    )
    null_meta_data_count = postgres.get_first(
        dedent("SELECT COUNT(*) from image WHERE meta_data IS NULL;")
    )[0]
    return null_meta_data_count


def get_statistics(
    postgres_conn_id: str,
    task: AbstractOperator,
) -> Literal[UPDATE_LICENSE_URL, FINAL_REPORT]:
    null_meta_data_count = get_null_counts(postgres_conn_id, task)

    next_task = UPDATE_LICENSE_URL if null_meta_data_count > 0 else FINAL_REPORT
    logger.info(
        f"There are {null_meta_data_count} records with NULL in meta_data. \n"
        f"Next step: {next_task}"
    )

    return next_task


def update_license_url(postgres_conn_id: str, task: AbstractOperator) -> dict[str, int]:
    """Add license_url to meta_data batching all records with the same license.
    :param task: automatically passed by Airflow, used to set the execution timeout
    :param postgres_conn_id: Postgres connection id
    """

    logger.info("Getting image records without license_url.")
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
    )
    license_map = get_reverse_license_path_map()

    total_count = 0
    total_counts = {}
    for license_items, path in license_map.items():
        license_name, license_version = license_items
        logger.info(f"Processing {license_name} {license_version}, {license_items}.")
        license_url = f"{base_url}{path}/"

        select_query = dedent(
            f"""
            SELECT identifier FROM image
            WHERE (
            meta_data is NULL AND license = '{license_name}'
            AND license_version = '{license_version}')
            """
        )
        result = postgres.get_records(select_query)

        if not result:
            logger.info(f"No records to update with {license_url}.")
            continue
        logger.info(f"{len(result)} records to update with {license_url}.")
        license_url_col = {"license_url": license_url}
        update_license_url_query = dedent(
            f"""
            UPDATE image
            SET meta_data = {Json(license_url_col)}
            WHERE identifier IN ({','.join([f"'{r[0]}'" for r in result])});
            """
        )

        updated_count = postgres.run(
            update_license_url_query, autocommit=True, handler=RETURN_ROW_COUNT
        )
        logger.info(f"{updated_count} records updated with {license_url}.")
        total_counts[license_url] = updated_count
        total_count += updated_count

    logger.info(f"{total_count} image records with missing license_url updated.")
    for license_url, count in total_counts.items():
        logger.info(f"{count} records with {license_url}.")
    return total_counts


def final_report(
    postgres_conn_id: str,
    item_count: int,
    task: AbstractOperator,
):
    null_meta_data_count = get_null_counts(postgres_conn_id, task)

    message = f"""
Added license_url to *{item_count}* items`
Now, there are {null_meta_data_count} records with NULL meta_data left.
"""
    send_message(
        message,
        username="Airflow DAG Data Normalization - license_url",
        dag_id=DAG_ID,
    )

    logger.info(message)


dag = DAG(
    dag_id=DAG_ID,
    default_args={
        **DAG_DEFAULT_ARGS,
        "retries": 0,
        "execution_timeout": timedelta(hours=5),
    },
    schedule_interval=None,
    catchup=False,
    # Use the docstring at the top of the file as md docs in the UI
    doc_md=__doc__,
    tags=["data_normalization"],
)

with dag:
    get_statistics = BranchPythonOperator(
        task_id="get_stats",
        python_callable=get_statistics,
        op_kwargs={"postgres_conn_id": POSTGRES_CONN_ID},
    )
    update_license_url = PythonOperator(
        task_id=UPDATE_LICENSE_URL,
        python_callable=update_license_url,
        op_kwargs={"postgres_conn_id": POSTGRES_CONN_ID},
    )
    final_report = PythonOperator(
        task_id=FINAL_REPORT,
        python_callable=final_report,
        op_kwargs={
            "postgres_conn_id": POSTGRES_CONN_ID,
            "item_count": XCOM_PULL_TEMPLATE.format(
                update_license_url.task_id, "return_value"
            ),
        },
    )

    # If there are no records with NULL meta_data, skip the update step
    # and go straight to the final report
    get_statistics >> [update_license_url, final_report]
    update_license_url >> final_report
