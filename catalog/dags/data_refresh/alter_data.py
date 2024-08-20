"""
# Alter Data Task

This module contains the Airflow tasks used for filtering, transforming, and augmenting
data from the newly created temporary table in the downstream (API) database.
Currently, this provides an entrypoint for filtering tags that do not meet a certain
minimum accuracy, are malformed, or are from unvetted providers.
"""

import logging
from textwrap import dedent

from airflow.decorators import task, task_group
from airflow.models.abstractoperator import AbstractOperator
from airflow.providers.common.sql.hooks.sql import fetch_all_handler, fetch_one_handler
from psycopg2.extras import Json

from common.constants import POSTGRES_API_CONN_IDS, Environment
from common.sql import PGExecuteQueryOperator, PostgresHook
from data_refresh.data_refresh_types import DataRefreshConfig


logger = logging.getLogger(__name__)


DEFAULT_BATCH_SIZE = 100_000
# Filter out tags that exactly match these terms. All terms should be lowercase.
TAG_DENYLIST = {
    "no person",
    "squareformat",
    "uploaded:by=flickrmobile",
    "uploaded:by=instagram",
    "flickriosapp:filter=flamingo",
    "by",
}

# Filter out tags that contain the following terms. All entries should be
# lowercase.
TAG_CONTAINS_DENYLIST = {
    "flickriosapp",
    "uploaded",
    ":",
    "=",
    "cc0",
    "by-nc",
    "by-nd",
    "by-sa",
    "by-nc-nd",
    "by-nc-sa",
    "pdm",
}

# Filter out low-confidence tags, which indicate that the machine-generated tag
# may be inaccurate.
TAG_MIN_CONFIDENCE = 0.90
# Filter out tags that match the following providers (either because they haven't
# been vetted or because they are known to be low-quality).
FILTERED_TAG_PROVIDERS = {"rekognition"}
# Select the data within a given batch
QUERY_SELECTION = dedent("""
    SELECT id, identifier, tags
    FROM {temp_table}
    WHERE id BETWEEN {batch_start} AND {batch_end}
""")
# Update the tags for a given ID
QUERY_UPDATE = dedent("""
    UPDATE {temp_table}
    SET tags = {tags_fragment}
    WHERE id = {_id}
""")
# Get an estimate of total rows based on the min and max auto-assigned ID
QUERY_ROW_ESTIMATE = dedent("""
    SELECT min(id), max(id) FROM {temp_table}
""")


def _tag_denylisted(tag):
    """Check if a tag is banned or contains a banned substring."""

    if tag in TAG_DENYLIST:
        return True
    for denylisted_substring in TAG_CONTAINS_DENYLIST:
        if denylisted_substring in tag:
            return True
    return False


def generate_tag_updates(tags) -> list[dict] | None:
    """Filter denylisted, low-accuracy, and unverified provider tags."""
    update_required = False
    tag_output = []
    if not tags:
        return None
    for tag in tags:
        should_filter = False
        lower_tag = None
        if (
            # Malformed tag
            not ("name" in tag and isinstance(tag["name"], str))
            # Does not meet accuracy criteria
            or ("accuracy" in tag and float(tag["accuracy"]) < TAG_MIN_CONFIDENCE)
            # Provider must be excluded
            or ("provider" in tag and tag["provider"] in FILTERED_TAG_PROVIDERS)
        ):
            should_filter = True
        else:
            lower_tag = tag["name"].lower()
        if should_filter or _tag_denylisted(lower_tag):
            update_required = True
        else:
            tag_output.append(tag)

    if update_required:
        return tag_output
    return None


@task
def get_alter_batches(
    id_bounds: tuple[int, int], batch_size: int | None
) -> list[tuple[int, int]]:
    start, stop = id_bounds
    batch_size = batch_size or DEFAULT_BATCH_SIZE
    return [(x, x + batch_size - 1) for x in range(start, stop, batch_size)]


@task
def alter_data_batch(
    batch: tuple[int, int],
    temp_table: str,
    postgres_conn_id: str,
    task: AbstractOperator = None,
    timeout: float = None,
) -> int:
    logger.info(f"Starting data altering on batch: {batch}")
    batch_start, batch_end = batch
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=(
            timeout if timeout else PostgresHook.get_execution_timeout(task)
        ),
    )
    rows = postgres.run(
        QUERY_SELECTION.format(
            temp_table=temp_table, batch_start=batch_start, batch_end=batch_end
        ),
        handler=fetch_all_handler,
    )
    worker_conn = postgres.get_conn()
    logger.info("Data altering worker connected to database")
    with worker_conn.cursor() as write_cur:
        logger.info(f"Filtering {len(rows)} rows")

        altered_count = 0
        for row in rows:
            _id, identifier, tags = row
            tags_fragment = generate_tag_updates(tags)
            if not tags_fragment:
                continue
            altered_count += 1
            logger.debug(
                f"Updated tags for {identifier}\n\t"
                f"from '{tags}' \n\tto '{tags_fragment}'"
            )
            update_query = QUERY_UPDATE.format(
                temp_table=temp_table, tags_fragment=Json(tags_fragment), _id=_id
            )
            logger.debug(f"Executing update query: \n\t{update_query}")
            write_cur.execute(update_query)
    logger.info("Worker committing changes...")
    worker_conn.commit()
    worker_conn.close()
    return altered_count


@task
def report(counts: list[int]):
    total_count = sum(counts)
    logger.info(f"Filtered tags for a total of {total_count} records")
    return total_count


@task_group(group_id="alter_table_data")
def alter_table_data(
    target_environment: Environment,
    data_refresh_config: DataRefreshConfig,
):
    """Perform data altering across a number of tasks."""
    postgres_conn_id = POSTGRES_API_CONN_IDS.get(target_environment)
    temp_table = data_refresh_config.table_mapping.temp_table_name

    estimated_record_count = PGExecuteQueryOperator(
        task_id="get_estimated_record_count",
        conn_id=postgres_conn_id,
        sql=QUERY_ROW_ESTIMATE.format(temp_table=temp_table),
        handler=fetch_one_handler,
        return_last=True,
    )

    batches = get_alter_batches(
        estimated_record_count.output,
        batch_size="{{ var.value.get('DATA_REFRESH_ALTER_BATCH_SIZE', none) }}",
    )

    alter_data = alter_data_batch.partial(
        temp_table=temp_table, postgres_conn_id=postgres_conn_id
    ).expand(batch=batches)

    report(alter_data)
