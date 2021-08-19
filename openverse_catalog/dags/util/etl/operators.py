from airflow.providers.amazon.aws.operators.emr_create_job_flow import (
    EmrCreateJobFlowOperator,
)
from airflow.providers.amazon.aws.operators.emr_terminate_job_flow import (
    EmrTerminateJobFlowOperator,
)
from airflow.providers.amazon.aws.sensors.emr_job_flow import EmrJobFlowSensor
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.sensors.s3_prefix import S3PrefixSensor
from airflow.providers.amazon.aws.sensors.s3_key import S3KeySensor
from airflow.utils.trigger_rule import TriggerRule


def get_log_operator(dag, status):
    return BashOperator(
        task_id=f"log_{dag.dag_id}_{status}",
        bash_command=f"echo {status} {dag.dag_id} at $(date)",
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )


def get_check_cc_index_in_s3_sensor(dag, aws_conn_id):
    return S3PrefixSensor(
        task_id="check_for_cc_index",
        retries=0,
        aws_conn_id=aws_conn_id,
        bucket_name="commoncrawl",
        prefix=f"crawl-data/{_get_cc_index_template()}",
        poke_interval=60,
        timeout=60 * 60 * 24 * 3,
        soft_fail=True,
        mode="reschedule",
    )


def get_check_wat_file_in_s3_sensor(dag, aws_conn_id):
    return S3KeySensor(
        task_id="check_for_wat_file",
        retries=0,
        aws_conn_id=aws_conn_id,
        bucket_name="commoncrawl",
        bucket_key=f"crawl-data/{_get_cc_index_template()}/wat.paths.gz",
        poke_interval=60,
        timeout=60 * 60 * 24 * 3,
        soft_fail=True,
        mode="reschedule",
    )


def get_load_to_s3_operator(local_file, s3_key, s3_bucket, aws_conn_id):
    return PythonOperator(
        task_id=f"load_{s3_key.replace('/', '_').replace('.', '_')}_to_s3",
        python_callable=_load_file_to_s3,
        op_args=[local_file, s3_key, s3_bucket, aws_conn_id],
    )


def get_create_job_flow_operator(
    job_flow_name,
    job_flow_overrides,
    aws_conn_id,
    emr_conn_id,
):
    cc_index = _get_cc_index_template()
    job_flow_overrides["Steps"][0]["HadoopJarStep"]["Args"][-1] = cc_index
    print(job_flow_overrides)
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
        job_flow_id=_get_task_return_value_template(creator_task_id),
        aws_conn_id=aws_conn_id,
    )


def get_job_terminator(job_flow_name, aws_conn_id):
    creator_task_id = _get_job_flow_creator_task_id(job_flow_name)
    return EmrTerminateJobFlowOperator(
        task_id=f"terminate_{job_flow_name}",
        job_flow_id=_get_task_return_value_template(creator_task_id),
        aws_conn_id=aws_conn_id,
        trigger_rule=TriggerRule.ALL_DONE,
    )


def _load_file_to_s3(local_file, remote_key, bucket, aws_conn_id):
    s3 = S3Hook(aws_conn_id=aws_conn_id)
    s3.load_file(local_file, remote_key, replace=True, bucket_name=bucket)


def _get_job_flow_creator_task_id(job_flow_name):
    return f"create_{job_flow_name}"


def _get_cc_index_template():
    return "CC-MAIN-{{ execution_date.strftime('%Y-%V') }}"


def _get_task_return_value_template(task_id):
    puller_args = f"task_ids='{task_id}', key='return_value'"
    return f"{{{{ task_instance.xcom_pull({puller_args}) }}}}"
