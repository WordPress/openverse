"""
# Refresh Popularity Metrics TaskGroup Factory
This file generates a TaskGroup that refreshes the underlying popularity DB
tables, using a factory function.

This step updates any changes to popularity metrics, and recalculates the
popularity constants. It should be run at least once every month, or whenever
a new popularity metric is added. Scheduling is handled in the parent data
refresh DAG.
"""
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from common.constants import POSTGRES_CONN_ID
from common.popularity import sql
from data_refresh import reporting
from data_refresh.data_refresh_types import DataRefresh


GROUP_ID = "refresh_popularity_metrics_and_constants"
UPDATE_MEDIA_POPULARITY_METRICS_TASK_ID = "update_media_popularity_metrics_table"
UPDATE_MEDIA_POPULARITY_CONSTANTS_TASK_ID = "update_media_popularity_constants_view"


def create_refresh_popularity_metrics_task_group(data_refresh: DataRefresh):
    """
    This factory method instantiates a TaskGroup that will update the popularity
    DB tables for the given media type, including percentiles and popularity
    metrics. It also creates a reporting tasks which will report the status of the
    various steps once they complete.

    Required Arguments:

    data_refresh:  configuration data for the data refresh
    """
    media_type = data_refresh.media_type
    execution_timeout = data_refresh.refresh_metrics_timeout

    with TaskGroup(group_id=GROUP_ID) as refresh_all_popularity_data:
        update_metrics = PythonOperator(
            task_id=UPDATE_MEDIA_POPULARITY_METRICS_TASK_ID,
            python_callable=sql.update_media_popularity_metrics,
            op_args=[POSTGRES_CONN_ID, media_type],
            execution_timeout=execution_timeout,
            doc=(
                "Updates the popularity metrics table, adding any new "
                "popularity metrics and updating the configured percentile."
            ),
        )

        update_metrics_status = PythonOperator(
            task_id=f"report_{UPDATE_MEDIA_POPULARITY_METRICS_TASK_ID}_status",
            python_callable=reporting.report_status,
            op_kwargs={
                "media_type": media_type,
                "dag_id": data_refresh.dag_id,
                "message": "Popularity metrics update complete | "
                "_Next: popularity constants view update_",
            },
        )

        update_constants = PythonOperator(
            task_id=UPDATE_MEDIA_POPULARITY_CONSTANTS_TASK_ID,
            python_callable=sql.update_media_popularity_constants,
            op_args=[POSTGRES_CONN_ID, media_type],
            execution_timeout=execution_timeout,
            doc=(
                "Updates the popularity constants view. This completely "
                "recalculates the popularity constants for each provider."
            ),
        )

        update_constants_status = PythonOperator(
            task_id=f"report_{UPDATE_MEDIA_POPULARITY_CONSTANTS_TASK_ID}_status",
            python_callable=reporting.report_status,
            op_kwargs={
                "media_type": media_type,
                "dag_id": data_refresh.dag_id,
                "message": "Popularity constants view update complete | "
                "_Next: refresh matview_",
            },
        )

        update_metrics >> [update_constants, update_metrics_status]
        update_constants >> update_constants_status

    return refresh_all_popularity_data
