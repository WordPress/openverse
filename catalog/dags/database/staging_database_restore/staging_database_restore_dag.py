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

from database.staging_database_restore.constants import AWS_RDS_CONN_ID, DAG_ID
from database.staging_database_restore.staging_database_restore import (
    get_latest_prod_snapshot,
    get_staging_db_details,
    skip_restore,
)


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
    should_skip = skip_restore()
    latest_snapshot = get_latest_prod_snapshot()
    should_skip >> latest_snapshot

    RdsSnapshotExistenceSensor(
        task_id="ensure_snapshot_ready",
        db_type="instance",
        db_snapshot_identifier=latest_snapshot,
        aws_conn_id=AWS_RDS_CONN_ID,
        mode="reschedule",
        timeout=60 * 60 * 4,  # 4 hours
    )

    staging_details = get_staging_db_details()
    should_skip >> staging_details


restore_staging_database()
