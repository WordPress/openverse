"""
# Update the staging database

This DAG is responsible for updating the staging database using the most recent
snapshot of the production database.

For a full explanation of the DAG, see the implementation plan description:
https://docs.openverse.org/projects/proposals/search_relevancy_sandbox/20230406-implementation_plan_update_staging_database.html#dag
"""

import logging
from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.providers.amazon.aws.sensors.rds import RdsSnapshotExistenceSensor

from database.staging_database_restore.staging_database_restore import (
    DAG_ID,
    get_latest_prod_snapshot,
    skip_restore,
)
from database.staging_database_restore.utils import AWS_RDS_CONN_ID


log = logging.getLogger(__name__)


@dag(
    dag_id=DAG_ID,
    schedule="@monthly",
    start_date=datetime(2023, 5, 1),
    tags=["database"],
    max_active_runs=1,
    dagrun_timeout=timedelta(days=1),
    catchup=False,
    # Use the docstring at the top of the file as md docs in the UI
    doc_md=__doc__,
    render_template_as_native_obj=True,
)
def restore_staging_database():
    latest_snapshot = get_latest_prod_snapshot()
    skip_restore() >> latest_snapshot

    RdsSnapshotExistenceSensor(
        task_id="ensure_snapshot_ready",
        db_type="instance",
        db_snapshot_identifier=latest_snapshot,
        aws_conn_id=AWS_RDS_CONN_ID,
        mode="reschedule",
        timeout=60 * 60 * 4,  # 4 hours
    )


restore_staging_database()
