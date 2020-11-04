from datetime import datetime, timedelta
import logging
import os

from airflow import DAG
from airflow.contrib.operators.emr_create_job_flow_operator import (
    EmrCreateJobFlowOperator
)
from airflow.contrib.operators.emr_terminate_job_flow_operator import (
    EmrTerminateJobFlowOperator
)
from airflow.contrib.sensors.emr_job_flow_sensor import EmrJobFlowSensor
from airflow.hooks.S3_hook import S3Hook
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

FILE_DIR = os.path.abspath(os.path.dirname(__file__))
CORE_INSTANCE_COUNT = 100
AWS_CONN_ID = os.getenv("AWS_CONN_ID", "aws_test")
BUCKET_V2 = "commonsmapper-v2"
CONFIG_SH_KEY = "bootstrap/config-py27.sh"
CONFIG_SH = f"s3://{BUCKET_V2}/{CONFIG_SH_KEY}"
EXTRACT_SCRIPT_S3_KEY = "scripts/ExtractCCLinks_testing.py"
EXTRACT_SCRIPT_S3 = f"s3://{BUCKET_V2}/{EXTRACT_SCRIPT_S3_KEY}"
LOCAL_FILES_DIR = os.path.join(FILE_DIR, "util", "etl")
CONFIG_SH_LOCAL = os.path.join(LOCAL_FILES_DIR, "bootstrap", "config-py27.sh")
EXTRACT_SCRIPT_LOCAL = os.path.join(
    LOCAL_FILES_DIR, "scripts", "ExtractCCLinks.py"
)
LOG_URI = f"s3://{BUCKET_V2}/logs/airflow_pipeline"

DAG_DEFAULT_ARGS = {
    'owner': 'data-eng-admin',
    'depends_on_past': False,
    'start_date': datetime(2019, 1, 15),
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=60),
}

JOB_FLOW_OVERRIDES = {
    "Applications": [{"Name": "hive"}, {"Name": "spark"}, {"Name": "pig"}],
    "BootstrapActions": [
        {
            "Name": "pip_install_deps",
            "ScriptBootstrapAction": {"Path": CONFIG_SH}
        }
    ],
    "Configurations": [
        {
            "Classification": "spark-defaults",
            "Properties": {
                "spark.executor.memory": "12G",
                "spark.driver.memory": "12G",
                "spark.driver.cores": "8",
                "spark.default.parallelism": "4784",
                "spark.executor.heartbeatInterval": "10000s",
                "spark.network.timeout": "12000s",
                "spark.executor.cores": "8",
                "spark.executor.instances": "300",
                "spark.dynamicAllocation.enabled": "false"
            }
        }, {
            "Classification": "emrfs-site",
            "Properties": {"fs.s3.enableServerSideEncryption": "true"}
        }
    ],
    "Instances": {
        "Ec2KeyName": "cc-catalog",
        "Ec2SubnetId": "subnet-d52562fa",
        "EmrManagedSlaveSecurityGroup": "sg-0a7b0a7d",
        "EmrManagedMasterSecurityGroup": "sg-226d1c55",
        "InstanceGroups": [
            {
                "BidPrice": "0.75",
                "EbsConfiguration": {
                    "EbsBlockDeviceConfigs": [
                        {
                            "VolumeSpecification": {
                                "SizeInGB": 32,
                                "VolumeType": "gp2"
                            },
                            "VolumesPerInstance": 1
                        }
                    ]
                },
                "InstanceCount": CORE_INSTANCE_COUNT,
                "InstanceRole": "CORE",
                "InstanceType": "c4.8xlarge",
                "Market": "SPOT",
                "Name": "common_crawl_etl_job_flow_core"
            },
            {
                "EbsConfiguration": {
                    "EbsBlockDeviceConfigs": [
                        {
                            "VolumeSpecification": {
                                "SizeInGB": 32,
                                "VolumeType": "gp2"
                            },
                            "VolumesPerInstance": 1
                        }
                    ]
                },
                "InstanceCount": 1,
                "InstanceRole": "MASTER",
                "InstanceType": "m4.xlarge",
                "Market": "ON_DEMAND",
                "Name": "common_crawl_etl_job_flow_master",
            }
        ],
        "KeepJobFlowAliveWhenNoSteps": False,
        "TerminationProtected": False,
    },
    "JobFlowRole": "DataPipelineDefaultResourceRole",
    "LogUri": LOG_URI,
    "Name": "common_crawl_etl_job_flow",
    "ReleaseLabel": "emr-5.11.0",
    "ScaleDownBehavior": "TERMINATE_AT_TASK_COMPLETION",
    "ServiceRole": "DataPipelineDefaultRole",
    "Steps": [
        {
            "ActionOnFailure": "CONTINUE",
            "HadoopJarStep": {
                "Args": [
                    "spark-submit",
                    "--deploy-mode",
                    "cluster",
                    "--master",
                    "yarn",
                    EXTRACT_SCRIPT_S3,
                    "--default"
                ],
                "Jar": "command-runner.jar",
            },
            "Name": "extract_cc_links",
        }
    ],
    "Tags": [
        {"Key": "cc:environment", "Value": "production"},
        {
            "Key": "cc:purpose",
            "Value": "Find links to CC licensed content in Common Crawl."
        },
        {"Key": "cc:product", "Value": "cccatalog"},
        {"Key": "cc:team", "Value": "cc-search"},
        {"Key": "Name", "Value": "Common Crawl Data Pipeline"}
    ],
    "VisibleToAllUsers": True,
}


