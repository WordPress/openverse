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
from popularity.popularity_refresh_types import PopularityRefresh

from common.constants import POSTGRES_CONN_ID
from common.popularity import sql
from data_refresh import reporting
from data_refresh.data_refresh_types import DataRefresh


GROUP_ID = "refresh_popularity_metrics_and_constants"
UPDATE_MEDIA_POPULARITY_METRICS_TASK_ID = "update_media_popularity_metrics_table"
DROP_MEDIA_POPULARITY_CONSTANTS_TASK_ID = "drop_media_popularity_constants_view"
CREATE_MEDIA_POPULARITY_CONSTANTS_TASK_ID = "create_media_popularity_constants_view"


def create_refresh_popularity_metrics_task_group(
    refresh_config: DataRefresh | PopularityRefresh,
):
    """
    Create tasks related to refreshing popularity statistics.

    This factory method instantiates a TaskGroup that will update the popularity
    DB tables for the given media type, including percentiles and popularity
    metrics. It also creates a reporting tasks which will report the status of the
    various steps once they complete.

    Required Arguments:

    refresh_config:  configuration data for the refresh
    """
    media_type = refresh_config.media_type
    execution_timeout = refresh_config.refresh_metrics_timeout

    with TaskGroup(group_id=GROUP_ID) as refresh_all_popularity_data:
        update_metrics = PythonOperator(
            task_id=UPDATE_MEDIA_POPULARITY_METRICS_TASK_ID,
            python_callable=sql.update_media_popularity_metrics,
            op_kwargs={
                "postgres_conn_id": POSTGRES_CONN_ID,
                "media_type": media_type,
            },
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
                "dag_id": refresh_config.dag_id,
                "message": "Popularity metrics update complete | "
                "_Next: popularity constants view update_",
            },
        )

        drop_constants = PythonOperator(
            task_id=DROP_MEDIA_POPULARITY_CONSTANTS_TASK_ID,
            python_callable=sql.drop_media_popularity_constants,
            op_kwargs={
                "postgres_conn_id": POSTGRES_CONN_ID,
                "media_type": media_type,
            },
            execution_timeout=execution_timeout,
            doc=("Drops the popularity constants view."),
        )

        create_constants = PythonOperator(
            task_id=CREATE_MEDIA_POPULARITY_CONSTANTS_TASK_ID,
            python_callable=sql.create_media_popularity_constants_view,
            op_kwargs={
                "postgres_conn_id": POSTGRES_CONN_ID,
                "media_type": media_type,
            },
            execution_timeout=execution_timeout,
            doc=(
                "Recreates the popularity constants view. This completely "
                "recalculates the popularity constants for each provider."
            ),
        )

        recreate_constants_status = PythonOperator(
            task_id=f"report_{CREATE_MEDIA_POPULARITY_CONSTANTS_TASK_ID}_status",
            python_callable=reporting.report_status,
            op_kwargs={
                "media_type": media_type,
                "dag_id": refresh_config.dag_id,
                "message": "Popularity constants view update complete | "
                "_Next: refresh matview_",
            },
        )

        update_metrics >> [drop_constants, update_metrics_status]
        drop_constants >> create_constants >> recreate_constants_status

    return refresh_all_popularity_data
