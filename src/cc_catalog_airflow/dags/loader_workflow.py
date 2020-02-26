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

DAG_ID = 'DB_loader'
DB_CONN_ID = 'postgres_openledger_upstream'
FILE_CHANGE_WAIT = 1

OUTPUT_DIR_PATH = os.path.realpath(os.environ['OUTPUT_DIR'])
FAILURE_SUB_DIRECTORY = 'db_loader_failures'
FAILURE_DIR_PATH = os.path.join(OUTPUT_DIR_PATH, FAILURE_SUB_DIRECTORY)
STAGING_SUB_DIRECTORY = 'db_loader_staging'
STAGING_DIR_PATH = os.path.join(OUTPUT_DIR_PATH, STAGING_SUB_DIRECTORY)

DAG_DEFAULT_ARGS = {
    'owner': 'data-eng-admin',
    'depends_on_past': False,
    'start_date': datetime(2020, 1, 15),
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(seconds=15),
}


def create_dag(args=DAG_DEFAULT_ARGS, dag_id=DAG_ID):
    dag = DAG(
        dag_id=dag_id,
        default_args=args,
        concurrency=1,
        max_active_runs=1,
        schedule_interval='* * * * *',
        catchup=False
    )

    with dag:
        stage_oldest_tsv_file = get_file_staging_operator(dag)
        create_table = get_table_creator_operator(dag)
        load_data = get_loader_operator(dag)
        delete_file = get_file_deletion_operator(dag)
        move_failures = get_failure_moving_operator(dag)
        (
            stage_oldest_tsv_file
            >> create_table
            >> load_data
            >> delete_file
        )
        [
            stage_oldest_tsv_file,
            create_table, load_data,
            delete_file
        ] >> move_failures
    return dag


def get_file_staging_operator(dag):
    return ShortCircuitOperator(
        task_id='stage_oldest_tsv_file',
        python_callable=_stage_oldest_tsv_file,
        dag=dag
    )


def get_table_creator_operator(dag):
    return PythonOperator(
        task_id='create_table',
        python_callable=sql.create_if_not_exists_loading_table,
        op_args=[DB_CONN_ID],
        dag=dag
    )


def get_loader_operator(dag):
    return PythonOperator(
        task_id='load_data',
        python_callable=_load_data,
        dag=dag
    )


def get_file_deletion_operator(dag):
    return PythonOperator(
        task_id='delete_file',
        python_callable=_delete_old_records_and_file,
        trigger_rule=TriggerRule.ALL_SUCCESS,
        dag=dag,
    )


def get_failure_moving_operator(dag):
    return PythonOperator(
        task_id='move_failures',
        python_callable=_move_staged_files_to_failure_directory,
        trigger_rule=TriggerRule.ONE_FAILED,
        dag=dag
    )


def _stage_oldest_tsv_file(staging_directory=STAGING_DIR_PATH):
    tsv_file_name = _get_oldest_file()
    tsv_found = tsv_file_name is not None
    if tsv_found:
        _move_file(tsv_file_name, staging_directory)
    return tsv_found


def _load_data(
        staging_directory=STAGING_DIR_PATH,
        postgres_conn_id=DB_CONN_ID
):
    tsv_file_name = _get_staged_file()
    sql.import_data_to_intermediate_table(postgres_conn_id, tsv_file_name)
    sql.upsert_records_to_image_table(postgres_conn_id)


def _delete_old_records_and_file(postgres_conn_id=DB_CONN_ID):
    sql.delete_load_table_data(postgres_conn_id)

    tsv_file_name = _get_staged_file()
    logger.info(f'Deleting {tsv_file_name}')
    os.remove(tsv_file_name)


def _get_oldest_file(
        minimum_age_minutes=FILE_CHANGE_WAIT,
        output_dir=OUTPUT_DIR_PATH
):
    oldest_file_name = None
    logger.info(f'getting files from {output_dir}')
    path_list = _get_full_tsv_paths(output_dir)
    logger.info(f'found files:\n{path_list}')
    last_modified_list = [(p, os.stat(p).st_mtime) for p in path_list]
    logger.info(f'last_modified_list:\n{last_modified_list}')

    if not last_modified_list:
        return

    oldest_file_modified = min(last_modified_list, key=lambda t: t[1])
    cutoff_time = datetime.now() - timedelta(minutes=minimum_age_minutes)

    if datetime.fromtimestamp(oldest_file_modified[1]) <= cutoff_time:
        oldest_file_name = oldest_file_modified[0]
    else:
        logger.info(f'no file found older than {minimum_age_minutes} minutes.')

    return oldest_file_name


def _get_staged_file(staging_directory=STAGING_DIR_PATH):
    path_list = _get_full_tsv_paths(staging_directory)
    assert len(path_list) == 1
    return path_list[0]


def _get_full_tsv_paths(directory):
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f[-4:] == '.tsv'
    ]


def _move_staged_files_to_failure_directory(
        staging_directory=STAGING_DIR_PATH,
        failure_directory=FAILURE_DIR_PATH
):
    staged_file_list = _get_full_tsv_paths(staging_directory)
    for file_path in staged_file_list:
        _move_file(file_path, failure_directory)


def _create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)


def _move_file(file_path, new_directory):
    _create_directory_if_not_exists(new_directory)
    new_file_path = os.path.join(new_directory, os.path.basename(file_path))
    logger.info(f'Moving {file_path} to {new_file_path}')
    os.rename(file_path, new_file_path)


globals()[DAG_ID] = create_dag()
