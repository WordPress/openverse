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
from collections import defaultdict
from datetime import timedelta
from textwrap import dedent
from typing import Literal

from airflow.models import DAG
from airflow.models.abstractoperator import AbstractOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID, XCOM_PULL_TEMPLATE
from common.licenses import get_license_info_from_license_pair
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

    select_query = dedent(
        """
    SELECT identifier, license, license_version
    FROM image WHERE meta_data IS NULL;"""
    )
    records_with_null_in_metadata = postgres.get_records(select_query)

    # Dictionary with license pair as key and list of identifiers as value
    records_to_update = defaultdict(list)

    for result in records_with_null_in_metadata:
        identifier, license_, version = result
        records_to_update[(license_, version)].append(identifier)

    total_updated = 0
    updated_by_license = {}

    for (license_, version), identifiers in records_to_update.items():
        *_, license_url = get_license_info_from_license_pair(license_, version)
        if license_url is None:
            logger.info(f"No license pair ({license_}, {version}) in the license map.")
            continue
        logger.info(f"{len(identifiers):4} items will be updated with {license_url}")
        license_url_dict = {"license_url": license_url}
        update_query = dedent(
            f"""
            UPDATE image
            SET meta_data = {Json(license_url_dict)}
            WHERE identifier IN ({','.join([f"'{r}'" for r in identifiers])});
            """
        )
        updated_count: int = postgres.run(
            update_query, autocommit=True, handler=RETURN_ROW_COUNT
        )
        logger.info(f"{updated_count} records updated with {license_url}.")
        if updated_count:
            updated_by_license[license_url] = updated_count
        total_updated += updated_count
    logger.info(f"Updated {total_updated} rows")
    return updated_by_license


def final_report(
    postgres_conn_id: str,
    updated_by_license: dict[str, int] | None,
    task: AbstractOperator = None,
):
    """Check for null in `meta_data` and send a message to Slack
    with the statistics of the DAG run.

    :param postgres_conn_id: Postgres connection id.
    :param updated_by_license: stringified JSON with the number of records updated
    for each license_url. If `update_license_url` was skipped, this will be "None".
    :param task: automatically passed by Airflow, used to set the execution timeout.
    """
    null_meta_data_count = get_null_counts(postgres_conn_id, task)

    if not updated_by_license:
        updated_message = "No records were updated."
    else:
        formatted_item_count = "".join(
            [
                f"{license_url}: {count} rows\n"
                for license_url, count in updated_by_license.items()
            ]
        )
        updated_message = f"Update statistics:\n{formatted_item_count}"
    message = f"""
`add_license_url` DAG run completed.
{updated_message}
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
    doc_md=__doc__,
    tags=["data_normalization"],
    render_template_as_native_obj=True,
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
        trigger_rule=TriggerRule.ALL_DONE,
        op_kwargs={
            "postgres_conn_id": POSTGRES_CONN_ID,
            "updated_by_license": XCOM_PULL_TEMPLATE.format(
                update_license_url.task_id, "return_value"
            ),
        },
    )

    # If there are no records with NULL meta_data, skip the update step
    # and go straight to the final report
    get_statistics >> [update_license_url, final_report]
    update_license_url >> final_report
