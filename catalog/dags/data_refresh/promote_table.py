"""# TODO"""

import logging
from dataclasses import asdict
from typing import NamedTuple

from airflow.decorators import task, task_group
from airflow.utils.trigger_rule import TriggerRule

from common.constants import POSTGRES_API_CONN_IDS, Environment
from common.sql import fetch_all, run_sql
from data_refresh import queries
from data_refresh.data_refresh_types import DataRefreshConfig


logger = logging.getLogger(__name__)


class TableIndex(NamedTuple):
    index_name: str
    temp_index_name: str
    index_def: str


class ConstraintInfo(NamedTuple):
    constraint_table: str
    constraint_name: str
    constraint_statement: str


def fetch_all_tuples(cursor):
    try:
        rows = cursor.fetchall()
        return [ConstraintInfo(row[0], row[1], row[2]) for row in rows]
    except Exception as e:
        raise ValueError("Unable to extract expected row data from cursor") from e


def _transform_index_def(
    existing_index_def: str, temp_table_name: str, table_name: str
) -> str:
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
    schema_name, table_name = tokens[table_name_idx].split(".")
    tokens[table_name_idx] = f"{schema_name}.{temp_table_name}"

    return TableIndex(old_index_name, temp_index_name, " ".join(tokens))


@task
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


@task
def create_table_indices(postgres_conn_id: str, index_configs: list[TableIndex]):
    for index_config in index_configs:
        if "(id)" in index_config.index_def:
            # Skip the primary key index, as this already exists
            logger.info(f"Skipping adding {index_config.index_name} index.")
            continue

        # Create the index
        run_sql.function(
            postgres_conn_id=postgres_conn_id, sql_template=index_config.index_def
        )


def _is_foreign_key(_statement, table):
    return f"REFERENCES {table}(" in _statement


def _remap_constraint(
    constraint_name: str,
    constraint_table: str,
    constraint_statement: str,
    table_name: str,
    temp_table_name: str,
) -> list[str]:
    """Produce ALTER TABLE ... statements for each constraint."""

    # Drop the existing constraint from the live tale
    alterations = [
        queries.DROP_CONSTRAINT_QUERY.format(
            constraint_table=constraint_table, constraint_name=constraint_name
        )
    ]

    # If the constraint applied directly to the media table, then
    # we now apply it to the temp table
    if constraint_table == table_name:
        alterations.append(
            queries.ADD_CONSTRAINT_QUERY.format(
                constraint_name=constraint_name,
                constraint_table=temp_table_name,
                constraint_statement=constraint_statement,
            )
        )

    # Constraint is a foreign key constraint which references the media table.
    # Build the alter table statement for this case.
    else:
        tokens = constraint_statement.split(" ")

        # Point the constraint to the new table by replacing the referenced table name (always
        # appears after the word `REFERENCES`) with the temp table.
        reference_idx = tokens.index("REFERENCES") + 1
        table_reference = tokens[reference_idx]
        new_reference = table_reference.replace(f"{table_name}(", f"{temp_table_name}(")
        tokens[reference_idx] = new_reference
        new_constraint_statement = " ".join(tokens)

        alterations.append(
            queries.ADD_CONSTRAINT_QUERY.format(
                constraint_table=constraint_table,
                constraint_name=constraint_name,
                constraint_statement=new_constraint_statement,
            )
        )

    return alterations


def _generate_delete_orphans(
    constraint_statement: str, constraint_table: str, temp_table_name: str
):
    """
    Parse the foreign key statement and generate the deletion statement.

    Takes a foreign key constraint statement from a different API table, which
    references the media table being replaced. It is possible that some records which
    exist in the current (live) media table may no longer exist in the new table
    (for example, records that were moved to a `deleted_media` table as part of the
    `delete_records` DAG). It is necessary to DROP any records in related tables
    that have a foreign key reference to records that will no longer exist when
    the tables are swapped.

    Example: if the following CONSTRAINT exists on the `imagelist_images` table:
    `FOREIGN KEY (imagelist_id) REFERENCES imagelist(id) DEFERRABLE INITIALLY DEFERRED;`

    Then the following DELETE statement will be generated to drop records from
    `imagelist_images` which reference images that do not exist in the temp table:
    ```
    DELETE FROM imagelist_images AS fk_table
    WHERE NOT EXISTS(
        SELECT 1 FROM temp_import_image AS r
        WHERE r.id = fk.imagelist_id
    );
    ```
    """

    # Example foreign key constraint statement:
    # `FOREIGN KEY (moderator_id) REFERENCES auth_us`

    tokens = constraint_statement.split(" ")
    # The foreign key field always comes after the word `KEY`
    foreign_key_field_idx = tokens.index("KEY") + 1
    # The field referenced by the foreign key
    referenced_field_idx = tokens.index("REFERENCES") + 1

    foreign_key_field = tokens[foreign_key_field_idx].strip("()")
    # We will replace the referenced table with the temp table
    _, referenced_field = tokens[referenced_field_idx].strip(")").split("(")

    return queries.DELETE_ORPHANS_QUERY.format(
        foreign_key_table=constraint_table,
        foreign_key_field=foreign_key_field,
        referenced_table=temp_table_name,
        referenced_field=referenced_field,
    )


