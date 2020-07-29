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
AWS_CONN_ID = os.getenv('AWS_CONN_ID', 'no_aws_conn_id')
CCCATALOG_STORAGE_BUCKET = os.getenv('CCCATALOG_STORAGE_BUCKET')
MINIMUM_FILE_AGE_MINUTES = int(os.getenv('LOADER_FILE_AGE', 15))
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
        aws_conn_id=AWS_CONN_ID,
        output_dir=OUTPUT_DIR_PATH,
        storage_bucket=CCCATALOG_STORAGE_BUCKET,
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
        copy_to_s3 = operators.get_copy_to_s3_operator(
            dag,
            output_dir,
            storage_bucket,
            aws_conn_id
        )
        load_s3_data = operators.get_load_s3_data_operator(
            dag,
            storage_bucket,
            aws_conn_id,
            postgres_conn_id
        )
        one_failed_s3 = operators.get_one_failed_switch(
            dag,
            's3'
        )
        load_local_data = operators.get_load_local_data_operator(
            dag,
            output_dir,
            postgres_conn_id
        )
        one_success_save = operators.get_one_success_switch(
            dag,
            'save'
        )
        all_done_save = operators.get_all_done_switch(
            dag,
            'save'
        )
        all_failed_save = operators.get_all_failed_switch(
            dag,
            'save'
        )
        delete_staged_file = operators.get_file_deletion_operator(
            dag,
            output_dir
        )
        one_failed_delete = operators.get_one_failed_switch(
            dag,
            'delete'
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
            >> [create_loading_table, copy_to_s3]
            >> load_s3_data
        )
        [copy_to_s3, load_s3_data] >> one_failed_s3
        [create_loading_table, one_failed_s3] >> load_local_data
        [copy_to_s3, load_local_data] >> one_success_save
        [copy_to_s3, load_local_data] >> all_done_save
        [copy_to_s3, load_local_data] >> all_failed_save
        [one_success_save, all_done_save] >> delete_staged_file
        [load_s3_data, load_local_data] >> drop_loading_table
        delete_staged_file >> one_failed_delete
        [one_failed_delete, all_failed_save] >> move_staged_failures
    return dag


globals()[DAG_ID] = create_dag()
