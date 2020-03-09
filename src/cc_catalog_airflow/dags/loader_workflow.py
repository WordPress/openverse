from datetime import datetime, timedelta
import logging
import os
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.python_operator import ShortCircuitOperator
from airflow.utils.trigger_rule import TriggerRule

from util import sql

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

LOAD_TABLE_NAME_STUB = 'provider_image_data'

OUTPUT_DIR_PATH = os.path.realpath(os.getenv('OUTPUT_DIR', '/tmp/'))
FAILURE_SUBDIRECTORY = 'db_loader_failures'
STAGING_SUBDIRECTORY = 'db_loader_staging'
TIMESTAMP_TEMPLATE = '{{ ts_nodash }}'

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
        stage_oldest_tsv_file = _get_file_staging_operator(
            dag,
            output_dir,
            minimum_file_age_minutes
        )
        create_table = _get_table_creator_operator(
            dag,
            postgres_conn_id
        )
        load_data = _get_loader_operator(
            dag,
            output_dir,
            postgres_conn_id
        )
        delete_file = _get_file_deletion_operator(
            dag,
            output_dir
        )
        drop_table = _get_drop_table_operator(
            dag,
            postgres_conn_id
        )
        move_failures = _get_failure_moving_operator(
            dag,
            output_dir
        )
        (
            stage_oldest_tsv_file
            >> create_table
            >> load_data
            >> [delete_file, drop_table]
        )
        [
            stage_oldest_tsv_file, create_table, load_data,
            delete_file, drop_table
        ] >> move_failures
    return dag


def _get_file_staging_operator(
        dag,
        output_dir,
        minimum_file_age_minutes,
        identifier=TIMESTAMP_TEMPLATE
):
    staging_directory = _get_staging_directory(output_dir, identifier)
    return ShortCircuitOperator(
        task_id='stage_oldest_tsv_file',
        python_callable=_stage_oldest_tsv_file,
        op_args=[output_dir, staging_directory, minimum_file_age_minutes],
        dag=dag
    )


def _get_table_creator_operator(
        dag,
        postgres_conn_id,
        identifier=TIMESTAMP_TEMPLATE
):
    load_table_name = _get_load_table_name(identifier)
    return PythonOperator(
        task_id='create_table',
        python_callable=_create_loading_table,
        op_args=[postgres_conn_id, load_table_name],
        dag=dag
    )


def _get_loader_operator(
        dag,
        output_dir,
        postgres_conn_id,
        identifier=TIMESTAMP_TEMPLATE
):
    staging_directory = _get_staging_directory(output_dir, identifier)
    load_table = _get_load_table_name(identifier)
    return PythonOperator(
        task_id='load_data',
        python_callable=_load_data,
        op_args=[staging_directory, postgres_conn_id, load_table],
        dag=dag
    )


def _get_file_deletion_operator(
        dag,
        output_dir,
        identifier=TIMESTAMP_TEMPLATE
):
    staging_directory = _get_staging_directory(output_dir, identifier)
    return PythonOperator(
        task_id='delete_file',
        python_callable=_delete_old_file,
        op_args=[staging_directory],
        trigger_rule=TriggerRule.ALL_SUCCESS,
        dag=dag,
    )


def _get_drop_table_operator(
        dag,
        postgres_conn_id,
        identifier=TIMESTAMP_TEMPLATE
):
    load_table = _get_load_table_name(identifier)
    return PythonOperator(
        task_id='drop_table',
        python_callable=_drop_loading_table,
        op_args=[postgres_conn_id, load_table],
        trigger_rule=TriggerRule.ALL_DONE,
        dag=dag,
    )


def _get_failure_moving_operator(
        dag,
        output_dir,
        identifier=TIMESTAMP_TEMPLATE
):
    staging_directory = _get_staging_directory(output_dir, identifier)
    failure_directory = _get_failure_directory(output_dir, identifier)
    return PythonOperator(
        task_id='move_failures',
        python_callable=_move_staged_files_to_failure_directory,
        op_args=[staging_directory, failure_directory],
        trigger_rule=TriggerRule.ONE_FAILED,
        dag=dag
    )


