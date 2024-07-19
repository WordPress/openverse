"""
# Distributed Reindex TaskGroup

This module contains the Airflow tasks used for orchestrating the reindexing of records from the temporary tables in the downstream (API) database, into a new Elasticsearch index. Reindexing is performed on a fleet of indexer worker EC2 instances, with instance creation and termination managed by Airflow.
"""

import logging
import math
from textwrap import dedent
from typing import Sequence
from urllib.parse import urlparse

from airflow import settings
from airflow.decorators import task, task_group
from airflow.exceptions import AirflowSkipException
from airflow.models.connection import Connection
from airflow.providers.amazon.aws.hooks.ec2 import EC2Hook
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.sensors.base import PokeReturnValue
from airflow.utils.trigger_rule import TriggerRule
from requests import Response

from common.constants import (
    AWS_ASG_CONN_ID,
    OPENLEDGER_API_CONN_ID,
    PRODUCTION,
    REFRESH_POKE_INTERVAL,
    Environment,
)
from common.sql import PGExecuteQueryOperator, single_value
from data_refresh.constants import INDEXER_LAUNCH_TEMPLATES, INDEXER_WORKER_COUNTS
from data_refresh.data_refresh_types import DataRefreshConfig


logger = logging.getLogger(__name__)


WORKER_CONN_ID = "indexer_worker_{worker_id}_http_{environment}"


class TempConnectionHTTPOperator(HttpOperator):
    """
    Wrapper around the HTTPOperator which allows templating of the conn_id,
    in order to support using a temporary conn_id passed through XCOMs.
    """

    template_fields: Sequence[str] = (
        "endpoint",
        "data",
        "headers",
        # Extended to allow templating of conn_id
        "http_conn_id",
    )


class TempConnectionHTTPSensor(HttpSensor):
    """
    Wrapper around the HTTPSensor which allows templating of the conn_id,
    in order to support using a temporary conn_id passed through XCOMs.
    """

    template_fields: Sequence[str] = (
        "endpoint",
        "request_params",
        "headers",
        # Extended to allow templating of conn_id
        "http_conn_id",
    )


def response_filter_status_check_endpoint(response: Response) -> str:
    """
    Handle the response from the `trigger_reindex` task.

    This is used to get the status endpoint from the response, which is used to poll for the status
    of the reindexing task.
    """
    status_check_url = response.json()["status_check"]
    return urlparse(status_check_url).path


def response_check_wait_for_completion(response: Response) -> bool:
    """
    Handle the response for `wait_for_reindex` Sensor.

    Processes the response to determine whether the task can complete.
    """
    data = response.json()

    if data["active"]:
        # The reindex is still running. Poll again later.
        return False

    if data["error"]:
        raise ValueError("An error was encountered during reindexing.")

    logger.info(f"Reindexing done with {data['progress']}% completed.")
    return True


@task
def get_worker_params(
    estimated_record_count: int,
    environment: str,
    target_environment: Environment,
    aws_conn_id: str = AWS_ASG_CONN_ID,
):
    """Determine the set of start/end indices to be passed to each indexer worker."""
    # Defaults to one indexer worker in local development
    worker_count = (
        INDEXER_WORKER_COUNTS.get(target_environment)
        if environment == PRODUCTION
        else 1
    )
    records_per_worker = math.floor(estimated_record_count / worker_count)

    return [
        {
            "start_id": worker_index * records_per_worker,
            "end_id": (1 + worker_index) * records_per_worker,
        }
        for worker_index in range(worker_count)
    ]


@task
def get_launch_template_version(
    environment: str,
    target_environment: Environment,
    aws_conn_id: str = AWS_ASG_CONN_ID,
):
    """
    Get the latest version of the launch template. Indexer workers will all be created with this
    version. Importantly, this allows us to retry an individual indexer worker and ensure that
    it will run with the same version of the indexer worker as the others, even if code has been
    deployed to the indexer worker in the meantime.
    """
    if environment != PRODUCTION:
        raise AirflowSkipException("Skipping instance creation in local environment.")

    ec2_hook = EC2Hook(aws_conn_id=aws_conn_id, api_type="client_type")
    launch_templates = ec2_hook.conn.describe_launch_templates(
        LaunchTemplateNames=INDEXER_LAUNCH_TEMPLATES.get(target_environment)
    )

    if len(launch_templates.get("LaunchTemplates")) == 0:
        raise Exception("Unable to determine launch template version.")

    return launch_templates.get("LaunchTemplates")[0].get("LatestVersionNumber")


