import os
import logging as log
from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from util.popularity.sql import (
    upload_normalized_popularity, build_popularity_dump_query,
    dump_selection_to_tsv
)
from util.popularity.math import (
    generate_popularity_tsv, get_percentiles
)
from util.operator_util import get_log_operator
"""
Dump all of the popularity data to the disk, compute the popularity score for
each row, and load it back into the database.

See `util.popularity.math` for a more complete explanation of how popularity is
calculated.
"""

DAG_ID = "popularity_workflow_dag"
DAG_DEFAULT_ARGS = {
    'owner': 'data-eng-admin',
    'depends_on_past': False,
    'start_date': datetime(2020, 1, 1),
    'email_on_retry': False,
    'retries': 0,
}

# The fields in the `meta_data` column that factor into the popularity data
# calculation.
popularity_fields = [
    'global_usage_count',
    'views'
]

DB_CONN_ID = os.getenv('OPENLEDGER_CONN_ID', 'postgres_openledger_testing')

POPULARITY_DUMP_DEST = os.path.join(
    os.getenv('OUTPUT_DIR'), 'popularity_dump.tsv'
)
NORMALIZED_POPULARITY_DEST = os.path.join(
    os.getenv('OUTPUT_DIR'), 'normalized_popularity_dump.tsv'
)


def get_runner_operator(dag):
    return PythonOperator(
        task_id="popularity_workflow_task",
        python_callable=main,
        depends_on_past=False,
        dag=dag
    )


def create_dag():
    dag = DAG(
        dag_id=DAG_ID,
        default_args=DAG_DEFAULT_ARGS,
        start_date=datetime(2020, 1, 1),
        schedule_interval="@monthly",
        catchup=False
    )
    with dag:
        start_task = get_log_operator(dag, DAG_ID, "Starting")
        run_task = get_runner_operator(dag)
        end_task = get_log_operator(dag, DAG_ID, "Finished")
        start_task >> run_task >> end_task
    return dag


globals()[DAG_ID] = create_dag()


def main():
    log.info('Starting popularity job. Fetching percentiles. . .')
    percentiles = get_percentiles(DB_CONN_ID, popularity_fields)
    dump_query = build_popularity_dump_query(popularity_fields)
    log.info('Creating TSV of popularity data. . .')
    with open(POPULARITY_DUMP_DEST, 'w+') as in_tsv, \
            open(NORMALIZED_POPULARITY_DEST, 'w+') as out_tsv:
        dump_selection_to_tsv(DB_CONN_ID, dump_query, POPULARITY_DUMP_DEST)
        log.info('Normalizing popularity data. . .')
        generate_popularity_tsv(in_tsv, out_tsv, percentiles, popularity_fields)
        log.info('Finished normalizing popularity scores. Uploading. . .')
        upload_normalized_popularity(DB_CONN_ID, NORMALIZED_POPULARITY_DEST)
        log.info('Popularity normalization complete.')
