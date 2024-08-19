"""
# Data Refresh DAG Factory

This file generates our data refresh DAGs for each media type and environment using a factory function. The data refresh is a process which makes new content added to the Catalog by our provider DAGs available to the API.

The data refresh has the following high level steps:

* Copy Data: An FDW extension is used to connect the API database to the upstream (catalog) database. The entire contents of the upstream media table are copied into a new temp table in the API database. This temp table will later replace the main media table in the API.
* Create Index: Create a new Elasticsearch index, matching the configuration of the existing media index.
* Distributed Reindex: Convert each record from the new temp table to the format required by an Elasticsearch document, and then reindex them into the newly created index.
* Create and Populate Filtered Index: Create a new Elasticsearch index matching the configuration of the existing filtered index, and then reindex documents into it from the new media index, applying appropriate filtering for sensitive terms.
* Reapply Constraints: Recreate indices and constraints from the original API tables on the new temp tables.
* Promote Table: Drop the old media table in the API and rename the temp table and its indices, which has the effect of promoting them/replacing the old table.
* Promote Index: Promote the new Elasticsearch index by unlinking the given alias from the existing index and moving it to the new one. (Used for both the main and filtered indices.)
* Delete Index: Delete the old Elasticsearch index. (Used for both the main and filtered indices.)

Importantly, the data refresh DAGs are also configured to handle concurrency
requirements of the reindexing steps.

You can find more background information on this process in the following
issues and related PRs:

- [[Implementation Plan] Ingestion Server Removal](
https://docs.openverse.org/projects/proposals/ingestion_server_removal/20240328-implementation_plan_ingestion_server_removal.html)
- [[Feature] Merge popularity calculations and data refresh into a single DAG](
https://github.com/WordPress/openverse-catalog/issues/453)
"""

import logging
from collections.abc import Sequence
from itertools import product

from airflow import DAG
from airflow.decorators import task_group
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

from common import cloudwatch
from common import elasticsearch as es
from common.constants import (
    DAG_DEFAULT_ARGS,
    DATA_REFRESH_POOL,
    ENVIRONMENTS,
    Environment,
)
from common.sensors.constants import ES_CONCURRENCY_TAGS
from common.sensors.single_run_external_dags_sensor import SingleRunExternalDAGsSensor
from common.sensors.utils import wait_for_external_dags_with_tag
from data_refresh.alter_data import alter_table_data
from data_refresh.copy_data import copy_upstream_tables
from data_refresh.create_and_promote_index import create_index
from data_refresh.data_refresh_types import DATA_REFRESH_CONFIGS, DataRefreshConfig
from data_refresh.distributed_reindex import perform_distributed_reindex
from data_refresh.reporting import report_record_difference


logger = logging.getLogger(__name__)


@task_group(group_id="wait_for_conflicting_dags")
def wait_for_conflicting_dags(
    data_refresh_config: DataRefreshConfig,
    external_dag_ids: list[str],
    concurrency_tag: str,
):
    # Wait to ensure that no other Data Refresh DAGs are running.
    SingleRunExternalDAGsSensor(
        task_id="wait_for_data_refresh",
        external_dag_ids=external_dag_ids,
        check_existence=True,
        poke_interval=data_refresh_config.concurrency_check_poke_interval,
        mode="reschedule",
        pool=DATA_REFRESH_POOL,
    )

    # Wait for other DAGs that operate on this ES cluster. If a new or filtered index
    # is being created by one of these DAGs, we need to wait for it to finish or else
    # the data refresh might destroy the index being used as the source index.
    # Realistically the data refresh is too slow to beat the index creation process,
    # even if it was triggered immediately after one of these DAGs; however, it is
    # always safer to avoid the possibility of the race condition altogether.
    wait_for_external_dags_with_tag.override(group_id="wait_for_es_dags")(
        tag=concurrency_tag,
        # Exclude the other data refresh DAG ids for this environment, as waiting on these
        # was handled in the previous task.
        excluded_dag_ids=external_dag_ids,
    )