@task
def generate_constraints_for_table(
    all_constraints: list[ConstraintInfo], table_name: str, temp_table_name: str
):
    """
    Produce `ALTER TABLE...` statements needed to drop constraints from the
    live (old) tables and remap them to the temp tables.
    """
    # `ALTER TABLE...` statements for applying the new constraints
    remap_constraints = []
    # Statements for dropping records in related tables that reference records
    # that exist in the current (live) media table but not the new one.
    # These must be dropped before other constraints can be applied.
    drop_orphans = []

    for constraint in all_constraints:
        constraint_statement = constraint.constraint_statement
        constraint_table = constraint.constraint_table

        # Consider all constraints that either apply directly to the given table or
        # which may reference it from another table (foreign key constraints).
        # Ignore PRIMARY KEY statements and UNIQUE statements, which are already
        # enforced via the table indices copied in an earlier task
        is_fk = _is_foreign_key(constraint_statement, table_name)
        if (
            (constraint_table == table_name or is_fk)
            and "PRIMARY KEY" not in constraint_statement
            and "UNIQUE" not in constraint_statement
        ):
            # Generate the `ALTER TABLE...` statements needed to drop this constraint
            # from the live table and apply it to the temp table.
            alter_statements = _remap_constraint(
                constraint.constraint_name,
                constraint_table,
                constraint_statement,
                table_name,
                temp_table_name,
            )
            remap_constraints.extend(alter_statements)

            # If the constraint was a foreign key constraint, TODO
            if is_fk:
                delete_orphans = _generate_delete_orphans(
                    constraint_statement, constraint_table, temp_table_name
                )
                drop_orphans.append(delete_orphans)

    constraint_statements = []
    # Drop orphans first
    constraint_statements.extend(drop_orphans)
    constraint_statements.extend(remap_constraints)

    return constraint_statements


@task
def apply_constraints_to_table(postgres_conn_id: str, constraints: list[str]):
    for constraint in constraints:
        run_sql.function(postgres_conn_id=postgres_conn_id, sql_template=constraint)


@task_group(group_id="remap_table_indices_to_table")
def remap_table_indices_to_table(
    table_name: str, temp_table_name: str, postgres_conn_id: str
):
    """
    Apply all indices on the main media table to the temp table. Indices will be given
    names prefixed with `temp_import_` in this step to avoid collisions, and renamed
    later when the table is promoted.
    """
    # Get the CREATE statements for the indices applied to the live (old) table
    existing_index_defs = run_sql.override(
        task_id="get_existing_index_defs", trigger_rule=TriggerRule.NONE_FAILED
    )(
        postgres_conn_id=postgres_conn_id,
        sql_template=queries.SELECT_TABLE_INDICES_QUERY,
        handler=fetch_all,
        table_name=table_name,
    )

    # Transform the CREATE statements so they can be used to apply identical indices
    # to the temp table
    new_index_configs = transform_index_defs(
        temp_table_name=temp_table_name,
        table_name=table_name,
        existing_index_defs=existing_index_defs,
    )

    # Actually create the new indices on the temp table
    create_table_indices(
        postgres_conn_id=postgres_conn_id, index_configs=new_index_configs
    )

    # Return the information for the newly created indices, so that they can later
    # be renamed to match the live index names
    return new_index_configs


@task_group(group_id="remap_table_constraints_to_table")
def remap_table_constraints_to_table(
    table_name: str, temp_table_name: str, postgres_conn_id: str
):
    all_constraints = run_sql.override(task_id="get_all_existing_constraints")(
        postgres_conn_id=postgres_conn_id,
        sql_template=queries.SELECT_ALL_CONSTRAINTS_QUERY,
        handler=fetch_all_tuples,
    )

    # Generate SQL for remapping constraints from the table to the temp_table
    remapped_constraints = generate_constraints_for_table(
        all_constraints=all_constraints,
        table_name=table_name,
        temp_table_name=temp_table_name,
    )

    apply_constraints_to_table(
        postgres_conn_id=postgres_conn_id, constraints=remapped_constraints
    )


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


@task_group(group_id="promote_table")
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


@task_group(group_id="promote_tables")
def promote_tables(
    data_refresh_config: DataRefreshConfig, target_environment: Environment
):
    """TODO. Promote the temporary table in the API database to the main one, and delete the original."""

    downstream_conn_id = POSTGRES_API_CONN_IDS.get(target_environment)

    promote_table.partial(
        postgres_conn_id=downstream_conn_id,
    ).expand_kwargs([asdict(tm) for tm in data_refresh_config.table_mappings])
