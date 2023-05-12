import logging

from airflow.decorators import task
from airflow.exceptions import AirflowSkipException
from airflow.models import Variable
from airflow.providers.amazon.aws.hooks.rds import RdsHook

from common import slack
from database.staging_database_restore.constants import (
    DAG_ID,
    PROD_IDENTIFIER,
    SKIP_VARIABLE,
    STAGING_IDENTIFIER,
)
from database.staging_database_restore.utils import setup_rds_hook


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


@task()
def skip_restore(should_skip: bool = False) -> None:
    if not (
        should_skip
        or Variable.get(SKIP_VARIABLE, default_var=False, deserialize_json=True)
    ):
        return
    slack.send_message(
        f"""
:info: The staging database restore has been skipped.
(Set the `{SKIP_VARIABLE}` Airflow Variable to `false`
to disable this behavior.)
""",
        DAG_ID,
    )
    raise AirflowSkipException("Skipping restore step")


@task()
@setup_rds_hook
def get_latest_prod_snapshot(rds_hook: RdsHook = None):
    # Get snapshots
    snapshots = rds_hook.conn.describe_db_snapshots(
        DBInstanceIdentifier=PROD_IDENTIFIER,
        SnapshotType="automated",
    ).get("DBSnapshots", [])
    # Sort by descending creation time
    snapshots = sorted(
        snapshots,
        key=lambda x: x["SnapshotCreateTime"],
        reverse=True,
    )
    if not snapshots:
        raise ValueError(f"No snapshots found for {PROD_IDENTIFIER}")
    latest_snapshot = snapshots[0]
    log.info(f"Latest snapshot: {latest_snapshot}")
    return latest_snapshot["DBSnapshotIdentifier"]


@task()
@setup_rds_hook
def get_staging_db_details(rds_hook: RdsHook = None):
    # Get staging DB details
    instances = rds_hook.conn.describe_db_instances(
        DBInstanceIdentifier=STAGING_IDENTIFIER,
    ).get("DBInstances", [])
    if not instances:
        raise ValueError(f"No staging DB found for {STAGING_IDENTIFIER}")
    staging_db = instances[0]
    # While it might be tempting to log this information, it contains sensitive
    # values. Instead, we'll select only the information we need, then log that.
    staging_db = {
        key: value for key, value in staging_db.items() if key in REQUIRED_DB_INFO
    }
    log.info(f"Staging DB config: {staging_db}")
    return staging_db
