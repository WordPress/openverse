"""
# Data Refresh DAG Factory
This file generates our data refresh DAGs using a factory function.
For the given media type these DAGs will first refresh the popularity data,
then initiate a data refresh on the data refresh server and await the
success or failure of that task.

Popularity data for each media type is collated in a materialized view. Before
initiating a data refresh, the DAG will first refresh the view in order to
update popularity data for records that have been ingested since the last refresh.
On the first run of the month, the DAG will also refresh the underlying tables,
including the percentile values and any new popularity metrics. The DAG can also
be run with the `force_refresh_metrics` option to run this refresh after the first
of the month.

Once this step is complete, the data refresh can be initiated. A data refresh
occurs on the data refresh server in the openverse-api project. This is a task
which imports data from the upstream Catalog database into the API, copies contents
to a new Elasticsearch index, and finally makes the index "live". This process is
necessary to make new content added to the Catalog by our provider DAGs available
to the API. You can read more in the [README](
https://github.com/WordPress/openverse-api/blob/main/ingestion_server/README.md
) Importantly, the data refresh TaskGroup is also configured to handle concurrency
requirements of the data refresh server. Finally, once the origin indexes have been
refreshed, the corresponding filtered index creation DAG is triggered.

You can find more background information on this process in the following
issues and related PRs:

- [[Feature] Data refresh orchestration DAG](
https://github.com/WordPress/openverse-catalog/issues/353)
- [[Feature] Merge popularity calculations and data refresh into a single DAG](
https://github.com/WordPress/openverse-catalog/issues/453)
"""
import logging
from collections.abc import Sequence

from airflow import DAG
from airflow.models.dagrun import DagRun
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.settings import SASession
from airflow.utils.session import provide_session
from airflow.utils.state import State

from common.constants import (
    DAG_DEFAULT_ARGS,
    OPENLEDGER_API_CONN_ID,
    XCOM_PULL_TEMPLATE,
)
from common.sql import PGExecuteQueryOperator
from data_refresh.data_refresh_task_factory import create_data_refresh_task_group
from data_refresh.data_refresh_types import DATA_REFRESH_CONFIGS, DataRefresh
from data_refresh.refresh_popularity_metrics_task_factory import (
    GROUP_ID as REFRESH_POPULARITY_METRICS_GROUP_ID,
)
from data_refresh.refresh_popularity_metrics_task_factory import (
    UPDATE_MEDIA_POPULARITY_METRICS_TASK_ID,
    create_refresh_popularity_metrics_task_group,
)
from data_refresh.refresh_view_data_task_factory import (
    UPDATE_DB_VIEW_TASK_ID,
    create_refresh_view_data_task,
)
from data_refresh.reporting import report_record_difference, report_status


logger = logging.getLogger(__name__)

REFRESH_MATERIALIZED_VIEW_TASK_ID = UPDATE_DB_VIEW_TASK_ID
# The first task in the refresh_popularity_metrics TaskGroup
REFRESH_POPULARITY_METRICS_TASK_ID = (
    f"{REFRESH_POPULARITY_METRICS_GROUP_ID}"
    f".{UPDATE_MEDIA_POPULARITY_METRICS_TASK_ID}"
)


def _single_value(cursor):
    try:
        row = cursor.fetchone()
        return row[0]
    except Exception as e:
        raise ValueError("Unable to extract expected row data from cursor") from e


@provide_session
def _month_check(dag_id: str, session: SASession = None) -> str:
    """
    Check whether there has been a previous DagRun this month.

    If so, return the task_id for the matview refresh task; else, return the
    task_id for refresh popularity metrics task.

    Required Arguments:

    dag_id:     id of the currently running Dag
    """
    # Get the current DagRun
    DR = DagRun
    current_dagrun = (
        session.query(DR).filter(DR.dag_id == dag_id, DR.state == State.RUNNING)
    ).first()

    # If `force_refresh_metrics` has been passed in the dagrun config, then
    # immediately return the task_id to refresh popularity metrics without
    # doing the month check.
    force_refresh_metrics = current_dagrun.conf.get("force_refresh_metrics")
    if force_refresh_metrics is not None:
        logger.info(f"`force_refresh_metrics` is set to {force_refresh_metrics}.")
        return (
            REFRESH_POPULARITY_METRICS_TASK_ID
            if force_refresh_metrics
            else REFRESH_MATERIALIZED_VIEW_TASK_ID
        )

    # Get the most recent successful dagrun for this Dag
    latest_dagrun = (
        session.query(DR)
        .filter(DR.dag_id == dag_id, DR.state == State.SUCCESS)
        .order_by(DR.start_date.desc())
    ).first()

    # No previous successful dagrun, refresh all popularity data.
    if latest_dagrun is None:
        return REFRESH_POPULARITY_METRICS_TASK_ID

    # Check if the last dagrun was in the same month as the current run
    current_date = current_dagrun.start_date
    last_dagrun_date = latest_dagrun.start_date
    is_last_dagrun_in_current_month = (
        current_date.month == last_dagrun_date.month
        and current_date.year == last_dagrun_date.year
    )

    return (
        REFRESH_POPULARITY_METRICS_TASK_ID
        if not is_last_dagrun_in_current_month
        else REFRESH_MATERIALIZED_VIEW_TASK_ID
    )


