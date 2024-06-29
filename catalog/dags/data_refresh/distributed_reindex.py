"""
# Distributed Reindex TaskGroup

TODO Docstring

"""

import logging
import math
from dataclasses import dataclass
from datetime import timedelta
from functools import cached_property
from textwrap import dedent
from urllib.parse import urlparse

from airflow import settings
from airflow.decorators import task, task_group
from airflow.exceptions import AirflowSkipException
from airflow.models.connection import Connection
from airflow.providers.amazon.aws.hooks.base_aws import AwsBaseHook
from airflow.providers.amazon.aws.hooks.ec2 import EC2Hook
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.sensors.base import BaseSensorOperator, PokeReturnValue
from airflow.utils.trigger_rule import TriggerRule
from requests import Response

from common.constants import (
    AWS_ASG_CONN_ID,
    OPENLEDGER_API_CONN_ID,
    PRODUCTION,
    REFRESH_POKE_INTERVAL,
)
from common.sql import PGExecuteQueryOperator, single_value
from data_refresh.data_refresh_types import DataRefreshConfig


logger = logging.getLogger(__name__)


WORKER_CONN_ID = "indexer_worker_{worker_id}_http_{environment}"


@dataclass
class AutoScalingGroupConfig:
    name: str
    instance_count: int


class AutoScalingGroupSensor(BaseSensorOperator):
    """
    Sensor that waits for an AutoScalingGroup to have the desired number of healthy
    instances in service, and returns the list of instance_ids once the condition
    has been met.
    """

    def __init__(
        self,
        *,
        environment: str,
        asg_config: AutoScalingGroupConfig,
        aws_conn_id: str = AWS_ASG_CONN_ID,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.environment = environment
        self.asg_config = asg_config
        self.aws_conn_id = aws_conn_id

    @cached_property
    def conn(self):
        if self.environment != PRODUCTION:
            raise AirflowSkipException(
                "Skipping interactions with ASG in local development environment."
            )
        return AwsBaseHook(
            aws_conn_id=self.aws_conn_id, client_type="autoscaling"
        ).get_conn()

    def poke(self):
        asg = self.conn.describe_auto_scaling_groups(
            AutoScalingGroupNames=[self.asg_config.name]
        ).get("AutoScalingGroups")[0]

        instances = asg.get("Instances")

        # Return True when the ASG has the desired number of instances, and all
        # instances are healthy and in service.
        if len(instances) == self.asg_config.instance_count and all(
            instance.get("HealthStatus") == "HEALTHY"
            and instance.get("LifecycleState" == "InService")
            for instance in instances
        ):
            # Pass the list of instance_ids along through XCOMs once the conditions
            # have been met
            return PokeReturnValue(
                is_done=True,
                xcom_value=[instance.get("InstanceId") for instance in instances],
            )

        return PokeReturnValue(is_done=False, xcom_value=None)


@task
def get_autoscaling_group(
    environment: str,
    target_environment: str,
    aws_conn_id: str = AWS_ASG_CONN_ID,
):
    """Select the appropriate autoscaling group for the given environment."""
    # TODO pull this repeated code out.
    if environment != PRODUCTION:
        raise AirflowSkipException(
            "Skipping interactions with ASG in local development environment."
        )

    asg_conn = AwsBaseHook(
        aws_conn_id=aws_conn_id, client_type="autoscaling"
    ).get_conn()

    asgs = asg_conn.describe_auto_scaling_groups(
        Filters=[{"Name": "tag:WorkerTargetEnvironment", "Values": [environment]}]
    ).get("AutoScalingGroups")

    if len(asgs) != 1:
        raise Exception(
            f"Could not uniquely identify ASG for {environment} indexer workers."
        )

    target_asg = asgs[0]
    return AutoScalingGroupConfig(
        name=target_asg.get("AutoScalingGroupName"),
        instance_count=target_asg.get("MaxSize"),
    )


@task
def set_asg_capacity(
    environment: str,
    asg_config: AutoScalingGroupConfig,
    desired_capacity: int | None = None,
    aws_conn_id: str = AWS_ASG_CONN_ID,
):
    """Set the desired capacity of the autoscaling group to the desired number of instances."""
    if environment != PRODUCTION:
        raise AirflowSkipException(
            "Skipping interactions with ASG in local development environment."
        )

    asg_conn = AwsBaseHook(
        aws_conn_id=aws_conn_id, client_type="autoscaling"
    ).get_conn()

    if desired_capacity is None:
        desired_capacity = asg_config.instance_count

    return asg_conn.set_desired_capacity(
        AutoScalingGroupName=asg_config.asg_name, DesiredCapacity=desired_capacity
    )


@task
def get_worker_params(
    estimated_record_count: int,
    instance_ids: list[str],
    environment: str,
    target_environment: str,
    aws_conn_id: str = AWS_ASG_CONN_ID,  # TODO
):
    """
    TODO Because we are using an ASG now, we have lost the ability to retry an individual worker --
    because once an individual worker has failed, it will always be terimated so the trigger task
    cannot be retried. We can retry starting at the `start_workers` task but this will cause ALL
    the workers to be spun up and assigned work.

    We could allow the ASG to spin up a replacement when the reindexing task errors, but:
    (1) Unless someone notices and manually retries immediately, this instance will be kept live
        (and costing money) in the meantime
    (2) The trigger task will still attempt to hit the original instance; there's no way to tell
        it the updated one.

    We could try starting up the instances one at a time, so instead of setting the desired capacity
    to n all at once and then dynamically (trigger -> wait -> terminate) for each instance, we
    would have n parallel task groups that (create_instance -> trigger -> wait -> terminate). But
    this is not possible because of two limitations:
    * set_desired_capacity has no concept of "increment": you have to give it the total capacity
      you want for the ASG. So you cannot have n parallel tasks all incrementing the ASG capacity.
    * even if you could, set_desired_capacity does not return the instance_ids of the instances
      that get created as a result of the action. So there is no way for the `trigger` task to
      know which instance "belongs" to its branch

    The only thing I can think is of to make this entire `distributed_reindex` taskgroup take a few
    additional arguments:
    * desired_number_of_workers
    * index_ranges

    Maybe those are optional arguments, and when not passed the DAG assumes you want the max number of
    workers for this environment and you want all records to be reindexed. But the arguments can be
    optionally used to use a smaller number of workers, and reindex only portions of the total count.
    This taskgroup would also be used to create a separate, distributed_reindex DAG.

    Then if a single indexer worker fails during a data refresh, we could manually run this other
    DAG with desired_number_of_workers set to 1 and the faulty index range specified. When it passes
    we just manually pass that step in the original data_refresh DagRun and continue.
    """
    if environment != PRODUCTION:
        # Point to the local catalog_indexer_worker Docker container
        return {
            "start_id": 0,
            "end_id": estimated_record_count,
            "instance_id": None,
            "server": "http://catalog_indexer_worker:8003/",
        }

    # Get the private IP addresses of the worker instances
    ec2_hook = EC2Hook(aws_conn_id=aws_conn_id, api_type="client_type")
    reservations = ec2_hook.describe_instances(instance_ids=instance_ids).get(
        "Reservations"
    )

    # `Reservations` is a list of dicts, grouping instances by the run command that
    # started them. To be safe we get instances matching our expected instanceIds across
    # all reservations.
    servers = {
        instance.get("InstanceId"): instance.get("PrivateIpAddress")
        for reservation in reservations
        for instance in reservation.get("Instances")
    }

    records_per_worker = math.floor(estimated_record_count / len(instance_ids))

    params = []
    for worker_index, (instance_id, server) in servers.items():
        params.append(
            {
                "start_id": worker_index * records_per_worker,
                "end_id": (1 + worker_index) * records_per_worker,
                "instance_id": instance_id,
                "server": f"http://{server}:8003/",
            }
        )

    return params


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
def create_connection(instance_id: str, server: str, target_environment: str):
    worker_conn_id = WORKER_CONN_ID.format(
        worker_id=instance_id, environment=target_environment
    )
    # Create the Connection
    Connection(conn_id=worker_conn_id, uri=server)
    session = settings.Session()
    session.commit()


def trigger_reindex(
    worker_conn: str,
    model_name: str,
    table_name: str,
    start_id: int,
    end_id: int,
    target_index: int,
    target_environment: str,
) -> HttpOperator:
    """Trigger the reindexing task on an indexer worker."""
    data = {
        "model_name": model_name,
        "table_name": table_name,
        "target_index": target_index,
        "start_id": start_id,
        "end_id": end_id,
    }

    # Create a temporary Connection. We do not persist to the db because the instance is temporary.
    # TODO Alternative: split out a task to create the connection and persist to the db, add a
    # cleanup task to drop the connection after the instance is terminated.
    # worker_conn_id = WORKER_CONN_ID.format(worker_id=instance_id, environment=target_environment)
    # worker_conn = Connection(conn_id=worker_conn_id, uri=server)

    return HttpOperator(
        task_id="trigger_reindexing_task",
        http_conn_id=worker_conn,
        endpoint="task",
        data=data,
        response_check=lambda response: response.status_code == 202,
        response_filter=response_filter_status_check_endpoint,
    )


@task
def wait_for_reindex(
    worker_conn: str,
    status_endpoint: str,
    timeout: timedelta,
    poke_interval: int = REFRESH_POKE_INTERVAL,  # TODO
) -> HttpSensor:
    """Wait for the reindexing task on an indexer worker to complete."""
    # Create a temporary Connection. We do not persist to the db because the worker is temporary.
    # TODO Alternative: split out a task to create the connection and persist to the db, add a
    # cleanup task to drop the connection after the instance is terminated.
    # worker_conn_id = WORKER_CONN_ID.format(worker_id=instance_id, environment=target_environment)
    # worker_conn = Connection(conn_id=worker_conn_id, uri=server)

    return HttpSensor(
        task_id="wait_for_reindexing_task",
        http_conn_id=worker_conn,
        endpoint=status_endpoint,
        method="GET",
        response_check=response_check_wait_for_completion,
        mode="reschedule",
        poke_interval=poke_interval,
        timeout=timeout.total_seconds(),
    )


@task
def terminate_indexer_worker(
    environment: str,
    instance_id: str,
    aws_conn_id: str = AWS_ASG_CONN_ID,
):
    """Terminate an individual indexer worker."""
    if environment != PRODUCTION:
        raise AirflowSkipException(
            "Skipping interactions with ASG in local development environment."
        )

    asg_conn = AwsBaseHook(
        aws_conn_id=aws_conn_id, client_type="autoscaling"
    ).get_conn()

    asg_conn.terminate_instance_in_auto_scaling_group(
        InstanceId=instance_id,
        # Tell the ASG not to spin up a new instance to replace the terminated one.
        ShouldDecrementDesiredCapacity=True,
    )


@task
def drop_connection(worker_conn: str):
    """Drop the connection to the now terminated instance."""
    session = settings.Session()
    session.delete(worker_conn)
    session.commit()


@task_group(group_id="reindex")
def reindex(
    instance_id: str,
    server: str,
    model_name: str,
    table_name: str,
    target_index: str,
    start_id: int,
    end_id: int,
    environment: str,
    target_environment: str,
    aws_conn_id: str = AWS_ASG_CONN_ID,
):
    """
    Trigger a reindexing task on a remote indexer worker and wait for it to complete. Once done,
    terminate the indexer worker instance.
    """
    worker_conn = create_connection(
        instance_id=instance_id, server=server, target_environment=target_environment
    )

    trigger_reindexing_task = trigger_reindex(
        worker_conn=worker_conn,
        model_name=model_name,
        table_name=table_name,
        start_id=start_id,
        end_id=end_id,
        target_index=target_index,
        target_environment=target_environment,
    )

    wait_for_reindexing_task = wait_for_reindex(
        worker_conn=worker_conn,
        status_endpoint=trigger_reindexing_task,
        timeout=timedelta(days=1),  # TODO get from config
        poke_interval=REFRESH_POKE_INTERVAL,  # TODO get from config
    )

    terminate_instance = terminate_indexer_worker.override(
        # Terminate the instance even if there is an upstream failure
        trigger_rule=TriggerRule.ALL_DONE
    )(environment=environment, instance_id=instance_id, aws_conn_id=aws_conn_id)

    drop_conn = drop_connection(worker_conn=worker_conn)

    wait_for_reindexing_task >> [terminate_instance, drop_conn]


@task_group(group_id="run_distributed_reindex")
def perform_distributed_reindex(
    environment: str,
    target_environment: str,  # TODO, update types
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
    )

    asg_config = get_autoscaling_group(
        environment=environment,
        target_environment=target_environment,
        aws_conn_id=aws_conn_id,
    )

    start_workers = set_asg_capacity.override(task_id="start_indexer_workers")(
        environment=environment, asg_config=asg_config, aws_conn_id=aws_conn_id
    )

    workers = AutoScalingGroupSensor(
        task_id="wait_for_workers",
        environment=environment,
        asg_config=asg_config,
        aws_conn_id=aws_conn_id,
    )

    start_workers >> workers

    worker_params = get_worker_params(
        estimated_record_count=estimated_record_count,
        instance_ids=workers,
        environment=environment,
        target_environment=target_environment,
        aws_conn_id=aws_conn_id,
    )

    workers >> worker_params

    distributed_reindex = reindex.partial(
        model_name=data_refresh_config.media_type,
        table_name=data_refresh_config.media_type,
        target_index=target_index,
        environment=environment,
        target_environment=target_environment,
        aws_conn_id=aws_conn_id,
    ).expand_kwargs(worker_params)

    # All workers should be terminated once work is complete, even if errors were encountered.
    # However, it is possible to have live instances left over if a worker crashed during
    # reindexing and the ASG spun up a replacement that the DAG is not tracking. We force the
    # ASG capacity to 0 at the end of execution to ensure this does not happen.
    terminate_workers = set_asg_capacity.override(
        task_id="ensure_all_workers_terminated", trigger_rule=TriggerRule.ALL_DONE
    )(
        environment=environment,
        asg_config=asg_config,
        desired_capacity=0,
        aws_conn_id=aws_conn_id,
    )

    distributed_reindex >> terminate_workers
