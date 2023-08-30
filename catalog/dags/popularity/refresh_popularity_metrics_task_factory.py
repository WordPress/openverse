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
UPDATE_MEDIA_POPULARITY_METRICS_TASK_ID = "update_media_popularity_metrics"
UPDATE_MEDIA_POPULARITY_CONSTANTS_TASK_ID = "update_media_popularity_constants"


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
        update_metrics = sql.update_media_popularity_metrics.override(
            task_id=UPDATE_MEDIA_POPULARITY_METRICS_TASK_ID,
            execution_timeout=execution_timeout,
        )(
            postgres_conn_id=POSTGRES_CONN_ID,
            media_type=media_type,
        )
        update_metrics.doc = (
            "Updates the metrics and target percentiles. If a popularity"
            " metric is configured for a new provider, this step will add it"
            " to the metrics table."
        )

        update_metrics_status = PythonOperator(
            task_id=f"report_{UPDATE_MEDIA_POPULARITY_METRICS_TASK_ID}_status",
            python_callable=reporting.report_status,
            op_kwargs={
                "media_type": media_type,
                "dag_id": refresh_config.dag_id,
                "message": "Popularity metrics update complete | "
                "_Next: popularity constants update_",
            },
        )

        update_constants = (
            sql.update_percentile_and_constants_for_provider.override(
                group_id=UPDATE_MEDIA_POPULARITY_CONSTANTS_TASK_ID,
            )
            .partial(
                postgres_conn_id=POSTGRES_CONN_ID,
                media_type=media_type,
                execution_timeout=execution_timeout,
            )
            .expand(
                provider=[
                    provider
                    for provider in sql.POPULARITY_METRICS_BY_MEDIA_TYPE[
                        media_type
                    ].keys()
                ]
            )
        )
        update_constants.doc = (
            "Recalculate the percentile values and popularity constants"
            " for each provider, and update them in the metrics table. The"
            " popularity constants will be used to calculate standardized"
            " popularity scores."
        )

        update_constants_status = PythonOperator(
            task_id=f"report_{UPDATE_MEDIA_POPULARITY_CONSTANTS_TASK_ID}_status",
            python_callable=reporting.report_status,
            op_kwargs={
                "media_type": media_type,
                "dag_id": refresh_config.dag_id,
                "message": "Popularity constants update complete | "
                "_Next: refresh matview_",
            },
        )

        update_metrics >> [update_metrics_status, update_constants]
        update_constants >> update_constants_status

    return refresh_all_popularity_data
