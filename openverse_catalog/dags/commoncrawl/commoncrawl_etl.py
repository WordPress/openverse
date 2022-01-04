import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.emr_create_job_flow import (
    EmrCreateJobFlowOperator,
)
from airflow.providers.amazon.aws.operators.emr_terminate_job_flow import (
    EmrTerminateJobFlowOperator,
)
from airflow.providers.amazon.aws.sensors.emr_job_flow import EmrJobFlowSensor
from airflow.providers.amazon.aws.sensors.s3_key import S3KeySensor
from airflow.providers.amazon.aws.sensors.s3_prefix import S3PrefixSensor
from airflow.utils.trigger_rule import TriggerRule
from commoncrawl.commoncrawl_utils import get_load_s3_task_id, load_file_to_s3


FILE_DIR = os.path.abspath(os.path.dirname(__file__))
CORE_INSTANCE_COUNT = 100
AWS_CONN_ID = os.getenv("AWS_CONN_ID", "aws_test")
EMR_CONN_ID = os.getenv("EMR_CONN_ID", "emr_test")
COMMONCRAWL_BUCKET = os.environ.get("COMMONCRAWL_BUCKET", "not_set")
BUCKET_V2 = "ov-commonsmapper"
CONFIG_SH_KEY = "bootstrap/config-py27.sh"
CONFIG_SH = f"s3://{BUCKET_V2}/{CONFIG_SH_KEY}"
EXTRACT_SCRIPT_S3_KEY = "scripts/ExtractCCLinks.py"
EXTRACT_SCRIPT_S3 = f"s3://{BUCKET_V2}/{EXTRACT_SCRIPT_S3_KEY}"
LOCAL_FILES_DIR = os.path.join(FILE_DIR, "util", "etl")
CONFIG_SH_LOCAL = os.path.join(LOCAL_FILES_DIR, "bootstrap", "config-py27.sh")
EXTRACT_SCRIPT_LOCAL = os.path.join(
    LOCAL_FILES_DIR, "dags/commoncrawl_scripts/scripts", "ExtractCCLinks.py"
)
LOG_URI = f"s3://{BUCKET_V2}/logs/airflow_pipeline"
RAW_PROCESS_JOB_FLOW_NAME = "common_crawl_etl_job_flow"
DAG_DEFAULT_ARGS = {
    "owner": "data-eng-admin",
    "depends_on_past": False,
    "start_date": datetime(2019, 1, 15),
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=60),
}

CC_INDEX_TEMPLATE = "CC-MAIN-{{ execution_date.strftime('%Y-%V') }}"
JOB_FLOW_OVERRIDES = {
    "Applications": [{"Name": "hive"}, {"Name": "spark"}, {"Name": "pig"}],
    "BootstrapActions": [
        {
            "Name": "pip_install_deps",
            "ScriptBootstrapAction": {"Path": CONFIG_SH},
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
                "spark.dynamicAllocation.enabled": "false",
            },
        },
        {
            "Classification": "emrfs-site",
            "Properties": {"fs.s3.enableServerSideEncryption": "true"},
        },
    ],
    "Instances": {
        "Ec2KeyName": "cc-catalog",
        "Ec2SubnetIds": [
            "subnet-8ffebeb0",
            # "subnet-9210d39d",
            # "subnet-99d0dcd2",
            # "subnet-9a7145fe",
            # "subnet-cf2d5692",
            # "subnet-d52562fa",
        ],
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
                                "VolumeType": "gp2",
                            },
                            "VolumesPerInstance": 1,
                        }
                    ]
                },
                "InstanceCount": CORE_INSTANCE_COUNT,
                "InstanceRole": "CORE",
                "InstanceType": "c4.8xlarge",
                "Market": "SPOT",
                "Name": "common_crawl_etl_job_flow_core",
            },
            {
                "EbsConfiguration": {
                    "EbsBlockDeviceConfigs": [
                        {
                            "VolumeSpecification": {
                                "SizeInGB": 32,
                                "VolumeType": "gp2",
                            },
                            "VolumesPerInstance": 1,
                        }
                    ]
                },
                "InstanceCount": 1,
                "InstanceRole": "MASTER",
                "InstanceType": "m4.xlarge",
                "Market": "ON_DEMAND",
                "Name": "common_crawl_etl_job_flow_master",
            },
        ],
        "KeepJobFlowAliveWhenNoSteps": False,
        "TerminationProtected": False,
    },
    "JobFlowRole": "DataPipelineDefaultResourceRole",
    "LogUri": LOG_URI,
    "Name": RAW_PROCESS_JOB_FLOW_NAME,
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
                    # This was "--default" previously but a task within the DAG
                    # modified it on DAG parse time to be this value.
                    CC_INDEX_TEMPLATE,
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
            "Value": "Find links to CC licensed content in Common Crawl.",
        },
        {"Key": "cc:product", "Value": "cccatalog"},
        {"Key": "cc:team", "Value": "cc-search"},
        {"Key": "Name", "Value": "Common Crawl Data Pipeline"},
    ],
    "VisibleToAllUsers": True,
}


