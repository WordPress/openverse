"""
Manages weekly database snapshots. RDS does not support weekly snapshots
schedules on its own, so we need a DAG to manage this for us.

It runs on Saturdays at 00:00 UTC in order to happen before the data refresh.

The DAG will automatically delete the oldest snapshots when more snaphots
exist than it is configured to retain.

Requires two variables:

`AIRFLOW_RDS_ARN`: The ARN of the RDS DB instance that needs snapshots.
`AIRFLOW_RDS_SNAPSHOTS_TO_RETAIN`: How many historical snapshots to retain.
"""

import logging
from datetime import datetime

import boto3
from airflow.decorators import dag, task
from airflow.providers.amazon.aws.operators.rds import RdsCreateDbSnapshotOperator
from airflow.providers.amazon.aws.sensors.rds import RdsSnapshotExistenceSensor


logger = logging.getLogger(__name__)

DAG_ID = "rotate_db_snapshots"
MAX_ACTIVE = 1


@task()
def delete_previous_snapshots(rds_arn: str, snapshots_to_retain: int):
    rds = boto3.client("rds")
    # Snapshot object documentation:
    # https://docs.aws.amazon.com/AmazonRDS/latest/APIReference/API_DBSnapshot.html
    snapshots = rds.describe_db_snapshots(
        DBInstanceIdentifier=rds_arn,
    )["DBSnapshots"]

    snapshots.sort(
        key=lambda x: datetime.fromisoformat(x["SnapshotCreateTime"]), reverse=True
    )

    if len(snapshots) <= snapshots_to_retain or not (
        snapshots_to_delete := snapshots[snapshots_to_retain:]
    ):
        logger.info("No snapshots to delete.")
        return

    logger.info(f"Deleting {len(snapshots_to_delete)} snapshots.")
    for snapshot in snapshots_to_delete:
        logger.info(f"Deleting {snapshot['DBSnapshotIdentifier']}.")
        rds.delete_db_snapshot(DBSnapshotIdentifier=snapshot["DBSnapshotIdentifier"])


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
    render_template_as_native_obj=True,
)
def rotate_db_snapshots():
    snapshot_id = "airflow-{{ ds }}"
    db_identifier_template = "{{ var.value.AIRFLOW_RDS_ARN }}"
    create_db_snapshot = RdsCreateDbSnapshotOperator(
        task_id="create_snapshot",
        db_type="instance",
        db_identifier=db_identifier_template,
        db_snapshot_identifier=snapshot_id,
    )
    wait_for_snapshot_availability = RdsSnapshotExistenceSensor(
        task_id="await_snapshot_availability",
        db_type="instance",
        db_snapshot_identifier=snapshot_id,
        # This is the default for ``target_statuses`` but making it explicit is clearer
        target_statuses=["available"],
    )

    (
        create_db_snapshot
        >> wait_for_snapshot_availability
        >> delete_previous_snapshots(
            rds_arn=db_identifier_template,
            snapshots_to_retain="{{ var.json.AIRFLOW_RDS_SNAPSHOTS_TO_RETAIN }}",
        )
    )


rotate_db_snapshots()
