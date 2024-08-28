"""# TODO"""

import logging
from dataclasses import asdict
from typing import NamedTuple

from airflow.decorators import task, task_group

from common.constants import POSTGRES_API_CONN_IDS, Environment
from common.sql import fetch_all, run_sql
from data_refresh.data_refresh_types import DataRefreshConfig


logger = logging.getLogger(__name__)


class TableIndex(NamedTuple):
    index_name: str
    temp_index_name: str
    index_def: str


@task
def transform_index_def(existing_index_def: str, temp_table_name: str):
    """
    Given a CREATE INDEX statement for an index on the existing media table, return a
    transformed statement that can be run to apply an identical index to the temp table.
    """
    is_pk = "(id)" in existing_index_def
    tokens = existing_index_def.split(" ")

    # The index name always follows the word 'INDEX' in the def,
    # e.g. `CREATE [UNIQUE] INDEX {index_name}`
    index_name_idx = tokens.index("INDEX") + 1
    old_index_name = tokens[index_name_idx]
    # Avoid a naming collision with the existing index by prepending
    # `temp_import` to the index name. Later when the temp table is promoted,
    # and the current media table is deleted, the indices will be restored
    # to their original names.
    temp_index_name = f"temp_import_{old_index_name}"
    tokens[index_name_idx] = temp_index_name

    # Update the table name to the temp table. The table name always follows
    # the word 'ON' in the def, e.g. `ON public.audio`
    table_name_idx = tokens.index("ON") + 1
    schema_name, table_name = tokens[table_name_idx].split(".")
    tokens[table_name_idx] = f"{schema_name}.{temp_table_name}"

    return TableIndex(
        old_index_name,
        temp_index_name,
        # The primary key index already exists, so we do not need to create a new one.
        " ".join(tokens) if not is_pk else "",
    )


@task_group(group_id="regenerate_table_indices")
def generate_table_indices_for_table(
    table_name: str, temp_table_name: str, postgres_conn_id: str
):
    """
    Apply all indices on the main media table to the temp table. Indices will be given
    names prefixed with `temp_import_` in this step to avoid collisions, and renamed
    later when the table is promoted.
    """
    # for each table in table_mappings, generate indices
    # Get the existing index defs from the current media table. This returns a dictionary mapping
    # index names to their existing CREATE statements
    existing_index_defs = run_sql.override(task_id="get_existing_index_defs")(
        postgres_conn_id=postgres_conn_id,
        sql_template="SELECT indexdef FROM pg_indexes WHERE tablename='{table_name}'",
        handler=fetch_all,
        table_name=table_name,
    )

    # Transform the CREATE statements so they can be used to apply to the temp table
    new_index_defs = transform_index_def.partial(
        temp_table_name=temp_table_name
    ).expand(existing_index_def=existing_index_defs)

    # Create the new indices on the temp table
    new_table_indices = run_sql.partial(
        postgres_conn_id=postgres_conn_id,
    ).expand(
        sql_template=[
            new_index.index_def
            for new_index in new_index_defs
            if new_index.index_def is not None
        ]
    )

    # Return the names of the newly created indices
    return new_table_indices


@task_group
def generate_table_indices(
    data_refresh_config: DataRefreshConfig, target_environment: Environment
):
    downstream_conn_id = POSTGRES_API_CONN_IDS.get(target_environment)

    generate_table_indices_for_table.partial(
        postgres_conn_id=downstream_conn_id
    ).expand_kwargs([asdict(tm) for tm in data_refresh_config.table_mappings])
