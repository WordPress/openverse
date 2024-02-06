"""
# Popularity Refresh DAG Factory

This file generates our popularity refresh DAGs using a factory function.

For the given media type these DAGs will first update the popularity metrics table,
adding any new metrics and updating the percentile that is used in calculating the
popularity constants. It then refreshes the popularity constants view, which
recalculates the popularity constant for each provider.

Once the constants have been updated, the DAG will trigger a `batched_update`
DagRun for each provider of this media_type that is configured to support popularity
data. The batched update recalculates standardized popularity scores for all
records, using the new constant. When the updates are complete, all records have
up-to-date popularity data. This DAG can be run concurrently with data refreshes
and regular ingestion.


You can find more background information on this process in the following
implementation plan:

- [[Implementation Plan] Decoupling Popularity Calculations from the Data Refresh](
https://docs.openverse.org/projects/proposals/popularity_optimizations/20230420-implementation_plan_popularity_optimizations.html)
"""
import logging
from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from common import slack
from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID
from database.batched_update.constants import DAG_ID as BATCHED_UPDATE_DAG_ID
from popularity import sql
from popularity.popularity_refresh_types import (
    POPULARITY_REFRESH_CONFIGS,
    PopularityRefresh,
)


logger = logging.getLogger(__name__)


@task
def get_last_updated_time():
    """
    Return the current utc datetime, which will be used when building the batched
    update queries. Once new popularity constants are calculated, they will
    automatically be used to calculate popularity scores at ingestion. The popularity
    refresh need only update the scores for records which were last updated before
    this time.

    Getting this cutoff time is pulled out into a separate task to ensure that it
    runs only when the `refresh_popularity_metrics_and_constants` task is complete.
    """
    return datetime.utcnow()


def create_popularity_refresh_dag(popularity_refresh: PopularityRefresh):
    """
    Instantiate a DAG for a popularity refresh.

    For the given media type, this DAG will recalculate the popularity constants and
    then refresh all existing standardized popularity scores with the new constant.

    Required Arguments:

    popularity_refresh: dataclass containing configuration information for the DAG
    """

    SLACK_USERNAME = f"{popularity_refresh.media_type.capitalize()} Popularity Refresh"
    SLACK_EMOJI = ":database:"

    default_args = {
        **DAG_DEFAULT_ARGS,
        **popularity_refresh.default_args,
    }

    dag = DAG(
        dag_id=popularity_refresh.dag_id,
        default_args=default_args,
        start_date=popularity_refresh.start_date,
        schedule=popularity_refresh.schedule,
        max_active_runs=1,
        catchup=False,
        doc_md=__doc__,
        tags=["popularity_refresh"],
    )

    with dag:
        update_metrics = sql.update_media_popularity_metrics.override(
            task_id="update_popularity_metrics",
        )(
            postgres_conn_id=POSTGRES_CONN_ID,
            media_type=popularity_refresh.media_type,
            popularity_metrics=popularity_refresh.popularity_metrics,
        )
        update_metrics.doc = (
            "Updates the metrics and target percentiles. If a popularity"
            " metric is configured for a new provider, this step will add it"
            " to the metrics table."
        )

        update_metrics_status = slack.notify_slack.override(
            task_id="report_update_popularity_metrics_status"
        )(
            text="Popularity metrics update complete | _Next: popularity"
            " constants update_",
            username=SLACK_USERNAME,
            icon_emoji=SLACK_EMOJI,
            dag_id=popularity_refresh.dag_id,
        )

        update_constants = (
            sql.update_percentile_and_constants_for_provider.override(
                group_id="refresh_popularity_metrics_and_constants",
            )
            .partial(
                postgres_conn_id=POSTGRES_CONN_ID,
                media_type=popularity_refresh.media_type,
                execution_timeout=popularity_refresh.refresh_metrics_timeout,
                popularity_metrics=popularity_refresh.popularity_metrics,
            )
            .expand(provider=list(popularity_refresh.popularity_metrics.keys()))
        )
        update_constants.doc = (
            "Recalculate the percentile values and popularity constants"
            " for each provider, and update them in the metrics table. The"
            " popularity constants will be used to calculate standardized"
            " popularity scores."
        )

        update_constants_status = slack.notify_slack.override(
            task_id="report_update_popularity_metrics_status"
        )(
            text="Popularity constants update complete | _Next: refresh"
            " popularity scores_",
            username=SLACK_USERNAME,
            icon_emoji=SLACK_EMOJI,
            dag_id=popularity_refresh.dag_id,
        )

        # Once popularity constants have been calculated, establish the cutoff time
        # after which records that have updates do not need to be refreshed.
        get_cutoff_time = get_last_updated_time()

        # For each provider that supports popularity data for this media type, trigger a
        # batched_update to recalculate all old standardized popularity scores using the
        # newly refreshed constant.
        refresh_popularity_scores = TriggerDagRunOperator.partial(
            task_id="refresh_popularity",
            trigger_dag_id=BATCHED_UPDATE_DAG_ID,
            # Wait for all the dagruns to finish
            wait_for_completion=True,
            # Release the worker slot while waiting
            deferrable=True,
            poke_interval=popularity_refresh.poke_interval,
            execution_timeout=popularity_refresh.refresh_popularity_timeout,
            retries=0,
        ).expand(
            # Build the conf for each provider
            conf=sql.get_providers_update_confs(
                POSTGRES_CONN_ID, popularity_refresh, get_cutoff_time
            )
        )

        notify_complete = slack.notify_slack(
            text=(
                f"{popularity_refresh.media_type.capitalize()} Popularity Refresh"
                " Complete"
            ),
            username=SLACK_USERNAME,
            icon_emoji=SLACK_EMOJI,
            dag_id=popularity_refresh.dag_id,
        )

        # Set up task dependencies
        update_metrics >> [update_metrics_status, update_constants]
        update_constants >> [update_constants_status, get_cutoff_time]
        get_cutoff_time >> refresh_popularity_scores >> notify_complete

    return dag


# Generate a popularity refresh DAG for each media type.
for popularity_refresh in POPULARITY_REFRESH_CONFIGS:
    globals()[popularity_refresh.dag_id] = create_popularity_refresh_dag(
        popularity_refresh
    )
