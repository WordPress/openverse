import logging

from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.utils.trigger_rule import TriggerRule
from common.loader import loader, paths, smithsonian_unit_codes, sql


logger = logging.getLogger(__name__)

TIMESTAMP_TEMPLATE = "{{ ts_nodash }}"


def get_file_staging_operator(
    output_dir, minimum_file_age_minutes, identifier=TIMESTAMP_TEMPLATE
):
    return ShortCircuitOperator(
        task_id="stage_oldest_tsv_file",
        python_callable=paths.stage_oldest_tsv_file,
        op_args=[output_dir, identifier, minimum_file_age_minutes],
    )


def get_table_creator_operator(postgres_conn_id, identifier=TIMESTAMP_TEMPLATE):
    return PythonOperator(
        task_id="create_loading_table",
        python_callable=sql.create_loading_table,
        op_args=[postgres_conn_id, identifier],
    )


def get_load_local_data_operator(
    output_dir, postgres_conn_id, overwrite=False, identifier=TIMESTAMP_TEMPLATE
):
    return PythonOperator(
        task_id="load_local_data",
        python_callable=loader.load_local_data,
        op_kwargs={"overwrite": overwrite},
        op_args=[output_dir, postgres_conn_id, identifier],
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )


def get_copy_to_s3_operator(
    output_dir, storage_bucket, aws_conn_id, identifier=TIMESTAMP_TEMPLATE
):
    return PythonOperator(
        task_id="copy_to_s3",
        python_callable=loader.copy_to_s3,
        op_args=[output_dir, storage_bucket, identifier, aws_conn_id],
    )


def get_load_s3_data_operator(
    bucket,
    aws_conn_id,
    postgres_conn_id,
    overwrite=False,
    identifier=TIMESTAMP_TEMPLATE,
):
    return PythonOperator(
        task_id="load_s3_data",
        python_callable=loader.load_s3_data,
        op_kwargs={"overwrite": overwrite},
        op_args=[bucket, aws_conn_id, postgres_conn_id, identifier],
    )


def get_one_failed_switch(identifier):
    return DummyOperator(
        task_id=f"one_failed_{identifier}",
        trigger_rule=TriggerRule.ONE_FAILED,
    )


def get_all_failed_switch(identifier):
    return DummyOperator(
        task_id=f"all_failed_{identifier}",
        trigger_rule=TriggerRule.ALL_FAILED,
    )


def get_one_success_switch(identifier):
    return DummyOperator(
        task_id=f"one_success_{identifier}",
        trigger_rule=TriggerRule.ONE_SUCCESS,
    )


def get_all_done_switch(identifier):
    return DummyOperator(
        task_id=f"all_done_{identifier}",
        trigger_rule=TriggerRule.ALL_DONE,
    )


def get_file_deletion_operator(output_dir, identifier=TIMESTAMP_TEMPLATE):
    return PythonOperator(
        task_id="delete_staged_file",
        python_callable=paths.delete_staged_file,
        op_args=[output_dir, identifier],
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )


def get_drop_table_operator(postgres_conn_id, identifier=TIMESTAMP_TEMPLATE):
    return PythonOperator(
        task_id="drop_loading_table",
        python_callable=sql.drop_load_table,
        op_args=[postgres_conn_id, identifier],
        trigger_rule=TriggerRule.ALL_DONE,
    )


def get_failure_moving_operator(output_dir, identifier=TIMESTAMP_TEMPLATE):
    return PythonOperator(
        task_id="move_staged_failures",
        python_callable=paths.move_staged_files_to_failure_directory,
        op_args=[output_dir, identifier],
        trigger_rule=TriggerRule.ONE_SUCCESS,
    )


def get_smithsonian_unit_code_operator(postgres_conn_id):
    return PythonOperator(
        task_id="check_new_smithsonian_unit_codes",
        python_callable=smithsonian_unit_codes.alert_unit_codes_from_api,
        op_args=[postgres_conn_id],
    )


def get_image_expiration_operator(postgres_conn_id, provider):
    return PythonOperator(
        task_id=f"expire_outdated_images_of_{provider}",
        python_callable=sql.expire_old_images,
        op_args=[postgres_conn_id, provider],
    )
