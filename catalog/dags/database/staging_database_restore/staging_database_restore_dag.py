"""
# Staging Database Restore DAG

This DAG is responsible for updating the staging database using the most recent
snapshot of the production database.

For a full explanation of the DAG, see the implementation plan description:
https://docs.openverse.org/projects/proposals/search_relevancy_sandbox/20230406-implementation_plan_update_staging_database.html#dag

This DAG can be skipped by setting the `SKIP_STAGING_DATABASE_RESTORE` Airflow Variable
to `true`. To change this variable, navigate to Admin > Variables in the Airflow UI,
then click the "edit" button next to the variable and set the value to either `true`
or `false`.

This DAG will default to using the standard AWS connection ID for the RDS operations.
For local testing, you can set up two environment variables to have the RDS operations
run using a different hook:
- `AWS_RDS_CONN_ID`: The Airflow connection ID to use for RDS operations
  (e.g. `aws_rds`)
- `AIRFLOW_CONN_<ID>`: The connection string to use for RDS operations (per the above
  example, it might be `AIRFLOW_CONN_AWS_RDS`)
"""

import logging
from datetime import datetime, timedelta
from textwrap import dedent as d

from airflow.decorators import dag
from airflow.providers.amazon.aws.operators.rds import RdsDeleteDbInstanceOperator
from airflow.providers.amazon.aws.sensors.rds import RdsSnapshotExistenceSensor
from airflow.utils.trigger_rule import TriggerRule

from common.constants import (
    AWS_RDS_CONN_ID,
    DAG_DEFAULT_ARGS,
    POSTGRES_API_STAGING_CONN_ID,
)
from common.sensors.constants import STAGING_DB_CONCURRENCY_TAG
from common.sensors.utils import wait_for_external_dags_with_tag
from common.sql import PGExecuteQueryOperator
from database.staging_database_restore import constants
from database.staging_database_restore.staging_database_restore import (
    deploy_staging,
    get_latest_prod_snapshot,
    get_staging_db_details,
    make_rds_sensor,
    make_rename_task_group,
    notify_slack,
    restore_staging_from_snapshot,
    skip_restore,
)


log = logging.getLogger(__name__)


@dag(
    dag_id=constants.DAG_ID,
    schedule="@monthly",
    start_date=datetime(2023, 5, 1),
    tags=["database", STAGING_DB_CONCURRENCY_TAG],
    max_active_runs=1,
    dagrun_timeout=timedelta(days=1),
    catchup=False,
    # Use the docstring at the top of the file as md docs in the UI
    doc_md=__doc__,
    default_args={
        **DAG_DEFAULT_ARGS,
        # Don't add any retries by default
        "retries": 0,
    },
    render_template_as_native_obj=True,
)
def restore_staging_database():
    # If the `recreate_full_staging_index` DAG was manually triggered prior
    # to the database restoration starting, we should wait for it to
    # finish. It is not necessary to wait on any of the other ES DAGs as
    # they do not directly affect the database.
    wait_for_recreate_full_staging_index = wait_for_external_dags_with_tag(
        tag=STAGING_DB_CONCURRENCY_TAG
    )
    should_skip = skip_restore()
    latest_snapshot = get_latest_prod_snapshot()
    wait_for_recreate_full_staging_index >> should_skip >> latest_snapshot

    ensure_snapshot_ready = RdsSnapshotExistenceSensor(
        task_id="ensure_snapshot_ready",
        db_type="instance",
        db_snapshot_identifier=latest_snapshot,
        aws_conn_id=AWS_RDS_CONN_ID,
        mode="reschedule",
        timeout=60 * 60 * 4,  # 4 hours
    )

    staging_details = get_staging_db_details()
    should_skip >> staging_details

    restore_snapshot = restore_staging_from_snapshot(latest_snapshot, staging_details)
    ensure_snapshot_ready >> restore_snapshot

    await_staging_creation = make_rds_sensor(
        task_id="await_staging_creation",
        db_identifier=constants.TEMP_IDENTIFIER,
    )
    restore_snapshot >> await_staging_creation

    notify_outage = notify_slack.override(task_id="notify_outage")(
        ":warning: Staging database is being restored, staging will "
        "be down for the duration."
    )

    rename_staging_to_old = make_rename_task_group(
        constants.STAGING_IDENTIFIER, constants.OLD_IDENTIFIER
    )
    await_staging_creation >> [notify_outage, rename_staging_to_old]

    rename_temp_to_staging = make_rename_task_group(
        constants.TEMP_IDENTIFIER, constants.STAGING_IDENTIFIER
    )
    rename_staging_to_old >> rename_temp_to_staging

    # Only run this if the secondary rename failed
    rename_old_to_staging = make_rename_task_group(
        constants.OLD_IDENTIFIER,
        constants.STAGING_IDENTIFIER,
        trigger_rule=TriggerRule.ALL_FAILED,
    )
    notify_failed_but_back = notify_slack.override(task_id="notify_failed_but_back")(
        ":warning: Staging database rename failed, but staging should "
        "now be available. Please investigate the cause of the failure."
    )
    rename_temp_to_staging >> rename_old_to_staging >> notify_failed_but_back
    delete_old = RdsDeleteDbInstanceOperator(
        task_id="delete_old",
        db_instance_identifier=constants.OLD_IDENTIFIER,
        rds_kwargs={"SkipFinalSnapshot": True, "DeleteAutomatedBackups": False},
        aws_conn_id=AWS_RDS_CONN_ID,
        wait_for_completion=True,
    )

    rename_temp_to_staging >> delete_old

    notify_complete = notify_slack.override(task_id="notify_complete")(
        ":info: Staging database restore complete, staging should now be available.",
    )

    # Truncate the oauth tables, the cascade ensures all related tables are truncated
    truncate_tables = PGExecuteQueryOperator(
        task_id="truncate_oauth_tables",
        sql=d(
            """
            TRUNCATE TABLE api_throttledapplication RESTART IDENTITY CASCADE;
            TRUNCATE TABLE api_oauth2registration RESTART IDENTITY CASCADE;
            """
        ),
        postgres_conn_id=POSTGRES_API_STAGING_CONN_ID,
        execution_timeout=timedelta(minutes=5),
    )

    # Deploy the latest API package to staging
    execute_deploy = deploy_staging()

    rename_temp_to_staging >> [truncate_tables, execute_deploy] >> notify_complete


restore_staging_database()
