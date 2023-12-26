"""
Pull the latest copy of a table from the upstream catalog database.

Since some of these tables have hundreds of millions of records and are tens of
gigabytes in size, there are some performance considerations we need to account
for. Appending or updating large numbers of records has poor performance due to
the number of indices and constraints on the table. These indices and
constraints are necessary for good query performance and data consistency,
so we can't get rid of them. Since the data is being actively queried in
production, disabling indices and constraints temporarily isn't an option.

To work around these problems, we need to create a temporary table, import the
data, and only then create indices and constraints. Then, "promote" the new
table to replace the old data. This strategy is far faster than updating the
data in place.
"""

import logging as log
import multiprocessing

import psycopg2
from decouple import config
from psycopg2.extras import DictCursor
from psycopg2.sql import SQL, Identifier, Literal

from ingestion_server import slack
from ingestion_server.cleanup import clean_image_data
from ingestion_server.constants.internal_types import ApproachType
from ingestion_server.db_helpers import database_connect, DB_UPSTREAM_CONFIG
from ingestion_server.queries import (
    get_copy_data_query,
    get_create_ext_query,
    get_fdw_query,
    get_go_live_query,
)
from ingestion_server.utils.config import get_record_limit


RELATIVE_UPSTREAM_DB_HOST = config(
    "RELATIVE_UPSTREAM_DB_HOST",
    default=DB_UPSTREAM_CONFIG.host,
)
#: the hostname of the upstream DB from the POV of the downstream DB

RELATIVE_UPSTREAM_DB_PORT = config(
    "RELATIVE_UPSTREAM_DB_PORT",
    default=DB_UPSTREAM_CONFIG.port,
    cast=int,
)
#: the port of the upstream DB from the POV of the downstream DB


def _get_shared_cols(downstream, upstream, upstream_table: str, downstream_table: str):
    """
    Get the common columns between two tables with the same name in different DBs.

    Given two database connections and a table name, return the list of columns
    that the two tables have in common.

    :param downstream: an open connection to the downstream PostgreSQL database
    :param upstream: an open connection to the upstream PostgreSQL database
    :param upstream_table: the name of the table in the upstream db
    :param downstream_table: the name of the table in the downstream db
    :return: a list of the column names that are common to both databases
    """
    with downstream.cursor() as cur1, upstream.cursor() as cur2:
        get_tables = SQL("SELECT * FROM {table} LIMIT 0;")
        cur1.execute(get_tables.format(table=Identifier(downstream_table)))
        conn1_cols = {desc[0] for desc in cur1.description}
        cur2.execute(get_tables.format(table=Identifier(upstream_table)))
        conn2_cols = {desc[0] for desc in cur2.description}

    shared = list(conn1_cols.intersection(conn2_cols))
    log.info(f"Shared columns: {shared}")
    return shared


def _generate_indices(conn, table: str) -> tuple[list[str], dict[str, str]]:
    """
    Apply the existing table indices to the new temp table imported from upstream.

    :return: a list of ``CREATE INDEX`` SQL statements
    """

    index_mapping = {}

    def _clean_idxs(indices: list[str]):
        # Remove names of indices. We don't want to collide with the old names;
        # we want the database to generate them for us upon recreating the
        # table.
        cleaned = []
        for index in indices:
            # The index name is always after CREATE [UNIQUE] INDEX; delete it.
            tokens = index.split(" ")
            index_idx = tokens.index("INDEX")
            is_pk = "(id)" in index
            # Record what the old index was
            old_index = tokens[index_idx + 1]
            # Primary keys during data refresh are based on the table name and may
            # not be exactly correlated with what the primary keys are actually named
            new_index = (
                f"temp_import_{old_index}" if not is_pk else f"temp_import_{table}_pkey"
            )
            index_mapping[new_index] = old_index
            # Update name
            tokens[index_idx + 1] = new_index
            # The table name is always after ON. Rename it to match the
            # temporary copy of the data.
            on_idx = tokens.index("ON")
            table_name_idx = on_idx + 1
            schema_name, table_name = tokens[table_name_idx].split(".")
            tokens[table_name_idx] = f"{schema_name}.temp_import_{table_name}"
            # Skip the primary key, it already exists
            if not is_pk:
                cleaned.append(" ".join(tokens))

        return cleaned, index_mapping

    # Get all of the old indices from the existing table.
    with conn.cursor() as cur:
        get_idxs = SQL(
            "SELECT indexdef FROM pg_indexes WHERE tablename = {table};"
        ).format(table=Literal(table))
        cur.execute(get_idxs)
        idxs = cur.fetchall()
    cleaned_idxs = _clean_idxs([idx[0] for idx in idxs])
    return cleaned_idxs


