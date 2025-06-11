"""
# Distributed Reindex TaskGroup

This module contains the Airflow tasks used for orchestrating the reindexing of records from the temporary tables in the downstream (API) database, into a new Elasticsearch index. Reindexing is performed on a fleet of indexer worker EC2 instances, with instance creation and termination managed by Airflow.
"""

import functools
import logging
import math
from textwrap import dedent
from urllib.parse import urlparse

from airflow import settings
from airflow.decorators import task, task_group
from airflow.exceptions import AirflowSkipException
from airflow.models.connection import Connection
from airflow.operators.empty import EmptyOperator
from airflow.providers.amazon.aws.hooks.ec2 import EC2Hook
from airflow.providers.common.sql.hooks.handlers import fetch_one_handler
from airflow.sensors.base import PokeReturnValue
from airflow.utils.trigger_rule import TriggerRule
from requests import Response

from common import elasticsearch as es
from common.constants import (
    AWS_CONN_ID,
    POSTGRES_API_CONN_IDS,
    PRODUCTION,
    Environment,
)
from common.operators.http import TemplatedConnectionHttpOperator
from common.sensors.http import TemplatedConnectionHttpSensor
from common.sql import PGExecuteQueryOperator
from data_refresh.constants import INDEXER_LAUNCH_TEMPLATES, INDEXER_WORKER_COUNTS
from data_refresh.data_refresh_types import DataRefreshConfig


logger = logging.getLogger(__name__)


