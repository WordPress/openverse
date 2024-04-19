"""
Manages weekly database snapshots.

RDS does not support weekly snapshots schedules on its own, so we need a DAG to manage
this for us.

It runs on Saturdays at 00:00 UTC in order to happen before the data refresh.

The DAG will automatically delete the oldest snapshots when more snapshots
exist than it is configured to retain.

Requires two variables:

`CATALOG_RDS_DB_IDENTIFIER`: The "DBIdentifier" of the RDS DB instance.
`CATALOG_RDS_SNAPSHOTS_TO_RETAIN`: How many historical snapshots to retain.
"""

import logging
from datetime import datetime

from airflow.decorators import dag, task
from airflow.providers.amazon.aws.hooks.rds import RdsHook
from airflow.providers.amazon.aws.operators.rds import RdsCreateDbSnapshotOperator
from airflow.providers.amazon.aws.sensors.rds import RdsSnapshotExistenceSensor

from common.constants import AWS_RDS_CONN_ID, DAG_DEFAULT_ARGS


logger = logging.getLogger(__name__)

DAG_ID = "rotate_db_snapshots"
MAX_ACTIVE = 1


AIRFLOW_MANAGED_SNAPSHOT_ID_PREFIX = "airflow-managed"


@task()
def delete_previous_snapshots(db_identifier: str, snapshots_to_retain: int):
    hook = RdsHook(aws_conn_id=AWS_RDS_CONN_ID)

    # Snapshot object documentation:
    # https://docs.aws.amazon.com/AmazonRDS/latest/APIReference/API_DBSnapshot.html
    snapshots = hook.conn.describe_db_snapshots(
        DBInstanceIdentifier=db_identifier,
        SnapshotType="manual",  # Automated backups cannot be manually managed
    )["DBSnapshots"]

    # Other manual snapshots may exist; we only want to automatically manage
    # ones this DAG created
    snapshots = [
        snapshot
        for snapshot in snapshots
        if snapshot["DBSnapshotIdentifier"].startswith(
            AIRFLOW_MANAGED_SNAPSHOT_ID_PREFIX
        )
    ]

    snapshots.sort(
        key=lambda x: x["SnapshotCreateTime"],  # boto3 casts this to datetime
        reverse=True,
    )

    if len(snapshots) <= snapshots_to_retain or not (
        snapshots_to_delete := snapshots[snapshots_to_retain:]
    ):
        logger.info("No snapshots to delete.")
        return

    logger.info(f"Deleting {len(snapshots_to_delete)} snapshots.")
    for snapshot in snapshots_to_delete:
        logger.info(f"Deleting {snapshot['DBSnapshotIdentifier']}.")
        hook.conn.delete_db_snapshot(
            DBSnapshotIdentifier=snapshot["DBSnapshotIdentifier"]
        )


@dag(
    dag_id=DAG_ID,
    # At 00:00 on Saturday, this puts it before the data refresh starts
    schedule="0 0 * * 6",
    start_date=datetime(2022, 12, 2),
    tags=["maintenance"],
    max_active_tasks=MAX_ACTIVE,
    max_active_runs=MAX_ACTIVE,
    catchup=False,
    # Use the docstring at the top of the file as md docs in the UI
    doc_md=__doc__,
    default_args=DAG_DEFAULT_ARGS,
    render_template_as_native_obj=True,
)
def rotate_db_snapshots():
    snapshot_id = f"{AIRFLOW_MANAGED_SNAPSHOT_ID_PREFIX}-{{{{ ts_nodash }}}}"
    db_identifier = "{{ var.value.CATALOG_RDS_DB_IDENTIFIER }}"

    create_db_snapshot = RdsCreateDbSnapshotOperator(
        task_id="create_snapshot",
        db_type="instance",
        db_identifier=db_identifier,
        db_snapshot_identifier=snapshot_id,
        aws_conn_id=AWS_RDS_CONN_ID,
        wait_for_completion=False,
    )

    wait_for_snapshot_availability = RdsSnapshotExistenceSensor(
        task_id="await_snapshot_availability",
        db_type="instance",
        db_snapshot_identifier=snapshot_id,
        # This is the default for ``target_statuses`` but making it explicit is clearer
        target_statuses=["available"],
        aws_conn_id=AWS_RDS_CONN_ID,
        mode="reschedule",
    )

    (
        create_db_snapshot
        >> wait_for_snapshot_availability
        >> delete_previous_snapshots(
            db_identifier=db_identifier,
            snapshots_to_retain="{{ var.json.CATALOG_RDS_SNAPSHOTS_TO_RETAIN }}",
        )
    )


rotate_db_snapshots()
