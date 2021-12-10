"""
This file defines an Apache Airflow DAG that completely wipes out the
PostgreSQL relations and functions involved in calculating our
standardized popularity metric. It then recreates relations and
functions to make the calculation, and performs an initial calculation.
The results are available in the `image_view` materialized view.

This should only be run when new SQL code is deployed for the calculation.
"""
import os
from datetime import datetime, timedelta

from airflow import DAG
from common import slack
from common.popularity import operators


DAG_ID = "recreate_audio_popularity_calculation"
DB_CONN_ID = os.getenv("OPENLEDGER_CONN_ID", "postgres_openledger_testing")
CONCURRENCY = 1
SCHEDULE_CRON = None

DAG_DEFAULT_ARGS = {
    "owner": "data-eng-admin",
    "depends_on_past": False,
    "start_date": datetime(2020, 6, 15),
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(seconds=3600),
    "on_failure_callback": slack.on_failure_callback,
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
        tags=["database"],
    )
    with dag:
        drop_relations = operators.drop_media_popularity_relations(
            postgres_conn_id,
            "audio",
        )
        drop_functions = operators.drop_media_popularity_functions(
            postgres_conn_id,
            "audio",
        )
        create_metrics = operators.create_media_popularity_metrics(
            postgres_conn_id,
            "audio",
        )
        update_metrics = operators.update_media_popularity_metrics(
            postgres_conn_id,
            "audio",
        )
        create_percentile = operators.create_media_popularity_percentile(
            postgres_conn_id,
            "audio",
        )
        create_constants = operators.create_media_popularity_constants(
            postgres_conn_id,
            "audio",
        )
        create_popularity = operators.create_media_standardized_popularity(
            postgres_conn_id,
            "audio",
        )
        create_db_view = operators.create_db_view(
            postgres_conn_id,
            "audio",
        )

        (
            [drop_relations, drop_functions]
            >> create_metrics
            >> [update_metrics, create_percentile]
            >> create_constants
            >> create_popularity
            >> create_db_view
        )

    return dag


globals()[DAG_ID] = create_dag()
