"""
This file defines an Apache Airflow DAG that completely wipes out the
PostgreSQL relations and functions involved in calculating our
standardized popularity metric. It then recreates relations and
functions to make the calculation, and performs an initial calculation.
The results are available in the `image_view` materialized view.

This should only be run when new SQL code is deployed for the calculation.
"""
from datetime import datetime, timedelta
import logging
import os

from airflow import DAG

from util.popularity import operators
from util.operator_util import get_log_operator


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

DAG_ID = 'recreate_image_popularity_calculation'
DB_CONN_ID = os.getenv('OPENLEDGER_CONN_ID', 'postgres_openledger_testing')
CONCURRENCY = 1
SCHEDULE_CRON = None

DAG_DEFAULT_ARGS = {
    'owner': 'data-eng-admin',
    'depends_on_past': False,
    'start_date': datetime(2020, 6, 15),
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(seconds=3600),
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
        catchup=False
    )
    with dag:
        start_task = get_log_operator(dag, DAG_ID, 'Starting')
        drop_relations = operators.drop_media_popularity_relations(
            dag, postgres_conn_id,
        )
        drop_functions = operators.drop_media_popularity_functions(
            dag, postgres_conn_id,
        )
        create_metrics = operators.create_media_popularity_metrics(
            dag, postgres_conn_id
        )
        update_metrics = operators.update_media_popularity_metrics(
            dag, postgres_conn_id
        )
        create_percentile = operators.create_media_popularity_percentile(
            dag, postgres_conn_id
        )
        create_constants = operators.create_media_popularity_constants(
            dag, postgres_conn_id
        )
        create_popularity = operators.create_media_standardized_popularity(
            dag, postgres_conn_id
        )
        create_image_view = operators.create_db_view(
            dag, postgres_conn_id
        )
        end_task = get_log_operator(dag, DAG_ID, 'Finished')

        (
            start_task
            >> [drop_relations, drop_functions]
            >> create_metrics
            >> [update_metrics, create_percentile]
            >> create_constants
            >> create_popularity
            >> create_image_view
            >> end_task
        )

    return dag


globals()[DAG_ID] = create_dag()
