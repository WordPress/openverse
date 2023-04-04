"""
One-time run DAG to fix the foreign identifier for PhyloPic images.

In order to prevent broken links, we need to update the foreign identifier from using
the image URL to using the foreign image UUID.
"""

import logging
import re
from datetime import timedelta
from textwrap import dedent

from airflow.decorators import dag
from airflow.models.abstractoperator import AbstractOperator
from airflow.operators.python import PythonOperator
from psycopg2.errors import UniqueViolation

from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID, XCOM_PULL_TEMPLATE
from common.slack import send_message
from common.sql import PostgresHook


logger = logging.getLogger(__name__)

DAG_ID = "update_phylopic_foreign_identifier"


def update_foreign_identifiers(task: AbstractOperator) -> dict[str, int]:
    pg = PostgresHook(
        postgres_conn_id=POSTGRES_CONN_ID,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
    )
    phylopic_rows = pg.get_records(
        "SELECT foreign_identifier, identifier FROM image WHERE provider = 'phylopic';"
    )

    uuid_pattern = (
        "[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}"
    )
    prog = re.compile(uuid_pattern)
    counter = {
        "updated": 0,
        "skipped": 0,
        "failed_none": 0,
        "failed_duplicate": 0,
        "failed_other_reason": 0,
    }

    for foreign_identifier, identifier in phylopic_rows:
        if len(foreign_identifier) == 36:
            # The foreign identifier is (most likely) already the UUID
            counter["skipped"] += 1
            continue

        uuid = prog.search(foreign_identifier).group()
        if uuid is None:
            counter["failed_none"] += 1
            continue

        # Update the foreign identifier with the UUID
        update_query = dedent(
            f"""
            UPDATE image SET foreign_identifier = '{uuid}', thumbnail = NULL
            WHERE identifier = '{identifier}'
            """
        )

        try:
            pg.run(update_query)
            counter["updated"] += 1
        except UniqueViolation:
            logger.warning(
                f"Duplicate foreign identifier {uuid} for identifier {identifier}"
            )
            counter["failed_duplicate"] += 1
        except Exception as e:
            counter["failed_other_reason"] += 1
            logger.error(
                f"Failed to update foreign identifier for identifier {identifier}"
                f" with error: {e}"
            )

    return counter


def final_report(counter) -> None:
    message = f"{DAG_ID} DAG run completed. Update statistics:\n{counter}."
    send_message(message, dag_id=DAG_ID)


@dag(
    dag_id=DAG_ID,
    default_args={
        **DAG_DEFAULT_ARGS,
        "retries": 0,
        "execution_timeout": timedelta(hours=5),
    },
    schedule=None,
    catchup=False,
    doc_md=__doc__,
    tags=["data_normalization"],
)
def update_phylopic():
    update = PythonOperator(
        task_id="update_foreign_identifiers",
        python_callable=update_foreign_identifiers,
    )
    report = PythonOperator(
        task_id="final_report_on_foreign_identifiers",
        python_callable=final_report,
        op_kwargs={
            "counter": XCOM_PULL_TEMPLATE.format(update.task_id, "return_value")
        },
    )

    update >> report


update_phylopic()