@task
def create_worker(
    environment: str,
    target_environment: Environment,
    launch_template_version: int,
    aws_conn_id: str = AWS_ASG_CONN_ID,
):
    """
    Create a new EC2 instance using the launch template for the target
    environment. In local development, this step is skipped.
    """
    if environment != PRODUCTION:
        raise AirflowSkipException("Skipping instance creation in local environment.")

    ec2_hook = EC2Hook(aws_conn_id=aws_conn_id, api_type="client_type")
    instances = ec2_hook.conn.run_instances(
        MinCount=1,
        MaxCount=1,
        LaunchTemplate={
            "LaunchTemplateName": INDEXER_LAUNCH_TEMPLATES.get(target_environment),
            "Version": str(launch_template_version),
        },
        # Name the instance by applying a tag
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": f"catalog-indexer-worker-{target_environment}",
                    },
                ],
            },
        ],
    )["Instances"]

    if not len(instances) == 1:
        raise Exception(
            f"Expected one new instance, but {len(instances)} were created."
        )

    return instances[0]["InstanceId"]


# TODO configure interval/timeout
@task.sensor(poke_interval=60, timeout=3600, mode="reschedule")
def wait_for_worker(
    environment: str,
    instance_id: str,
    aws_conn_id: str = AWS_ASG_CONN_ID,
):
    """Await the EC2 instance with the given id to be in a healthy running state."""
    if environment != PRODUCTION:
        raise AirflowSkipException("Skipping instance creation in local environment.")

    ec2_hook = EC2Hook(aws_conn_id=aws_conn_id, api_type="client_type")
    result = ec2_hook.conn.describe_instance_status(InstanceIds=[instance_id])

    instance_status = result.get("InstanceStatuses", [])[0]
    state = instance_status.get("InstanceState", {}).get("Name")
    status = next(
        status.get("Status")
        for status in instance_status.get("InstanceStatus", {}).get("Details", [])
        if status.get("Name") == "reachability"
    )

    return PokeReturnValue(
        # Sensor completes only when the instance is running and has finished initializing
        is_done=(state == "running" and status == "ok")
    )


@task
def get_instance_ip_address(
    environment: str, instance_id: str, aws_conn_id: str = AWS_ASG_CONN_ID
):
    if environment != PRODUCTION:
        return "catalog_indexer_worker"

    ec2_hook = EC2Hook(aws_conn_id=aws_conn_id, api_type="client_type")
    reservations = ec2_hook.describe_instances(instance_ids=[instance_id]).get(
        "Reservations"
    )

    # `Reservations` is a list of dicts, grouping instances by the launch request that
    # started them. Because we are querying a single InstanceId we expect to have one
    # Reservation.
    if not (len(reservations) == 1 and len(reservations.get("Instances", {})) == 1):
        raise Exception("Unable to describe worker instance.")

    return reservations[0].get("Instances", {})[0].get("PrivateIpAddress")


@task(
    # Instance creation tasks are skipped locally, but we still want this task to run.
    trigger_rule=TriggerRule.NONE_FAILED
)
def create_connection(
    environment: str,
    target_environment: str,
    instance_id: str,
    server: str,
):
    """
    Create an Airflow Connection for the given indexer worker and persist it. It will
    later be dropped in a cleanup task.
    """
    worker_conn_id = f"indexer_worker_{instance_id or 'localhost'}"

    # Create the Connection
    logger.info(f"Creating connection with id {worker_conn_id}")
    worker_conn = Connection(conn_id=worker_conn_id, uri=f"http://{server}:8003/")
    session = settings.Session()
    session.add(worker_conn)
    session.commit()

    return worker_conn_id


@task
def terminate_indexer_worker(
    environment: str,
    instance_id: str,
    aws_conn_id: str = AWS_ASG_CONN_ID,
):
    """Terminate an individual indexer worker."""
    if environment != PRODUCTION:
        raise AirflowSkipException(
            "Skipping instance termination in local environment."
        )

    ec2_hook = EC2Hook(aws_conn_id=aws_conn_id, api_type="client_type")
    return ec2_hook.conn.terminate_instances(instance_ids=[instance_id])


