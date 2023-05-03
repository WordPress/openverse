"""
# Recreate Materialized View Task Factory
This file generates a TaskGroup that recreates the materialized view for a
given media type, using a factory function.

The task drops and recreates the materialized view, but not the underlying tables. This
means that the only effect is to add or update data (including popularity data)
for records which have been ingested since the last time the view was
refreshed.

This should be run every time before a data refresh is triggered.
"""
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.utils.trigger_rule import TriggerRule

from common.constants import POSTGRES_CONN_ID
from common.popularity import sql
from data_refresh import reporting
from data_refresh.data_refresh_types import DataRefresh


GROUP_ID = "recreate_matview"
DROP_DB_VIEW_TASK_ID = "drop_materialized_popularity_view"
CREATE_DB_VIEW_TASK_ID = "create_materialized_popularity_view"


def create_recreate_view_data_task(data_refresh: DataRefresh):
    """
    Create the recreate related tasks.

    The task drops and recreates the materialized view for the given media type. The
    view collates popularity data for each record. Recreating has the effect of adding
    popularity data for records that were ingested since the last time the view was
    created or refreshed, and updating popularity data for existing records. It also
    creates a reporting task which will report the status of the matview refresh once
    it is complete.

    The view is dropped and recreated rather than refreshed, because refreshing the view
    takes much longer in production and times out.

    Required Arguments:

    data_refresh: configuration information for the data refresh
    """
    with TaskGroup(group_id=GROUP_ID) as recreate_matview:
        drop_matview = PythonOperator(
            task_id=DROP_DB_VIEW_TASK_ID,
            python_callable=sql.drop_media_matview,
            op_kwargs={
                "postgres_conn_id": POSTGRES_CONN_ID,
                "media_type": data_refresh.media_type,
            },
            trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
            retries=0,
        )
        create_matview = PythonOperator(
            task_id=CREATE_DB_VIEW_TASK_ID,
            python_callable=sql.create_media_view,
            op_kwargs={
                "postgres_conn_id": POSTGRES_CONN_ID,
                "media_type": data_refresh.media_type,
            },
            execution_timeout=data_refresh.create_materialized_view_timeout,
            retries=0,
            doc_md=create_recreate_view_data_task.__doc__,
        )
        recreate_status = PythonOperator(
            task_id=f"report_{GROUP_ID}_status",
            python_callable=reporting.report_status,
            op_kwargs={
                "media_type": data_refresh.media_type,
                "dag_id": data_refresh.dag_id,
                "message": "Matview refresh complete | "
                "_Next: ingestion server data refresh_",
            },
        )

        drop_matview >> create_matview >> recreate_status

    return recreate_matview