def create_data_refresh_dag(
    data_refresh_config: DataRefreshConfig,
    target_environment: Environment,
    external_dag_ids: Sequence[str],
):
    """
    Instantiate a DAG for a data refresh.

    This DAG will run the data refresh for the given `media_type`.

    Required Arguments:

    data_refresh:       dataclass containing configuration information for the
                        DAG
    target_environment: the API environment in which the data refresh is performed
    external_dag_ids:   list of ids of the other data refresh DAGs. The data refresh step
                        of this DAG will not run concurrently with the corresponding step
                        of any dependent DAG.
    """
    default_args = {
        **DAG_DEFAULT_ARGS,
        **data_refresh_config.default_args,
    }

    concurrency_tag = ES_CONCURRENCY_TAGS.get(target_environment)

    dag = DAG(
        dag_id=f"{target_environment}_{data_refresh_config.dag_id}",
        dagrun_timeout=data_refresh_config.dag_timeout,
        default_args=default_args,
        start_date=data_refresh_config.start_date,
        schedule=data_refresh_config.schedule,
        render_template_as_native_obj=True,
        max_active_runs=1,
        catchup=False,
        doc_md=__doc__,
        tags=[
            "data_refresh",
            f"{target_environment}_data_refresh",
            concurrency_tag,
        ],
        render_template_as_native_obj=True,
    )

    with dag:
        # Connect to the appropriate Elasticsearch cluster
        es_host = es.get_es_host(environment=target_environment)

        # Get the current number of records in the target API table
        before_record_count = es.get_record_count_group_by_sources.override(
            task_id="get_before_record_count"
        )(
            es_host=es_host,
            index=data_refresh_config.media_type,
        )

        wait_for_dags = wait_for_conflicting_dags(
            data_refresh_config, external_dag_ids, concurrency_tag
        )

        copy_data = copy_upstream_tables(
            target_environment=target_environment,
            data_refresh_config=data_refresh_config,
        )

        alter_data = alter_table_data(
            environment=environment, data_refresh_config=data_refresh_config
        )

        # Create a new temporary index based off the configuration of the existing media index.
        # This will later replace the live index.
        target_index = create_index(
            data_refresh_config=data_refresh_config, es_host=es_host
        )

        # Disable Cloudwatch alarms that are noisy during the reindexing steps of a
        # data refresh.
        disable_alarms = PythonOperator(
            task_id="disable_sensitive_cloudwatch_alarms",
            python_callable=cloudwatch.enable_or_disable_alarms,
            op_kwargs={
                "enable": False,
            },
        )

        # Populate the Elasticsearch index.
        reindex = perform_distributed_reindex(
            environment="{{ var.value.ENVIRONMENT }}",
            target_environment=target_environment,
            target_index=target_index,
            data_refresh_config=data_refresh_config,
        )

        # TODO create_and_populate_filtered_index

        # Re-enable Cloudwatch alarms once reindexing is complete, even if it
        # failed.
        enable_alarms = PythonOperator(
            task_id="enable_sensitive_cloudwatch_alarms",
            python_callable=cloudwatch.enable_or_disable_alarms,
            op_kwargs={
                "enable": True,
            },
            trigger_rule=TriggerRule.ALL_DONE,
        )

        # TODO Promote
        # (TaskGroup that reapplies constraints, promotes new tables and indices,
        # deletes old ones)

        # Get the final number of records in the API table after the refresh
        after_record_count = es.get_record_count_group_by_sources.override(
            task_id="get_after_record_count", trigger_rule=TriggerRule.NONE_FAILED
        )(
            es_host=es_host,
            index=data_refresh_config.media_type,
        )

        # Report the count difference to Slack
        report_counts = PythonOperator(
            task_id="report_record_counts",
            python_callable=report_record_difference,
            op_kwargs={
                "before": before_record_count,
                "after": after_record_count,
                "media_type": data_refresh_config.media_type,
                "dag_id": data_refresh_config.dag_id,
            },
        )

        # Set up task dependencies
        (
            before_record_count
            >> wait_for_dags
            >> copy_data
            >> alter_data
            >> target_index
            >> disable_alarms
            >> reindex
        )
        reindex >> [enable_alarms, after_record_count]
        after_record_count >> report_counts

    return dag


# Generate data refresh DAGs for each DATA_REFRESH_CONFIG, per environment.
all_data_refresh_dag_ids = {refresh.dag_id for refresh in DATA_REFRESH_CONFIGS.values()}

for data_refresh_config, target_environment in product(
    DATA_REFRESH_CONFIGS.values(), ENVIRONMENTS
):
    # Construct a set of all data refresh DAG ids other than the current DAG
    other_dag_ids = all_data_refresh_dag_ids - {data_refresh_config.dag_id}

    globals()[data_refresh_config.dag_id] = create_data_refresh_dag(
        data_refresh_config,
        target_environment,
        [f"{target_environment}_{dag_id}" for dag_id in other_dag_ids],
    )
