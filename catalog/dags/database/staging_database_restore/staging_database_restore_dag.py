"""
# Update the staging database

This DAG is responsible for updating the staging database using the most recent
snapshot of the production database.

For a full explanation of the DAG, see the implementation plan description:
https://docs.openverse.org/projects/proposals/search_relevancy_sandbox/20230406-implementation_plan_update_staging_database.html#dag
"""

import logging
from datetime import datetime

from airflow.decorators import dag

from database.staging_database_restore.staging_database_restore import (
    DAG_ID,
    get_latest_prod_snapshot,
    skip_restore,
)


log = logging.getLogger(__name__)


@dag(
    dag_id=DAG_ID,
    schedule="@monthly",
    start_date=datetime(2023, 5, 1),
    tags=["database"],
    max_active_runs=1,
    catchup=False,
    # Use the docstring at the top of the file as md docs in the UI
    doc_md=__doc__,
    render_template_as_native_obj=True,
)
def restore_staging_database():
    (skip_restore() >> get_latest_prod_snapshot())


restore_staging_database()
