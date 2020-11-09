from airflow.contrib.operators.emr_create_job_flow_operator import (
    EmrCreateJobFlowOperator,
)
from airflow.contrib.operators.emr_terminate_job_flow_operator import (
    EmrTerminateJobFlowOperator,
)
from airflow.contrib.sensors.emr_job_flow_sensor import EmrJobFlowSensor
from airflow.hooks.S3_hook import S3Hook
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.trigger_rule import TriggerRule


def load_file_to_s3(local_file, remote_key, bucket, aws_conn_id):
    s3 = S3Hook(aws_conn_id=aws_conn_id)
    s3.load_file(local_file, remote_key, replace=True, bucket_name=bucket)


def get_log_operator(dag, status):
    return BashOperator(
        task_id=f"log_{dag.dag_id}_{status}",
        bash_command=f"echo {status} {dag.dag_id} at $(date)",
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )


def get_load_to_s3_operator(local_file, s3_key, s3_bucket, aws_conn_id):
    return PythonOperator(
        task_id=f"load_{s3_key.replace('/', '_').replace('.', '_')}_to_s3",
        python_callable=load_file_to_s3,
        op_args=[local_file, s3_key, s3_bucket, aws_conn_id],
    )


def get_create_job_flow_operator(
    job_flow_name,
    job_flow_overrides,
    aws_conn_id,
    emr_conn_id,
):
    return EmrCreateJobFlowOperator(
        task_id=_get_job_flow_creator_task_id(job_flow_name),
        job_flow_overrides=job_flow_overrides,
        aws_conn_id=aws_conn_id,
        emr_conn_id=emr_conn_id,
    )


def get_job_sensor(timeout, job_flow_name, aws_conn_id):
    creator_task_id = _get_job_flow_creator_task_id(job_flow_name)
    return EmrJobFlowSensor(
        timeout=timeout,
        mode="reschedule",
        task_id=f"check_{job_flow_name}",
        retries=0,
        job_flow_id=_get_job_flow_id_template(creator_task_id),
        aws_conn_id=aws_conn_id,
    )


def get_job_terminator(job_flow_name, aws_conn_id):
    creator_task_id = _get_job_flow_creator_task_id(job_flow_name)
    return EmrTerminateJobFlowOperator(
        task_id=f"terminate_{job_flow_name}",
        job_flow_id=_get_job_flow_id_template(creator_task_id),
        aws_conn_id=aws_conn_id,
        trigger_rule=TriggerRule.ALL_DONE,
    )


def _get_job_flow_creator_task_id(job_flow_name):
    return f"create_{job_flow_name}"


def _get_job_flow_id_template(creator_task_id):
    puller_args = f"task_ids='{creator_task_id}', key='return_value'"
    return f"{{{{ task_instance.xcom_pull({puller_args}) }}}}"