def _is_foreign_key(_statement, table):
    return f"REFERENCES {table}(" in _statement


def _remap_constraint(name, con_table, fk_statement, table) -> list[SQL]:
    """Produce ALTER TABLE ... statements for each constraint."""

    alterations = [
        SQL("ALTER TABLE {con_table} DROP CONSTRAINT {name}").format(
            con_table=Identifier(con_table), name=Identifier(name)
        )
    ]
    # Constraint applies to the table we're replacing
    if con_table == table:
        alterations.append(
            SQL("ALTER TABLE {con_table} ADD {fk_statement}").format(
                con_table=Identifier(con_table),
                fk_statement=SQL(fk_statement),
            )
        )
    # Constraint references the table we're replacing. Point it at the new
    # one.
    else:
        tokens = fk_statement.split(" ")
        # Point the constraint to the new table.
        reference_idx = tokens.index("REFERENCES") + 1
        table_reference = tokens[reference_idx]
        match_old_ref = f"{table}("
        new_ref = f"temp_import_{table}("
        new_reference = table_reference.replace(match_old_ref, new_ref)
        tokens[reference_idx] = new_reference
        con_definition = " ".join(tokens)
        create_constraint = SQL("ALTER TABLE {con_table} ADD {con_definition}").format(
            con_table=Identifier(con_table), con_definition=SQL(con_definition)
        )
        alterations.append(create_constraint)
    return alterations


def _generate_delete_orphans(fk_statement, fk_table):
    """
    Parse the foreign key statement and generate the deletion statement.

    Sometimes, upstream data is deleted. If there are foreign key
    references to deleted data, we must delete them before adding
    constraints back to the table.
    """

    fk_tokens = fk_statement.split(" ")
    fk_field_idx = fk_tokens.index("KEY") + 1
    fk_ref_idx = fk_tokens.index("REFERENCES") + 1
    fk_field = fk_tokens[fk_field_idx].replace("(", "").replace(")", "")
    fk_reference = fk_tokens[fk_ref_idx]
    ref_table, ref_field = fk_reference.split("(")
    ref_field = ref_field.replace(")", "")

    del_orphans = SQL(
        "DELETE FROM {fk_table} AS fk_table "
        "WHERE NOT EXISTS(SELECT 1 FROM {ref_table} AS r "
        "WHERE {ref_field} = {fk_field});"
    ).format(
        fk_table=Identifier(fk_table),
        ref_table=Identifier(f"temp_import_{ref_table}"),
        ref_field=Identifier("r", ref_field),
        fk_field=Identifier("fk_table", fk_field),
    )
    return del_orphans


def _generate_constraints(conn, table: str) -> list[SQL]:
    """
    Apply the existing table constraints to the new temp table imported from upstream.

    :return: a list of ``ALTER TABLE ADD CONSTRAINT`` SQL statements
    """

    # List all active constraints across the database.
    get_all_constraints = SQL(
        """
        SELECT conrelid::regclass AS table, conname, pg_get_constraintdef(c.oid)
        FROM pg_constraint AS c
        JOIN pg_namespace AS n
        ON n.oid = c.connamespace
        AND n.nspname = 'public'
        ORDER BY conrelid::regclass::text, contype DESC;
    """
    )
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(get_all_constraints)
        all_constraints = cur.fetchall()
    # Find all constraints that either exist inside of the table or
    # reference it from another table. Ignore PRIMARY KEY statements.
    remap_constraints = []
    drop_orphans = []
    for constraint in all_constraints:
        statement = constraint["pg_get_constraintdef"]
        con_table = constraint["table"]
        is_fk = _is_foreign_key(statement, table)
        if (con_table == table or is_fk) and "PRIMARY KEY" not in statement:
            alter_stmnts = _remap_constraint(
                constraint["conname"], con_table, statement, table
            )
            remap_constraints.extend(alter_stmnts)
            if is_fk:
                del_orphans = _generate_delete_orphans(statement, con_table)
                drop_orphans.append(del_orphans)

    constraint_statements = []
    constraint_statements.extend(drop_orphans)
    constraint_statements.extend(remap_constraints)
    return constraint_statements


def _update_progress(progress, new_value):
    if progress:
        progress.value = new_value


