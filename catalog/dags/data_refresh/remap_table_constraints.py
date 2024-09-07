"""
# Remap Table Constraints

This file contains TaskGroups related to remapping the table constraints from the live media table onto the temp table to prepare it for promotion.

"""

import logging
from typing import NamedTuple

from airflow.decorators import task, task_group

from common.sql import run_sql
from data_refresh import queries


logger = logging.getLogger(__name__)


class ConstraintInfo(NamedTuple):
    table: str
    name: str
    statement: str


def fetch_all_tuples(cursor):
    try:
        rows = cursor.fetchall()
        return [ConstraintInfo(row[0], row[1], row[2]) for row in rows]
    except Exception as e:
        raise ValueError("Unable to extract expected row data from cursor") from e


def _is_foreign_key(statement, table):
    return f"REFERENCES {table}(" in statement


def _remap_constraint(
    constraint: ConstraintInfo,
    table_name: str,
    temp_table_name: str,
) -> list[str]:
    """
    Given information about an existing CONSTRAINT involving the original media table,
    produce a list of `ALTER TABLE...` statements to remove the constraint from the
    existing table and apply it to the temp table.

    The constraint to remap may be a constraint directly on the live media table, in
    which case it is dropped and then added directly to the temp table. Alternatively,
    it may be a foreign key constraint on a related table which references the
    live media table, in which case it is dropped from the related table and
    re-added, altered to reference the temp table instead.
    """

    # In all cases, drop the existing constraint
    alterations = [
        queries.DROP_CONSTRAINT_QUERY.format(
            constraint_table=constraint.table, constraint_name=constraint.name
        )
    ]

    # If the constraint was applied directly to the media table, then
    # we now apply it to the temp table instead
    if constraint.table == table_name:
        alterations.append(
            queries.ADD_CONSTRAINT_QUERY.format(
                constraint_name=constraint.name,
                constraint_table=temp_table_name,
                constraint_statement=constraint.statement,
            )
        )

    # If the constraint was a foreign key constraint which referenced the media table,
    # we add it back to its original table, but altered to reference the temp table
    # instead.
    else:
        tokens = constraint.statement.split(" ")

        # Point the constraint to the new table by replacing the referenced table name (always
        # appears after the word `REFERENCES`) with the temp table.
        reference_idx = tokens.index("REFERENCES") + 1
        table_reference = tokens[reference_idx]
        new_reference = table_reference.replace(f"{table_name}(", f"{temp_table_name}(")
        tokens[reference_idx] = new_reference
        new_constraint_statement = " ".join(tokens)

        alterations.append(
            queries.ADD_CONSTRAINT_QUERY.format(
                constraint_table=constraint.table,
                constraint_name=constraint.name,
                constraint_statement=new_constraint_statement,
            )
        )

    return alterations


def _generate_delete_orphans(
    constraint_statement: str, constraint_table: str, temp_table_name: str
):
    """
    Parse a foreign key constraint and generate a `DELETE` statement to
    delete records which would become invalid when the tables are swapped.

    Takes a foreign key constraint statement from an API table, which
    references the media table being replaced. It is possible that some records which
    exist in the current (live) media table may no longer exist in the temp table
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


@task(map_index_template="{{ task.op_kwargs['table_name'] }}")
def generate_constraints_for_table(
    all_constraints: list[ConstraintInfo], table_name: str, temp_table_name: str
):
    """
    Produce `ALTER TABLE...` statements needed to drop constraints from the
    live (old) tables and remap them to the temp tables.
    """
    # `ALTER TABLE...` statements for dropping/applying the new constraints
    remap_constraints = []
    # Statements for dropping records in related tables that reference records
    # that exist in the current (live) media table but not the temp table.
    # These must be dropped before other constraints can be applied.
    drop_orphans = []

    for constraint in all_constraints:
        # Consider all constraints that either apply directly to the given table or
        # which may reference it from another table (foreign key constraints).
        # Ignore PRIMARY KEY statements and UNIQUE statements, which are already
        # enforced via the table indices copied in an earlier task
        is_fk = _is_foreign_key(constraint.statement, table_name)
        if (
            (constraint.table == table_name or is_fk)
            and "PRIMARY KEY" not in constraint.statement
            and "UNIQUE" not in constraint.statement
        ):
            # Generate the `ALTER TABLE...` statements needed to drop this constraint
            # from the live table and apply it to the temp table.
            alter_statements = _remap_constraint(
                constraint,
                table_name,
                temp_table_name,
            )
            remap_constraints.extend(alter_statements)

            # If the constraint was a foreign key constraint, generate statements
            # to ensure no records persist which reference deleted media.
            if is_fk:
                delete_orphans = _generate_delete_orphans(
                    constraint.statement, constraint.table, temp_table_name
                )
                drop_orphans.append(delete_orphans)

    constraint_statements = []
    # Drop orphans first
    constraint_statements.extend(drop_orphans)
    constraint_statements.extend(remap_constraints)

    return constraint_statements


@task(map_index_template="{{ task.op_kwargs['table_name'] }}")
def apply_constraints_to_table(
    postgres_conn_id: str, table_name: str, constraints: list[str]
):
    logger.info(f"Applying constraints for `{table_name}`.")
    for constraint in constraints:
        run_sql.function(postgres_conn_id=postgres_conn_id, sql_template=constraint)


@task_group
def remap_table_constraints_to_table(
    table_name: str, temp_table_name: str, postgres_conn_id: str
):
    all_constraints = run_sql.override(task_id="get_all_existing_constraints")(
        postgres_conn_id=postgres_conn_id,
        sql_template=queries.SELECT_ALL_CONSTRAINTS_QUERY,
        handler=fetch_all_tuples,
        map_index_template=table_name,
    )

    # Generate SQL for remapping constraints from the table to the temp_table
    remapped_constraints = generate_constraints_for_table(
        all_constraints=all_constraints,
        table_name=table_name,
        temp_table_name=temp_table_name,
    )

    apply_constraints_to_table(
        postgres_conn_id=postgres_conn_id,
        table_name=table_name,
        constraints=remapped_constraints,
    )
