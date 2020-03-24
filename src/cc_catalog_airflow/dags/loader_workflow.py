from datetime import datetime, timedelta
import logging
import os
from airflow import DAG

from util.loader import operators


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

DAG_ID = 'tsv_to_postgres_loader'
DB_CONN_ID = os.getenv('OPENLEDGER_CONN_ID', 'postgres_openledger_testing')
MINIMUM_FILE_AGE_MINUTES = 1
CONCURRENCY = 5
SCHEDULE_CRON = '* * * * *'

OUTPUT_DIR_PATH = os.path.realpath(os.getenv('OUTPUT_DIR', '/tmp/'))


DAG_DEFAULT_ARGS = {
    'owner': 'data-eng-admin',
    'depends_on_past': False,
    'start_date': datetime(2020, 1, 15),
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(seconds=15),
}


def create_dag(
        dag_id=DAG_ID,
        args=DAG_DEFAULT_ARGS,
        concurrency=CONCURRENCY,
        max_active_runs=CONCURRENCY,
        schedule_cron=SCHEDULE_CRON,
        postgres_conn_id=DB_CONN_ID,
        output_dir=OUTPUT_DIR_PATH,
        minimum_file_age_minutes=MINIMUM_FILE_AGE_MINUTES
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
        stage_oldest_tsv_file = operators.get_file_staging_operator(
            dag,
            output_dir,
            minimum_file_age_minutes
        )
        create_loading_table = operators.get_table_creator_operator(
            dag,
            postgres_conn_id
        )
        load_data = operators.get_loader_operator(
            dag,
            output_dir,
            postgres_conn_id
        )
        delete_staged_file = operators.get_file_deletion_operator(
            dag,
            output_dir
        )
        drop_loading_table = operators.get_drop_table_operator(
            dag,
            postgres_conn_id
        )
        move_staged_failures = operators.get_failure_moving_operator(
            dag,
            output_dir
        )
        (
            stage_oldest_tsv_file
            >> create_loading_table
            >> load_data
            >> [delete_staged_file, drop_loading_table]
        )
        [
            stage_oldest_tsv_file,
            create_loading_table,
            load_data,
            delete_staged_file,
            drop_loading_table
        ] >> move_staged_failures
    return dag


globals()[DAG_ID] = create_dag()