def refresh_api_table(
    upstream_table: str,
    downstream_table: str,
    progress: multiprocessing.Value = None,
    approach: ApproachType = "advanced",
):
    """
    Import updates from the upstream catalog database into the API.

    The process involves the following steps.

    1. Get the list of overlapping columns: ``_get_shared_cols``
    2. Create the FDW extension if it does not exist
    3. Create FDW for the data transfer: ``get_fdw_query``
    4. Import data into a temporary table: ``get_copy_data_query``
    5. Clean the data: ``clean_image_data``

    This is the main function of this module.

    :param upstream_table: The upstream table to copy.
    :param downstream_table: The name of the copied table in the downstream db.
    :param progress: multiprocessing.Value float for sharing task progress
    :param approach: whether to use advanced logic specific to media ingestion
    """

    # Step 1: Get the list of overlapping columns
    slack.status(
        upstream_table,
        "Starting ingestion server data refresh | _Next: copying data from upstream_",
    )
    downstream_db = database_connect()
    upstream_db = database_connect(dbconfig=DB_UPSTREAM_CONFIG)
    shared_cols = _get_shared_cols(
        downstream_db, upstream_db, upstream_table, downstream_table
    )
    upstream_db.close()

    with downstream_db, downstream_db.cursor() as downstream_cur:
        # Step 2: Create the FDW extension if it does not exist
        log.info("(Re)initializing foreign data wrapper")
        try:
            create_ext = get_create_ext_query()
            downstream_cur.execute(create_ext)
        except psycopg2.errors.UniqueViolation:
            log.warning("Extension already exists, possible race condition.")

    with downstream_db, downstream_db.cursor() as downstream_cur:
        # Step 3: Create FDW for the data transfer
        init_fdw = get_fdw_query(
            RELATIVE_UPSTREAM_DB_HOST,
            RELATIVE_UPSTREAM_DB_PORT,
            DB_UPSTREAM_CONFIG.dbname,
            DB_UPSTREAM_CONFIG.user,
            DB_UPSTREAM_CONFIG.password,
            upstream_table,
        )
        downstream_cur.execute(init_fdw)

        # Step 4: Import data into a temporary table
        log.info("Copying upstream data...")
        limit = get_record_limit()
        copy_data = get_copy_data_query(
            upstream_table,
            downstream_table,
            shared_cols,
            approach=approach,
            limit=limit,
        )
        log.info(f"Running copy-data query: \n{copy_data.as_string(downstream_cur)}")
        downstream_cur.execute(copy_data)

    next_step = (
        "image data cleaning"
        if downstream_table == "image"
        else "Elasticsearch reindex"
    )
    slack.status(upstream_table, f"Data copy complete | _Next: {next_step}_")

    if downstream_table == "image":
        # Step 5: Clean the data
        log.info("Cleaning data...")
        clean_image_data(downstream_table)
        log.info("Cleaning completed!")
        slack.status(
            downstream_table, "Data cleaning complete | _Next: Elasticsearch reindex_"
        )

    downstream_db.close()
    log.info(f"Finished refreshing table '{downstream_table}'.")
    _update_progress(progress, 100.0)


def promote_api_table(
    table: str,
    progress: multiprocessing.Value = None,
):
    """
    Promote the temporary table in the API database to the main one.

    This runs after ``refresh_api_table``. The process involves the following steps.

    6. Recreate indices from the original table: ``_generate_indices``
    7. Recreate constraints from the original table: ``_generate_constraints``
    8. Promote the temp table and delete the original: ``get_go_live_query``

    :param table: the upstream table to copy
    :param progress: multiprocessing.Value float for sharing task progress
    """

    log.info(f"`{table}`: Starting table promotion | _Next: recreate-indices_")
    downstream_db = database_connect()

    with downstream_db, downstream_db.cursor() as downstream_cur:
        # Step 6: Recreate indices from the original table
        log.info("Recreating database indices...")
        create_indices, index_mapping = _generate_indices(downstream_db, table)
        _update_progress(progress, 50.0)
        if create_indices != "":
            for create_index in create_indices:
                log.info(f"Running: {create_index}")
                downstream_cur.execute(create_index)
        log.info("Done creating indices! Remapping constraints...")
        _update_progress(progress, 70.0)

        # Step 7: Recreate constraints from the original table
        remap_constraints = _generate_constraints(downstream_db, table)
        if len(remap_constraints):
            for remap_constraint in remap_constraints:
                log.info(f"Running: {remap_constraint.as_string(downstream_cur)}")
                downstream_cur.execute(remap_constraint)
        log.info("Done remapping constraints! Going live with new table...")
        _update_progress(progress, 99.0)
        slack.status(table, "Indices & constraints applied | _Next: table promotion_")

        # Step 8: Promote the temporary table and delete the original
        go_live = get_go_live_query(table, index_mapping)
        log.info(f"Running go-live: \n{go_live.as_string(downstream_cur)}")
        downstream_cur.execute(go_live)
        slack.status(
            table, "Finished table promotion | _Next: Elasticsearch promotion_"
        )

    downstream_db.close()
    log.info(f"Finished promoting table {table}")
    _update_progress(progress, 100.0)