def load_file_to_s3(local_file, remote_key, bucket, aws_conn_id=AWS_CONN_ID):
    s3 = S3Hook(aws_conn_id=aws_conn_id)
    s3.load_file(local_file, remote_key, replace=True, bucket_name=bucket)


with DAG(
        dag_id="commoncrawl_etl_workflow",
        default_args=DAG_DEFAULT_ARGS,
        start_date=datetime(1970, 1, 1),
        schedule_interval=None,
        concurrency=1,
) as dag:

    job_start_logger = BashOperator(
        task_id="log_job_started",
        bash_command="echo Started ETL Job Flow at $(date)",
        trigger_rule=TriggerRule.ALL_SUCCESS
    )

    cluster_bootstrap_loader = PythonOperator(
        task_id="load_config_script_to_s3",
        python_callable=load_file_to_s3,
        op_args=[CONFIG_SH_LOCAL, CONFIG_SH_KEY, BUCKET_V2]
    )

    extract_script_loader = PythonOperator(
        task_id="load_extract_script_to_s3",
        python_callable=load_file_to_s3,
        op_args=[EXTRACT_SCRIPT_LOCAL, EXTRACT_SCRIPT_S3_KEY, BUCKET_V2]
    )

    job_flow_creator = EmrCreateJobFlowOperator(
        task_id="create_etl_job_flow",
        job_flow_overrides=JOB_FLOW_OVERRIDES,
        aws_conn_id=AWS_CONN_ID,
        emr_conn_id="emr_empty",
    )

    job_sensor = EmrJobFlowSensor(
        timeout=60 * 60 * 7,
        mode="reschedule",
        task_id="check_job_flow",
        retries=0,
        job_flow_id=(
            "{{"
            " task_instance.xcom_pull("
            "task_ids='create_etl_job_flow', key='return_value'"
            ")"
            " }}"
        ),
        aws_conn_id=AWS_CONN_ID,
    )
    job_flow_terminator = EmrTerminateJobFlowOperator(
        task_id="terminate_etl_job_flow",
        job_flow_id=(
            "{{"
            " task_instance.xcom_pull("
            "task_ids='create_etl_job_flow', key='return_value'"
            ")"
            " }}"
        ),
        aws_conn_id=AWS_CONN_ID,
        trigger_rule=TriggerRule.ALL_DONE
    )
    job_done_logger = BashOperator(
        task_id="log_job_done",
        bash_command="echo Finished ETL Job Flow at $(date)",
        trigger_rule=TriggerRule.ALL_SUCCESS
    )

    (
        job_start_logger
        >> [extract_script_loader, cluster_bootstrap_loader]
        >> job_flow_creator >> job_sensor >> job_flow_terminator
    )
    [job_flow_creator, job_sensor, job_flow_terminator] >> job_done_logger