def _get_staging_directory(
        output_dir,
        identifier,
        staging_subdirectory=STAGING_SUBDIRECTORY,
):
    return os.path.join(output_dir, staging_subdirectory, identifier)


def _get_failure_directory(
        output_dir,
        identifier,
        failure_subdirectory=FAILURE_SUBDIRECTORY,
):
    return os.path.join(output_dir, failure_subdirectory, identifier)


def _get_load_table_name(
        identifier,
        load_table_name_stub=LOAD_TABLE_NAME_STUB,
):
    return f'{load_table_name_stub}{identifier}'


def _stage_oldest_tsv_file(
        output_dir,
        staging_directory,
        minimum_file_age_minutes
):
    tsv_file_name = _get_oldest_tsv_file(output_dir, minimum_file_age_minutes)
    tsv_found = tsv_file_name is not None
    if tsv_found:
        _move_file(tsv_file_name, staging_directory)
    return tsv_found


def _create_loading_table(postgres_conn_id, load_table):
    sql.create_if_not_exists_loading_table(postgres_conn_id, load_table)


def _load_data(staging_directory, postgres_conn_id, load_table):
    tsv_file_name = _get_staged_file(staging_directory)
    sql.import_data_to_intermediate_table(
        postgres_conn_id,
        tsv_file_name,
        load_table
    )
    sql.upsert_records_to_image_table(postgres_conn_id, load_table)


def _delete_old_file(staging_directory):
    tsv_file_name = _get_staged_file(staging_directory)
    logger.info(f'Deleting {tsv_file_name}')
    os.remove(tsv_file_name)
    logger.info(f'Deleting {staging_directory}')
    os.rmdir(staging_directory)


def _drop_loading_table(postgres_conn_id, load_table):
    sql.drop_load_table(postgres_conn_id, load_table)


def _move_staged_files_to_failure_directory(
        staging_directory,
        failure_directory
):
    staged_file_list = _get_full_tsv_paths(staging_directory)
    for file_path in staged_file_list:
        _move_file(file_path, failure_directory)
    logger.info(f'Deleting {staging_directory}')
    os.rmdir(staging_directory)


def _get_oldest_tsv_file(
        directory,
        minimum_file_age_minutes
):
    oldest_file_name = None
    logger.info(f'getting files from {directory}')
    path_list = _get_full_tsv_paths(directory)
    logger.info(f'found files:\n{path_list}')
    tsv_last_modified_list = [(p, os.stat(p).st_mtime) for p in path_list]
    logger.info(f'last_modified_list:\n{tsv_last_modified_list}')

    if len(tsv_last_modified_list) == 0:
        return

    oldest_file_modified = min(tsv_last_modified_list, key=lambda t: t[1])
    cutoff_time = datetime.now() - timedelta(minutes=minimum_file_age_minutes)

    if datetime.fromtimestamp(oldest_file_modified[1]) <= cutoff_time:
        oldest_file_name = oldest_file_modified[0]
    else:
        logger.info(
            f'no file found older than {minimum_file_age_minutes} minutes.'
        )

    return oldest_file_name


def _move_file(file_path, new_directory):
    os.makedirs(new_directory, exist_ok=True)
    new_file_path = os.path.join(new_directory, os.path.basename(file_path))
    logger.info(f'Moving {file_path} to {new_file_path}')
    os.rename(file_path, new_file_path)


def _get_staged_file(staging_directory):
    path_list = _get_full_tsv_paths(staging_directory)
    assert len(path_list) == 1
    return path_list[0]


def _get_full_tsv_paths(directory):
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f[-4:] == '.tsv'
    ]


globals()[DAG_ID] = create_dag()
