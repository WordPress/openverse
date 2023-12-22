"""
# Data Refresh DAG Factory
This file generates our data refresh DAGs using a factory function.
For the given media type these DAGs will initiate a data refresh on the
ingestion server and await the success or failure of that task.

A data refresh occurs on the Ingestion server in the Openverse project. This is a task
which imports data from the upstream Catalog database into the API, copies contents
to a new Elasticsearch index, and finally makes the index "live". This process is
necessary to make new content added to the Catalog by our provider DAGs available
to the API. You can read more in the [README](
https://github.com/WordPress/openverse/blob/main/ingestion_server/README.md
) Importantly, the data refresh TaskGroup is also configured to handle concurrency
requirements of the Ingestion server. Finally, once the origin indexes have been
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
from airflow.operators.python import PythonOperator

from common.constants import (
    DAG_DEFAULT_ARGS,
    OPENLEDGER_API_CONN_ID,
    XCOM_PULL_TEMPLATE,
)
from common.sql import PGExecuteQueryOperator, single_value
from data_refresh.data_refresh_task_factory import create_data_refresh_task_group
from data_refresh.data_refresh_types import DATA_REFRESH_CONFIGS, DataRefresh
from data_refresh.reporting import report_record_difference


logger = logging.getLogger(__name__)


def create_data_refresh_dag(data_refresh: DataRefresh, external_dag_ids: Sequence[str]):
    """
    Instantiate a DAG for a data refresh.

    This DAG will run the data refresh for the given `media_type`.

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

        # Get the current number of records in the target API table
        before_record_count = PGExecuteQueryOperator(
            task_id="get_before_record_count",
            conn_id=OPENLEDGER_API_CONN_ID,
            sql=count_sql,
            handler=single_value,
            return_last=True,
        )

        # Trigger the data refresh on the remote ingestion server, and wait
        # for it to complete.
        data_refresh_group = create_data_refresh_task_group(
            data_refresh, external_dag_ids
        )

        # Get the final number of records in the API table after the refresh
        after_record_count = PGExecuteQueryOperator(
            task_id="get_after_record_count",
            conn_id=OPENLEDGER_API_CONN_ID,
            sql=count_sql,
            handler=single_value,
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

        # Set up task dependencies
        before_record_count >> data_refresh_group
        data_refresh_group >> after_record_count >> report_counts

    return dag


# Generate a data refresh DAG for each DATA_REFRESH_CONFIG.
all_data_refresh_dag_ids = {refresh.dag_id for refresh in DATA_REFRESH_CONFIGS.values()}

for data_refresh in DATA_REFRESH_CONFIGS.values():
    # Construct a set of all data refresh DAG ids other than the current DAG
    other_dag_ids = all_data_refresh_dag_ids - {data_refresh.dag_id}

    # Generate the DAG for this config, dependent on all the others
    globals()[data_refresh.dag_id] = create_data_refresh_dag(
        data_refresh, other_dag_ids
    )
