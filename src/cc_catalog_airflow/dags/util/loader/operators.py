import logging

from airflow.operators.python_operator import PythonOperator
from airflow.operators.python_operator import ShortCircuitOperator
from airflow.utils.trigger_rule import TriggerRule

from util.loader import loader, paths, sql

logger = logging.getLogger(__name__)

TIMESTAMP_TEMPLATE = '{{ ts_nodash }}'


def get_file_staging_operator(
        dag,
        output_dir,
        minimum_file_age_minutes,
        identifier=TIMESTAMP_TEMPLATE
):
    return ShortCircuitOperator(
        task_id='stage_oldest_tsv_file',
        python_callable=paths.stage_oldest_tsv_file,
        op_args=[output_dir, identifier, minimum_file_age_minutes],
        dag=dag
    )


def get_table_creator_operator(
        dag,
        postgres_conn_id,
        identifier=TIMESTAMP_TEMPLATE
):
    return PythonOperator(
        task_id='create_loading_table',
        python_callable=sql.create_loading_table,
        op_args=[postgres_conn_id, identifier],
        dag=dag
    )


def get_loader_operator(
        dag,
        output_dir,
        postgres_conn_id,
        identifier=TIMESTAMP_TEMPLATE
):
    return PythonOperator(
        task_id='load_data',
        python_callable=loader.load_data,
        op_args=[output_dir, postgres_conn_id, identifier],
        dag=dag
    )


def get_file_deletion_operator(
        dag,
        output_dir,
        identifier=TIMESTAMP_TEMPLATE
):
    return PythonOperator(
        task_id='delete_staged_file',
        python_callable=paths.delete_staged_file,
        op_args=[output_dir, identifier],
        trigger_rule=TriggerRule.ALL_SUCCESS,
        dag=dag,
    )


def get_drop_table_operator(
        dag,
        postgres_conn_id,
        identifier=TIMESTAMP_TEMPLATE
):
    return PythonOperator(
        task_id='drop_loading_table',
        python_callable=sql.drop_load_table,
        op_args=[postgres_conn_id, identifier],
        trigger_rule=TriggerRule.ALL_DONE,
        dag=dag,
    )


def get_failure_moving_operator(
        dag,
        output_dir,
        identifier=TIMESTAMP_TEMPLATE
):
    return PythonOperator(
        task_id='move_staged_failures',
        python_callable=paths.move_staged_files_to_failure_directory,
        op_args=[output_dir, identifier],
        trigger_rule=TriggerRule.ONE_FAILED,
        dag=dag
    )
