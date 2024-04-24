import logging
from datetime import timedelta
from pprint import pformat

from airflow.decorators import task, task_group
from airflow.models import Variable
from airflow.providers.amazon.aws.hooks.rds import RdsHook
from airflow.providers.amazon.aws.sensors.rds import RdsDbSensor
from airflow.utils.task_group import TaskGroup
from airflow.utils.trigger_rule import TriggerRule

from common import slack
from common.constants import AWS_RDS_CONN_ID
from common.github import GitHubAPI
from database.staging_database_restore import constants
from database.staging_database_restore.utils import (
    ensure_mutate_allowed,
    setup_github,
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
    "CopyTagsToSnapshot",
}

log = logging.getLogger(__name__)


@task.short_circuit
def skip_restore(should_skip: bool = False) -> bool:
    """
    Determine whether to skip the restore process.
    Can be overridden by setting the `SKIP_STAGING_DATABASE_RESTORE` Airflow Variable
    to `true`.
    Should return `True` to have the DAG continue, and `False` to have it skipped.
    <https://docs.astronomer.io/learn/airflow-branch-operator#taskshort_circuit-shortcircuitoperator>
    """
    should_continue = not (
        should_skip
        or Variable.get(
            constants.SKIP_VARIABLE, default_var=False, deserialize_json=True
        )
    )
    if not should_continue:
        notify_slack.function(
            "The staging database restore has been skipped. "
            f"(Set the `{constants.SKIP_VARIABLE}` Airflow Variable to `false`"
            "to disable this behavior.)"
        )
    return should_continue


@task
@setup_rds_hook
def get_latest_prod_snapshot(rds_hook: RdsHook = None) -> str:
    """
    Get the latest automated snapshot for the production database.
    <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds/client/describe_db_snapshots.html>
    Status is checked using a sensor in a later step, in case a snapshot creation is
    currently in progress.
    """
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
def get_staging_db_details(rds_hook: RdsHook = None) -> dict:
    """
    Retrieve the details of the staging database. Only some details are required (and
    others are actually sensitive) so filter down to only what we need.
    <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds/client/describe_db_instances.html>
    """
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


@task
@setup_rds_hook
def restore_staging_from_snapshot(
    latest_snapshot: str, staging_config: dict, rds_hook: RdsHook = None
) -> None:
    """
    Restore the staging database from the latest snapshot.
    Augment the restore operation with the existing details determined from
    a previous step.
    <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds/client/restore_db_instance_from_db_snapshot.html>
    """
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
def rename_db_instance(source: str, target: str, rds_hook: RdsHook = None) -> None:
    """
    Rename a database instance.
    This can only be run on instances where mutation is allowed.
    <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds/client/modify_db_instance.html>
    """
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
        aws_conn_id=AWS_RDS_CONN_ID,
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
    """
    Create a task group which includes both a rename operation, and a sensor to wait
    for the new database to be ready. This requires retries because the database
    may not be ready immediately after the rename when the first await is tried.
    """
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


@task
@setup_github
def get_latest_api_package_version(github: GitHubAPI = None) -> str:
    """Get the latest version of the API package from GitHub."""
    versions = github.get_package_versions("openverse-api")
    tags = set(versions[0]["metadata"]["container"]["tags"])
    # There might actually be more than one tag here, but since they all point
    # to the same build we don't care which is used.
    latest_version = sorted(tags - {"latest"})[0]
    log.info(f"Found latest version: {latest_version}")
    if not ("latest" in tags or latest_version.startswith("rel-")):
        raise ValueError(
            f"Latest version is not a release or not marked with 'latest': "
            f"{latest_version}"
        )

    return latest_version


@task
@setup_github
def dispatch_deploy(latest_version: str, github: GitHubAPI = None) -> None:
    """Dispatch the workflow for the staging API deployment."""
    github.dispatch_workflow(
        "openverse-infrastructure",
        "deploy-staging-api.yml",
        {
            "tag": latest_version,
            "run_name": f"staging database restore - {latest_version}",
        },
    )


@task_group(group_id="deploy_staging")
def deploy_staging() -> None:
    """Deploy the latest version of the API package to staging."""
    latest_version = get_latest_api_package_version()
    dispatch_deploy(latest_version)
