import logging
import os
from datetime import datetime, timedelta

from airflow import DAG
from common.etl import operators


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

FILE_DIR = os.path.abspath(os.path.dirname(__file__))
CORE_INSTANCE_COUNT = 100
AWS_CONN_ID = os.getenv("AWS_CONN_ID", "aws_test")
EMR_CONN_ID = os.getenv("EMR_CONN_ID", "emr_test")
BUCKET_V2 = "commonsmapper-v2"
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
                    "--default",
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
    concurrency=1,
    catchup=False,
) as dag:
    check_for_cc_index = operators.get_check_cc_index_in_s3_sensor(
        AWS_CONN_ID,
    )

    check_for_wat_file = operators.get_check_wat_file_in_s3_sensor(
        AWS_CONN_ID,
    )

    cluster_bootstrap_loader = operators.get_load_to_s3_operator(
        CONFIG_SH_LOCAL,
        CONFIG_SH_KEY,
        BUCKET_V2,
        AWS_CONN_ID,
    )

    extract_script_loader = operators.get_load_to_s3_operator(
        EXTRACT_SCRIPT_LOCAL,
        EXTRACT_SCRIPT_S3_KEY,
        BUCKET_V2,
        AWS_CONN_ID,
    )

    job_flow_creator = operators.get_create_job_flow_operator(
        RAW_PROCESS_JOB_FLOW_NAME, JOB_FLOW_OVERRIDES, AWS_CONN_ID, EMR_CONN_ID
    )

    job_sensor = operators.get_job_sensor(
        60 * 60 * 7,
        RAW_PROCESS_JOB_FLOW_NAME,
        AWS_CONN_ID,
    )

    job_flow_terminator = operators.get_job_terminator(
        RAW_PROCESS_JOB_FLOW_NAME,
        AWS_CONN_ID,
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