def setup_ec2_hook(func: callable) -> callable:
    """
    Provide an ec2_hook as one of the parameters for the called function.
    If the function is explicitly supplied with an ec2_hook, use that one.
    :return:
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        ec2_hook = kwargs.pop("ec2_hook", None) or EC2Hook(
            aws_conn_id=AWS_CONN_ID, api_type="client_type"
        )
        return func(*args, **kwargs, ec2_hook=ec2_hook)

    return wrapped


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
    id_range: tuple[int, int],
    environment: str,
    target_environment: Environment,
):
    """Determine the set of start/end indices to be passed to each indexer worker."""
    # Defaults to one indexer worker in local development
    worker_count = (
        INDEXER_WORKER_COUNTS.get(target_environment)
        if environment == PRODUCTION
        else 1
    )

    min_id, max_id = id_range
    estimated_record_count = max_id - min_id + 1
    records_per_worker = math.floor(estimated_record_count / worker_count)

    return [
        {
            "start_id": min_id + worker_index * records_per_worker,
            "end_id": min_id + (1 + worker_index) * records_per_worker,
        }
        for worker_index in range(worker_count)
    ]


@task
@setup_ec2_hook
def get_launch_template_version_number(
    environment: str,
    target_environment: Environment,
    ec2_hook: EC2Hook = None,
):
    """
    Get the latest version number of the launch template. Indexer workers will all be created with this
    version. Importantly, this allows us to retry an individual indexer worker and ensure that
    it will run with the same version of the indexer worker as the others, even if code has been
    deployed to the indexer worker in the meantime.
    """
    if environment != PRODUCTION:
        raise AirflowSkipException("Skipping instance creation in local environment.")

    launch_templates = ec2_hook.conn.describe_launch_templates(
        LaunchTemplateNames=[INDEXER_LAUNCH_TEMPLATES.get(target_environment)]
    )
    return launch_templates.get("LaunchTemplates")[0].get("LatestVersionNumber")


@task(
    # Prevents the entire reindex TaskGroup from skipping when get_launch_template_version_number
    # was skipped locally
    trigger_rule=TriggerRule.NONE_FAILED
)
@setup_ec2_hook
def create_worker(
    environment: str,
    target_environment: Environment,
    launch_template_version_number: int | str,
    ec2_hook: EC2Hook = None,
):
    """
    Create a new EC2 instance using the launch template for the target
    environment. In local development, this step is skipped.
    """
    if environment != PRODUCTION:
        raise AirflowSkipException("Skipping instance creation in local environment.")

    instances = ec2_hook.conn.run_instances(
        MinCount=1,
        MaxCount=1,
        LaunchTemplate={
            "LaunchTemplateName": INDEXER_LAUNCH_TEMPLATES.get(target_environment),
            "Version": str(launch_template_version_number),
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


def _get_reachability_status(instance_data, status_type):
    status_data = instance_data.get(status_type, {})
    reachability_status = next(
        (
            status.get("Status")
            for status in status_data.get("Details", [])
            if status.get("Name") == "reachability"
        ),
        None,
    )
    return reachability_status == "passed" and status_data.get("Status") == "ok"


@task.sensor(poke_interval=60, timeout=3600, mode="reschedule")
@setup_ec2_hook
def wait_for_worker(
    environment: str,
    instance_id: str,
    ec2_hook: EC2Hook = None,
):
    """Await the EC2 instance with the given id to be in a healthy running state."""
    if environment != PRODUCTION:
        raise AirflowSkipException("Skipping instance creation in local environment.")

    result = ec2_hook.conn.describe_instance_status(InstanceIds=[instance_id])
    logger.info(result)

    instance_statuses = result.get("InstanceStatuses")
    instance_status = instance_statuses[0] if instance_statuses else {}

    state = instance_status.get("InstanceState", {}).get("Name")
    is_reachable = all(
        [
            _get_reachability_status(instance_status, status_type)
            for status_type in ["InstanceStatus", "SystemStatus", "AttachedEbsStatus"]
        ]
    )

    return PokeReturnValue(
        # Sensor completes only when the instance is running and has finished initializing
        is_done=(state == "running" and is_reachable)
    )


@task(
    # Run locally when create instance tasks are skipped
    trigger_rule=TriggerRule.NONE_FAILED
)
@setup_ec2_hook
def get_instance_ip_address(
    environment: str,
    instance_id: str,
    ec2_hook: EC2Hook = None,
):
    if environment != PRODUCTION:
        return "catalog_indexer_worker"

    reservations = ec2_hook.describe_instances(instance_ids=[instance_id]).get(
        "Reservations"
    )
    return reservations[0].get("Instances", {})[0].get("PrivateIpAddress")


@task(
    # Instance creation tasks are skipped locally, but we still want this task to run.
    trigger_rule=TriggerRule.NONE_FAILED
)
def create_connection(
    environment: str,
    instance_id: str,
    media_type: str,
    server: str,
):
    """
    Create an Airflow Connection for the given indexer worker and persist it. It will
    later be dropped in a cleanup task.
    """
    worker_conn_id = f"indexer_worker_{instance_id or media_type}"

    # Create the Connection
    logger.info(f"Creating connection with id {worker_conn_id}")
    worker_conn = Connection(conn_id=worker_conn_id, uri=f"http://{server}:8003/")
    session = settings.Session()
    session.add(worker_conn)
    session.commit()

    return worker_conn_id


@task
@setup_ec2_hook
def terminate_indexer_worker(
    environment: str,
    instance_id: str,
    ec2_hook: EC2Hook = None,
):
    """Terminate an individual indexer worker."""
    if environment != PRODUCTION:
        raise AirflowSkipException(
            "Skipping instance termination in local environment."
        )
    return ec2_hook.conn.terminate_instances(InstanceIds=[instance_id])


@task(trigger_rule=TriggerRule.ALL_DONE)
def drop_connection(worker_conn: str):
    """Drop the Connection to the now terminated instance."""
    conn = Connection.get_connection_from_secrets(worker_conn)

    session = settings.Session()
    session.delete(conn)
    session.commit()


def assert_reindexing_success() -> EmptyOperator:
    """
    Fail if the direct upstream tasks, which perform the actual reindexing,
    fail. Otherwise simply pass.

    This is necessary because we have some tasks after the reindex step
    which always run even on reindexing failure (to drop the connection
    and terminate the worker instance). However in the event of failures,
    we still need the last task in the TaskGroup to be marked as `Failed`
    or else subsequent tasks (like the promotion steps) will run. It is
    not possible to set individual tasks within a TaskGroup as
    directly upstream of later tasks; the last task in the TaskGroup
    must fail.
    """
    return EmptyOperator(
        task_id="assert_reindexing_success", trigger_rule=TriggerRule.NONE_FAILED
    )


@task_group(group_id="reindex")
def reindex(
    data_refresh_config: DataRefreshConfig,
    target_index: str,
    launch_template_version_number: int | str,
    start_id: int,
    end_id: int,
    environment: str,
    target_environment: Environment,
):
    """
    Trigger a reindexing task on a remote indexer worker and wait for it to complete. Once done,
    terminate the indexer worker instance.
    """

    # Create a new EC2 instance
    instance_id = create_worker(
        environment=environment,
        target_environment=target_environment,
        launch_template_version_number=launch_template_version_number,
    )

    # Wait for the worker to finish initializing
    await_worker = wait_for_worker.override(
        poke_interval=data_refresh_config.reindex_poke_interval,
        timeout=data_refresh_config.indexer_worker_timeout.total_seconds(),
    )(environment=environment, instance_id=instance_id)

    instance_ip_address = get_instance_ip_address(
        environment=environment, instance_id=instance_id
    )

    worker_conn = create_connection(
        environment=environment,
        instance_id=instance_id,
        media_type=data_refresh_config.media_type,
        server=instance_ip_address,
    )

    trigger_reindexing_task = TemplatedConnectionHttpOperator(
        task_id="trigger_reindexing_task",
        http_conn_id=worker_conn,
        endpoint="task",
        data={
            "model_name": data_refresh_config.media_type,
            "table_name": data_refresh_config.table_mapping.temp_table_name,
            "target_index": target_index,
            "start_id": start_id,
            "end_id": end_id,
        },
        response_check=lambda response: response.status_code == 202,
        response_filter=response_filter_status_check_endpoint,
    )

    wait_for_reindexing_task = TemplatedConnectionHttpSensor(
        task_id="wait_for_reindexing_task",
        http_conn_id=worker_conn,
        endpoint=trigger_reindexing_task.output,
        method="GET",
        response_check=response_check_wait_for_completion,
        mode="reschedule",
        poke_interval=data_refresh_config.reindex_poke_interval,
        timeout=data_refresh_config.indexer_worker_timeout,
    )

    terminate_instance = terminate_indexer_worker.override(
        # Terminate the instance even if there is an upstream failure
        trigger_rule=TriggerRule.ALL_DONE
    )(
        environment=environment,
        instance_id=instance_id,
    )

    status = assert_reindexing_success()

    drop_conn = drop_connection(worker_conn=worker_conn)

    instance_id >> await_worker >> [instance_ip_address, worker_conn]
    worker_conn >> trigger_reindexing_task >> wait_for_reindexing_task
    wait_for_reindexing_task >> [terminate_instance, drop_conn, status]


@task_group(
    group_id="run_distributed_reindex",
)
def perform_distributed_reindex(
    es_host: str,
    environment: str,
    target_environment: Environment,
    target_index: str,
    data_refresh_config: DataRefreshConfig,
):
    """Perform the distributed reindex on a fleet of remote indexer workers."""
    id_range = PGExecuteQueryOperator(
        task_id="get_record_id_range",
        conn_id=POSTGRES_API_CONN_IDS.get(target_environment),
        sql=dedent(
            f"""
            SELECT min(id), max(id) FROM {data_refresh_config.table_mapping.temp_table_name};
            """
        ),
        handler=fetch_one_handler,
        return_last=True,
        trigger_rule=TriggerRule.NONE_FAILED,
    )

    launch_template_version_number = get_launch_template_version_number(
        environment=environment,
        target_environment=target_environment,
    )

    worker_params = get_worker_params(
        id_range=id_range.output,
        environment=environment,
        target_environment=target_environment,
    )

    id_range >> worker_params

    perform_reindex = reindex.partial(
        data_refresh_config=data_refresh_config,
        target_index=target_index,
        launch_template_version_number=launch_template_version_number,
        environment=environment,
        target_environment=target_environment,
    ).expand_kwargs(worker_params)

    # Refresh the index at the end, in order to make the documents available for
    # filtered index creation
    refresh_index = es.refresh_index.override(
        trigger_rule=TriggerRule.NONE_FAILED,
    )(
        es_host=es_host,
        index_name=target_index,
    )

    perform_reindex >> refresh_index