with DAG(
    dag_id="commoncrawl_etl_workflow",
    default_args=DAG_DEFAULT_ARGS,
    start_date=datetime(1970, 1, 1),
    schedule_interval="0 0 * * 1",
    max_active_tasks=1,
    catchup=False,
    tags=["commoncrawl"],
) as dag:
    check_for_cc_index = S3PrefixSensor(
        task_id="check_for_cc_index",
        retries=0,
        aws_conn_id=AWS_CONN_ID,
        bucket_name=COMMONCRAWL_BUCKET,
        prefix=f"crawl-data/{CC_INDEX_TEMPLATE}",
        poke_interval=60,
        timeout=60 * 60 * 24 * 3,
        soft_fail=True,
        mode="reschedule",
    )

    check_for_wat_file = S3KeySensor(
        task_id="check_for_wat_file",
        retries=0,
        aws_conn_id=AWS_CONN_ID,
        bucket_name=COMMONCRAWL_BUCKET,
        bucket_key=f"crawl-data/{CC_INDEX_TEMPLATE}/wat.paths.gz",
        poke_interval=60,
        timeout=60 * 60 * 24 * 3,
        soft_fail=True,
        mode="reschedule",
    )

    cluster_bootstrap_loader = PythonOperator(
        task_id=get_load_s3_task_id(CONFIG_SH_KEY),
        python_callable=load_file_to_s3,
        op_args=[CONFIG_SH_LOCAL, CONFIG_SH_KEY, BUCKET_V2, AWS_CONN_ID],
    )

    extract_script_loader = PythonOperator(
        task_id=get_load_s3_task_id(EXTRACT_SCRIPT_S3_KEY),
        python_callable=load_file_to_s3,
        op_args=[
            EXTRACT_SCRIPT_LOCAL,
            EXTRACT_SCRIPT_S3_KEY,
            BUCKET_V2,
            AWS_CONN_ID,
        ],
    )

    job_flow_creator = EmrCreateJobFlowOperator(
        task_id=f"create_{RAW_PROCESS_JOB_FLOW_NAME}",
        job_flow_overrides=JOB_FLOW_OVERRIDES,
        aws_conn_id=AWS_CONN_ID,
        emr_conn_id=EMR_CONN_ID,
    )

    job_sensor = EmrJobFlowSensor(
        task_id=f"check_{RAW_PROCESS_JOB_FLOW_NAME}",
        timeout=60 * 60 * 7,
        mode="reschedule",
        retries=0,
        job_flow_id=job_flow_creator.task_id,
        aws_conn_id=AWS_CONN_ID,
    )

    job_flow_terminator = EmrTerminateJobFlowOperator(
        task_id=f"terminate_{RAW_PROCESS_JOB_FLOW_NAME}",
        job_flow_id=job_flow_creator.task_id,
        aws_conn_id=AWS_CONN_ID,
        trigger_rule=TriggerRule.ALL_DONE,
    )

    (
        check_for_cc_index
        >> check_for_wat_file
        >> [extract_script_loader, cluster_bootstrap_loader]
        >> job_flow_creator
        >> job_sensor
        >> job_flow_terminator
    )
    [job_flow_creator, job_sensor, job_flow_terminator]
