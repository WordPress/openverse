import logging
from datetime import timedelta
from pprint import pformat

from airflow.decorators import task
from airflow.models import Variable
from airflow.providers.amazon.aws.hooks.rds import RdsHook
from airflow.providers.amazon.aws.sensors.rds import RdsDbSensor
from airflow.utils.task_group import TaskGroup
from airflow.utils.trigger_rule import TriggerRule

from common import slack
from database.staging_database_restore import constants
from database.staging_database_restore.utils import (
    ensure_mutate_allowed,
    setup_rds_hook,
)


REQUIRED_DB_INFO = {
    "MultiAZ",
    "AvailabilityZone",
    "VpcSecurityGroups",
    "DBSubnetGroup",
    "PubliclyAccessible",
    "DBInstanceClass",
    "AllocatedStorage",
}


log = logging.getLogger(__name__)


@task.short_circuit
def skip_restore(should_skip: bool = False) -> None:
    will_skip = should_skip or Variable.get(
        constants.SKIP_VARIABLE, default_var=False, deserialize_json=True
    )
    if not will_skip:
        slack.send_message(
            f"""
    :info: The staging database restore has been skipped.
    (Set the `{constants.SKIP_VARIABLE}` Airflow Variable to `false`
    to disable this behavior.)
    """,
            username=":database-pink:",
            dag_id=constants.DAG_ID,
        )
    return will_skip


@task
@setup_rds_hook
def get_latest_prod_snapshot(rds_hook: RdsHook = None):
    # Get snapshots
    snapshots = rds_hook.conn.describe_db_snapshots(
        DBInstanceIdentifier=constants.PROD_IDENTIFIER,
        SnapshotType="automated",
    ).get("DBSnapshots", [])
    # Sort by descending creation time
    snapshots = sorted(
        snapshots,
        key=lambda x: x["SnapshotCreateTime"],
        reverse=True,
    )
    if not snapshots:
        raise ValueError(f"No snapshots found for {constants.PROD_IDENTIFIER}")
    latest_snapshot = snapshots[0]
    log.info(f"Latest snapshot: {latest_snapshot}")
    return latest_snapshot["DBSnapshotIdentifier"]


@task
@setup_rds_hook
def get_staging_db_details(rds_hook: RdsHook = None):
    # Get staging DB details
    instances = rds_hook.conn.describe_db_instances(
        DBInstanceIdentifier=constants.STAGING_IDENTIFIER,
    ).get("DBInstances", [])
    if not instances:
        raise ValueError(f"No staging DB found for {constants.STAGING_IDENTIFIER}")
    staging_db = instances[0]
    # While it might be tempting to log this information, it contains sensitive
    # values. Instead, we'll select only the information we need, then log that.
    staging_db = {
        key: value for key, value in staging_db.items() if key in REQUIRED_DB_INFO
    }
    # Pull the DBSubnetGroup name out of the DBSubnetGroup object
    staging_db["DBSubnetGroupName"] = staging_db.pop("DBSubnetGroup")[
        "DBSubnetGroupName"
    ]
    # Pull the VPC IDs out of the VpcSecurityGroups objects
    staging_db["VpcSecurityGroupIds"] = [
        vpc["VpcSecurityGroupId"] for vpc in staging_db.pop("VpcSecurityGroups")
    ]
    log.info(f"Staging DB config: \n{pformat(staging_db)}")
    return staging_db


@task()
@setup_rds_hook
def restore_staging_from_snapshot(
    latest_snapshot: str, staging_config: dict, rds_hook: RdsHook = None
):
    log.info(
        f"Creating a new {constants.TEMP_IDENTIFIER} instance from {latest_snapshot} "
        f"with: \n{pformat(staging_config)}"
    )
    rds_hook.conn.restore_db_instance_from_db_snapshot(
        DBInstanceIdentifier=constants.TEMP_IDENTIFIER,
        DBSnapshotIdentifier=latest_snapshot,
        **staging_config,
    )


@task
@setup_rds_hook
def rename_db_instance(source: str, target: str, rds_hook: RdsHook = None):
    log.info("Checking input values")
    ensure_mutate_allowed(source)
    ensure_mutate_allowed(target)
    log.info(f"Renaming {source} to {target}")
    rds_hook.conn.modify_db_instance(
        DBInstanceIdentifier=source,
        NewDBInstanceIdentifier=target,
        ApplyImmediately=True,
    )


@task
def notify_slack(text: str) -> None:
    slack.send_message(
        text,
        username=constants.SLACK_USERNAME,
        icon_emoji=constants.SLACK_ICON,
        dag_id=constants.DAG_ID,
    )


def make_rds_sensor(task_id: str, db_identifier: str, retries: int = 0) -> RdsDbSensor:
    return RdsDbSensor(
        task_id=task_id,
        db_identifier=db_identifier,
        target_statuses=["available"],
        aws_conn_id=constants.AWS_RDS_CONN_ID,
        mode="reschedule",
        timeout=60 * 60,  # 1 hour
        retries=retries,
        retry_delay=timedelta(minutes=1),
    )


def make_rename_task_group(
    source: str,
    target: str,
    trigger_rule: TriggerRule = TriggerRule.ALL_SUCCESS,
) -> TaskGroup:
    source_name = source.removesuffix("-openverse-db")
    target_name = target.removesuffix("-openverse-db")
    with TaskGroup(group_id=f"rename_{source_name}_to_{target_name}") as rename_group:
        rename = rename_db_instance.override(
            task_id=f"rename_{source_name}_to_{target_name}",
            trigger_rule=trigger_rule,
        )(
            source=source,
            target=target,
        )
        await_rename = make_rds_sensor(
            task_id=f"await_{target_name}",
            db_identifier=target,
            retries=2,
        )
        rename >> await_rename

    return rename_group
