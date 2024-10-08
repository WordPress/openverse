"""
# Remap Table Indices

This file contains TaskGroups related to rmampping the table indices from the live media table onto the temp table to prepare it for promotion.
"""

import logging
from typing import NamedTuple

from airflow.decorators import task, task_group

from common.sql import fetch_all, run_sql
from data_refresh import queries


logger = logging.getLogger(__name__)


class TableIndex(NamedTuple):
    index_name: str
    temp_index_name: str
    index_def: str


def _transform_index_def(
    existing_index_def: str, temp_table_name: str, table_name: str
) -> TableIndex:
    """
    Given a CREATE INDEX statement for an index on the existing media table, return a
    transformed statement that can be run to apply an identical index to the temp table.
    """
    is_pk = "(id)" in existing_index_def
    tokens = existing_index_def.split(" ")

    # Avoid a naming collision with the existing index by prepending
    # `temp_import` to the index name. Later when the temp table is promoted,
    # and the current media table is deleted, the indices will be restored
    # to their original names.
    # The index name always follows the word 'INDEX' in the def,
    # e.g. `CREATE [UNIQUE] INDEX {index_name}`
    index_name_idx = tokens.index("INDEX") + 1
    old_index_name = tokens[index_name_idx]
    # For most indices, we just prefix the index name with `temp_import_`. The pk
    # index is automatically created at an earlier step and has a different
    # naming convention.
    temp_index_name = (
        f"temp_import_{old_index_name}"
        if not is_pk
        else f"temp_import_{table_name}_pkey"
    )
    tokens[index_name_idx] = temp_index_name

    # Update the table name to the temp table. The table name always follows
    # the word 'ON' in the def, e.g. `ON public.audio`
    table_name_idx = tokens.index("ON") + 1
    schema_name, table_name = tokens[table_name_idx].split(".", maxsplit=1)
    tokens[table_name_idx] = f"{schema_name}.{temp_table_name}"

    return TableIndex(old_index_name, temp_index_name, " ".join(tokens))


@task(map_index_template="{{ task.op_kwargs['table_name'] }}")
def transform_index_defs(
    existing_index_defs: list[str], temp_table_name: str, table_name: str
) -> list[TableIndex]:
    """
    Given a CREATE INDEX statement for an index on the existing media table, return a
    transformed statement that can be run to apply an identical index to the temp table.
    """
    return [
        _transform_index_def(index_def, temp_table_name, table_name)
        for index_def in existing_index_defs
    ]


@task(map_index_template="{{ task.op_kwargs['table_name'] }}")
def create_table_indices(
    postgres_conn_id: str, table_name: str, index_configs: list[TableIndex]
):
    logger.info(f"Creating indices for `{table_name}`.'")
    for index_config in index_configs:
        if "(id)" in index_config.index_def:
            # Skip the primary key index, as this already exists
            logger.info(f"Skipping adding {index_config.index_name} index.")
            continue

        # Create the index
        run_sql.function(
            postgres_conn_id=postgres_conn_id, sql_template=index_config.index_def
        )

    return index_configs


@task_group
def remap_table_indices_to_table(
    table_name: str, temp_table_name: str, postgres_conn_id: str
):
    """
    Apply all indices on the main media table to the temp table. Indices will be given
    names prefixed with `temp_import_` in this step to avoid collisions, and renamed
    later when the table is promoted.
    """
    # Get the CREATE statements for the indices applied to the live (old) table
    existing_index_defs = run_sql.override(task_id="get_existing_index_defs")(
        postgres_conn_id=postgres_conn_id,
        sql_template=queries.SELECT_TABLE_INDICES_QUERY,
        handler=fetch_all,
        table_name=table_name,
        map_index_template=table_name,
    )

    # Transform the CREATE statements so they can be used to apply identical indices
    # to the temp table
    new_index_configs = transform_index_defs(
        temp_table_name=temp_table_name,
        table_name=table_name,
        existing_index_defs=existing_index_defs,
    )

    # Actually create the new indices on the temp table
    indices = create_table_indices(
        postgres_conn_id=postgres_conn_id,
        table_name=table_name,
        index_configs=new_index_configs,
    )

    # Return the information for the newly created indices, so that they can later
    # be renamed to match the live index names
    return indices
