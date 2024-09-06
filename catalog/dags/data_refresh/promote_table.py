"""
# Promote Table

This file contains TaskGroups related to promoting the API DB tables as part of the data refresh.

In this TaskGroup, indices and constraints from the original table are applied to the temp table before dropping the original table and "promoting" the temp table by renaming it.
"""

import logging
from dataclasses import asdict

from airflow.decorators import task, task_group

from common.constants import POSTGRES_API_CONN_IDS, Environment
from common.sql import run_sql
from data_refresh import queries
from data_refresh.data_refresh_types import DataRefreshConfig
from data_refresh.remap_table_constraints import remap_table_constraints_to_table
from data_refresh.remap_table_indices import TableIndex, remap_table_indices_to_table


logger = logging.getLogger(__name__)


@task
def get_go_live_query(
    table_name: str, temp_table_name: str, index_mapping: list[TableIndex]
):
    """Get the query for replacing the original media table with the new temp table."""

    # The remapped indices on the temp table all have temporary names to avoid
    # naming collisions with the indices on the original table. Prepare the ALTER
    # TABLE statements for restoring them to their original names once the original
    # table is dropped.
    restore_index_names = ("\n        ").join(
        [
            queries.RENAME_INDEX_QUERY.format(
                old_name=index.temp_index_name, new_name=index.index_name
            )
            for index in index_mapping
        ]
    )

    return queries.GO_LIVE_QUERY.format(
        table_name=table_name,
        temp_table_name=temp_table_name,
        restore_index_names=restore_index_names,
    )


@task_group
def promote_table(
    postgres_conn_id: str,
    downstream_table_name: str,
    temp_table_name: str,
):
    # Recreate indices from the original table.
    remap_table_indices = remap_table_indices_to_table(
        postgres_conn_id=postgres_conn_id,
        table_name=downstream_table_name,
        temp_table_name=temp_table_name,
    )

    # Recreate constraints from the original table.
    remap_table_constraints = remap_table_constraints_to_table(
        postgres_conn_id=postgres_conn_id,
        table_name=downstream_table_name,
        temp_table_name=temp_table_name,
    )

    # Get the query to replace the current media table with the temp table.
    go_live_query = get_go_live_query(
        table_name=downstream_table_name,
        temp_table_name=temp_table_name,
        index_mapping=remap_table_indices,
    )

    # Run the promotion
    run_sql.override(task_id="promote")(
        postgres_conn_id=postgres_conn_id, sql_template=go_live_query
    )

    remap_table_indices >> remap_table_constraints >> go_live_query


@task_group
def promote_tables(
    data_refresh_config: DataRefreshConfig, target_environment: Environment
):
    """
    Promote the temporary table in the API database to the main one after remapping all
    constraints and indices from the original table, then delete the original.
    """

    downstream_conn_id = POSTGRES_API_CONN_IDS.get(target_environment)

    promote_table.partial(
        postgres_conn_id=downstream_conn_id,
    ).expand_kwargs([asdict(tm) for tm in data_refresh_config.table_mappings])
