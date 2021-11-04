"""
This file defines an Apache Airflow DAG that refreshes the data in
image_view, but not the underlying tables.  This means the only effect
of this DAG is to add or update data (including popularity data) for
images which have been ingested since the last time the view was
refreshed.

This should be run once per day.
"""
import logging
import os
from datetime import datetime, timedelta

from airflow import DAG
from common.popularity import operators


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

DAG_ID = "refresh_image_view_data"
DB_CONN_ID = os.getenv("OPENLEDGER_CONN_ID", "postgres_openledger_testing")
CONCURRENCY = 1
# We don't run on the first of the month, since the
# `refresh_all_image_popularity_data` DAG should run on that day.
SCHEDULE_CRON = "0 0 2-31 * *"

DAG_DEFAULT_ARGS = {
    "owner": "data-eng-admin",
    "depends_on_past": False,
    "start_date": datetime(2020, 6, 15),
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(seconds=3600),
}


def create_dag(
    dag_id=DAG_ID,
    args=DAG_DEFAULT_ARGS,
    concurrency=CONCURRENCY,
    max_active_runs=CONCURRENCY,
    schedule_cron=SCHEDULE_CRON,
    postgres_conn_id=DB_CONN_ID,
):
    dag = DAG(
        dag_id=dag_id,
        default_args=args,
        concurrency=concurrency,
        max_active_runs=max_active_runs,
        schedule_interval=schedule_cron,
        catchup=False,
    )
    with dag:
        operators.update_db_view(postgres_conn_id)

    return dag


globals()[DAG_ID] = create_dag()