@task(trigger_rule=TriggerRule.ALL_DONE)
def drop_connection(worker_conn: str):
    """Drop the Connection to the now terminated instance."""
    conn = Connection.get_connection_from_secrets(worker_conn)

    session = settings.Session()
    session.delete(conn)
    session.commit()


@task_group(group_id="reindex")
def reindex(
    model_name: str,
    table_name: str,
    target_index: str,
    start_id: int,
    end_id: int,
    environment: str,
    target_environment: Environment,
    aws_conn_id: str = AWS_ASG_CONN_ID,
):
    """
    Trigger a reindexing task on a remote indexer worker and wait for it to complete. Once done,
    terminate the indexer worker instance.
    """

    launch_template_version = get_launch_template_version(
        environment=environment,
        target_environment=target_environment,
    )

    # Create a new EC2 instance
    instance_id = create_worker(
        environment=environment,
        target_environment=target_environment,
        launch_template_version=launch_template_version,
        aws_conn_id=aws_conn_id,
    )

    # Wait for the worker to finish initializing
    await_worker = wait_for_worker(
        environment=environment, instance_id=instance_id, aws_conn_id=aws_conn_id
    )

    instance_ip_address = get_instance_ip_address(
        environment=environment, instance_id=instance_id, aws_conn_id=aws_conn_id
    )

    worker_conn = create_connection(
        instance_id=instance_id,
        server=instance_ip_address,
        environment=environment,
        target_environment=target_environment,
    )

    trigger_reindexing_task = TempConnectionHTTPOperator(
        task_id="trigger_reindexing_task",
        http_conn_id=worker_conn,
        endpoint="task",
        data={
            "model_name": model_name,
            "table_name": table_name,
            "target_index": target_index,
            "start_id": start_id,
            "end_id": end_id,
        },
        response_check=lambda response: response.status_code == 202,
        response_filter=response_filter_status_check_endpoint,
    )

    wait_for_reindexing_task = TempConnectionHTTPSensor(
        task_id="wait_for_reindexing_task",
        http_conn_id=worker_conn,
        endpoint=trigger_reindexing_task.output,
        method="GET",
        response_check=response_check_wait_for_completion,
        mode="reschedule",
        poke_interval=REFRESH_POKE_INTERVAL,
        timeout=24 * 60 * 60,  # 1 day TODO
    )

    terminate_instance = terminate_indexer_worker.override(
        # Terminate the instance even if there is an upstream failure
        trigger_rule=TriggerRule.ALL_DONE
    )(
        environment=environment,
        instance_id=instance_id,
    )

    drop_conn = drop_connection(worker_conn=worker_conn)

    instance_id >> [await_worker, instance_ip_address]
    worker_conn >> trigger_reindexing_task >> wait_for_reindexing_task
    wait_for_reindexing_task >> [terminate_instance, drop_conn]


@task_group(
    group_id="run_distributed_reindex",
)
def perform_distributed_reindex(
    environment: str,
    target_environment: Environment,
    target_index: str,
    data_refresh_config: DataRefreshConfig,
    aws_conn_id: str = AWS_ASG_CONN_ID,
):
    """Perform the distributed reindex on a fleet of remote indexer workers."""
    estimated_record_count = PGExecuteQueryOperator(
        task_id="get_estimated_record_count",
        conn_id=OPENLEDGER_API_CONN_ID,
        sql=dedent(
            f"""
            SELECT id FROM {data_refresh_config.media_type}
            ORDER BY id DESC LIMIT 1;
            """
        ),
        handler=single_value,
        return_last=True,
        trigger_rule=TriggerRule.NONE_FAILED,
    )

    worker_params = get_worker_params(
        estimated_record_count=estimated_record_count.output,
        environment=environment,
        target_environment=target_environment,
        aws_conn_id=aws_conn_id,
    )

    estimated_record_count >> worker_params

    reindex.partial(
        model_name=data_refresh_config.media_type,
        table_name=data_refresh_config.media_type,
        target_index=target_index,
        environment=environment,
        target_environment=target_environment,
        aws_conn_id=aws_conn_id,
    ).expand_kwargs(worker_params)