def _month_check_with_reporting(dag_id: str, media_type: str) -> str:
    """
    Wrap the monthly check function.

    This reports which step is starting and which step is next to slack.
    """
    next_task_id = _month_check(dag_id)
    next_step = {
        REFRESH_POPULARITY_METRICS_TASK_ID: "update popularity metrics",
        REFRESH_MATERIALIZED_VIEW_TASK_ID: "refresh matview",
    }.get(next_task_id, "unable to determine next step")
    message = f":horse_racing: Starting data refresh | _Next: {next_step}_"
    report_status(media_type, message, dag_id)

    return next_task_id


def create_data_refresh_dag(data_refresh: DataRefresh, external_dag_ids: Sequence[str]):
    """
    Instantiate a DAG for a data refresh.

    This DAG will run the popularity calculation and subsequent data refresh for the
    given `media_type`.

    Required Arguments:

    data_refresh:     dataclass containing configuration information for the
                      DAG
    external_dag_ids: list of ids of the other data refresh DAGs. The data refresh step
                      of this DAG will not run concurrently with the corresponding step
                      of any dependent DAG.
    """
    default_args = {
        **DAG_DEFAULT_ARGS,
        **data_refresh.default_args,
    }

    dag = DAG(
        dag_id=data_refresh.dag_id,
        default_args=default_args,
        start_date=data_refresh.start_date,
        schedule=data_refresh.schedule,
        max_active_runs=1,
        catchup=False,
        doc_md=__doc__,
        tags=["data_refresh"],
    )

    with dag:
        # Count estimate SQL for determining the number of rows in the API table. While
        # this query is not exact, it is close to accurate since the API media table
        # does not receive many (if any) updates/insertions/deletions once the data
        # refresh is complete. In testing this was shown to be accurate and fast
        # (~0.000002% off and 1/14000th of the execution time). However, the reality is
        # that this count is *not* exact, so we show it as an estimate in reports.
        count_sql = f"""
        SELECT c.reltuples::bigint AS estimate
        FROM   pg_class c
        JOIN   pg_namespace n ON n.oid = c.relnamespace
        WHERE  c.relname = '{data_refresh.media_type}'
        AND    n.nspname = 'public';
        """

        # Check if this is the first DagRun of the month for this DAG.
        month_check = BranchPythonOperator(
            task_id="month_check",
            python_callable=_month_check_with_reporting,
            op_kwargs={
                "dag_id": data_refresh.dag_id,
                "media_type": data_refresh.media_type,
            },
        )

        # Get the current number of records in the target API table
        before_record_count = PGExecuteQueryOperator(
            task_id="get_before_record_count",
            conn_id=OPENLEDGER_API_CONN_ID,
            sql=count_sql,
            handler=_single_value,
            return_last=True,
        )

        # Refresh underlying popularity tables. This is required infrequently in order
        # to update new popularity metrics and constants, so this branch is only taken
        # if it is the first run of the month (or when forced).
        refresh_popularity_metrics = create_refresh_popularity_metrics_task_group(
            data_refresh
        )

        # Refresh the materialized view. This occurs on all DagRuns and updates
        # popularity data for newly ingested records.
        refresh_matview = create_refresh_view_data_task(data_refresh)

        # Trigger the actual data refresh on the remote data refresh server, and wait
        # for it to complete.
        data_refresh_group = create_data_refresh_task_group(
            data_refresh, external_dag_ids
        )

        # Get the final number of records in the API table after the refresh
        after_record_count = PGExecuteQueryOperator(
            task_id="get_after_record_count",
            conn_id=OPENLEDGER_API_CONN_ID,
            sql=count_sql,
            handler=_single_value,
            return_last=True,
        )

        # Report the count difference to Slack
        report_counts = PythonOperator(
            task_id="report_record_counts",
            python_callable=report_record_difference,
            op_kwargs={
                "before": XCOM_PULL_TEMPLATE.format(
                    before_record_count.task_id, "return_value"
                ),
                "after": XCOM_PULL_TEMPLATE.format(
                    after_record_count.task_id, "return_value"
                ),
                "media_type": data_refresh.media_type,
                "dag_id": data_refresh.dag_id,
            },
        )

        index_suffix = XCOM_PULL_TEMPLATE.format(
            data_refresh_group.get_child_by_label("generate_index_suffix").task_id,
            "return_value",
        )
        trigger_filtered_index_creation = TriggerDagRunOperator(
            task_id=f"trigger_create_filtered_{data_refresh.media_type}_index",
            trigger_dag_id=f"create_filtered_{data_refresh.media_type}_index",
            params={
                # Force to skip data refresh DAG concurrency check
                # as the data refresh DAG will clearly already be running
                # as it is triggering the filtered index creation DAG.
                "force": True,
                "origin_index_suffix": index_suffix,
                # Match origin and destination suffixes so we can tell which
                # filtered indexes were created as part of a data refresh.
                "destination_index_suffix": index_suffix,
            },
        )

        # Set up task dependencies
        month_check >> [refresh_popularity_metrics, refresh_matview]
        before_record_count >> data_refresh_group
        refresh_popularity_metrics >> refresh_matview >> data_refresh_group
        data_refresh_group >> after_record_count >> report_counts
        data_refresh_group >> trigger_filtered_index_creation

    return dag


# Generate a data refresh DAG for each DATA_REFRESH_CONFIG.
all_data_refresh_dag_ids = {refresh.dag_id for refresh in DATA_REFRESH_CONFIGS}

for data_refresh in DATA_REFRESH_CONFIGS:
    # Construct a set of all data refresh DAG ids other than the current DAG
    other_dag_ids = all_data_refresh_dag_ids - {data_refresh.dag_id}

    # Generate the DAG for this config, dependent on all the others
    globals()[data_refresh.dag_id] = create_data_refresh_dag(
        data_refresh, other_dag_ids
    )
