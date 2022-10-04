"""
# Refresh Materialized View Task Factory
This file generates a Task that refreshes the materialized view for a
given media type, using a factory function.

The task refreshes the materialized view, but not the underlying tables. This
means that the only effect is to add or update data (including popularity data)
for records which have been ingested since the last time the view was
refreshed.

This should be run every time before a data refresh is triggered.
"""
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from common.constants import POSTGRES_CONN_ID
from common.popularity import sql
from data_refresh import reporting
from data_refresh.data_refresh_types import DataRefresh


UPDATE_DB_VIEW_TASK_ID = "update_materialized_popularity_view"


def create_refresh_view_data_task(data_refresh: DataRefresh):
    """
    The task refreshes the materialized view for the given media type. The view collates
    popularity data for each record. Refreshing has the effect of adding popularity data
    for records that were ingested since the last time the view was refreshed, and
    updating popularity data for existing records. It also creates a reporting task
    which will report the status of the matview refresh once it is complete.

    Required Arguments:

    data_refresh: configuration information for the data refresh
    """
    refresh_matview = PythonOperator(
        task_id=UPDATE_DB_VIEW_TASK_ID,
        python_callable=sql.update_db_view,
        op_args=[POSTGRES_CONN_ID, data_refresh.media_type],
        execution_timeout=data_refresh.refresh_matview_timeout,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
        doc_md=create_refresh_view_data_task.__doc__,
    )

    refresh_status = PythonOperator(
        task_id=f"report_{UPDATE_DB_VIEW_TASK_ID}_status",
        python_callable=reporting.report_status,
        op_kwargs={
            "media_type": data_refresh.media_type,
            "dag_id": data_refresh.dag_id,
            "message": "Matview refresh complete | "
            "_Next: ingestion server data refresh_",
        },
    )

    refresh_matview >> refresh_status

    return refresh_matview
