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
import datetime
import logging
import os

from airflow import DAG
from airflow.decorators import task
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from popularity.popularity_refresh_types import (
    POPULARITY_REFRESH_CONFIGS,
    PopularityRefresh,
)
from popularity.refresh_popularity_metrics_task_factory import (
    create_refresh_popularity_metrics_task_group,
)

from common import slack
from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID
from common.popularity import sql
from database.batched_update.constants import DAG_ID as BATCHED_UPDATE_DAG_ID


logger = logging.getLogger(__name__)


@task
def notify_slack(text: str, media_type: str, dag_id: str) -> None:
    slack.send_message(
        text,
        username=f"{media_type} Popularity Refresh",
        icon_emoji=":database:",
        dag_id=dag_id,
    )


@task
def get_providers_update_confs(
    postgres_conn_id: str, popularity_refresh: PopularityRefresh
):
    """
    Build a list of DagRun confs for each provider of this media type. The confs will
    be used by the `batched_update` DAG to perform a batched update of all existing
    records, to recalculate their standardized_popularity with the new popularity
    constant. Providers that do not support popularity data are omitted.
    """
    # For the media type, get a list of the providers who support popularity data
    providers = sql.get_providers_with_popularity_data_for_media_type(
        postgres_conn_id, popularity_refresh.media_type
    )

    # Once the new popularity constants are calculated, they will automatically be used
    # to calculate popularity scores at ingestion. The popularity refresh need only
    # update the scores for records which were last updated before this time.
    last_updated_time = datetime.datetime.utcnow()

    # For each provider, create a conf that will be used by the batched_update to
    # refresh standardized popularity scores.
    return [
        {
            # Uniquely identify the query
            "query_id": (
                f"{provider}_popularity_refresh_{last_updated_time.strftime('%Y%m%d')}"
            ),
            "table_name": popularity_refresh.media_type,
            # Query used to select records that should be refreshed
            "select_query": (
                f"WHERE provider='{provider}' AND updated_on <"
                f"'{last_updated_time.strftime('%Y-%m-%d %H:%M:%S')}'"
            ),
            # Query used to update the standardized_popularity
            "update_query": sql.format_update_standardized_popularity_query(
                popularity_refresh.media_type
            ),
            "batch_size": 10_000,
            "update_timeout": (
                popularity_refresh.refresh_popularity_batch_timeout.total_seconds()
            ),
            "dry_run": False,
            "resume_update": False,
        }
        for provider in providers
    ]


def create_popularity_refresh_dag(popularity_refresh: PopularityRefresh):
    """
    Instantiate a DAG for a popularity refresh.

    For the given media type, this DAG will recalculate the popularity constants and
    then refresh all existing standardized popularity scores with the new constant.

    Required Arguments:

    popularity_refresh: dataclass containing configuration information for the DAG
    """
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
        poke_interval = int(os.getenv("DATA_REFRESH_POKE_INTERVAL", 60 * 30))

        # Refresh the underlying popularity tables. This step recalculates the
        # popularity constants, which will later be used to calculate updated
        # standardized popularity scores.
        refresh_popularity_metrics = create_refresh_popularity_metrics_task_group(
            popularity_refresh
        )

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
            poke_interval=poke_interval,
            retries=0,
        ).expand(
            # Build the conf for each provider
            conf=get_providers_update_confs(POSTGRES_CONN_ID, popularity_refresh)
        )

        notify_complete = notify_slack(
            text=(
                f"{popularity_refresh.media_type.capitalize()} Popularity Refresh"
                " Complete"
            ),
            media_type=popularity_refresh.media_type,
            dag_id=popularity_refresh.dag_id,
        )

        # Set up task dependencies
        refresh_popularity_metrics >> refresh_popularity_scores >> notify_complete

    return dag


# Generate a popularity refresh DAG for each media type.
for popularity_refresh in POPULARITY_REFRESH_CONFIGS:
    globals()[popularity_refresh.dag_id] = create_popularity_refresh_dag(
        popularity_refresh
    )
