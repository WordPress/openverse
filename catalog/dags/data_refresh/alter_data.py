"""
# Alter Data Task

This module contains the Airflow tasks used for filtering, transforming, and augmenting
data from the newly created temporary table in the downstream (API) database.
Currently, this provides an entrypoint for filtering tags that do not meet a certain
minimum accuracy, are malformed, or are from unvetted providers.

The filtering runs as one `UPDATE` per batch of ids inside the API database, so no
rows are loaded into the Airflow worker.
"""

import logging
from textwrap import dedent

from airflow.decorators import task, task_group
from airflow.models.abstractoperator import AbstractOperator
from airflow.providers.common.sql.hooks.handlers import fetch_one_handler

from common.constants import POSTGRES_API_CONN_IDS, Environment
from common.sql import RETURN_ROW_COUNT, PGExecuteQueryOperator, PostgresHook
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

# True when a tag is malformed, below the confidence threshold, from a filtered
# provider, or has a denylisted name. Every branch must be non-null, because
# `NOT NULL` would drop a tag that should be kept.
TAG_IS_FILTERED = """(
    jsonb_typeof(tag -> 'name') IS DISTINCT FROM 'string'
    OR CASE
        WHEN jsonb_typeof(tag -> 'accuracy') IN ('number', 'string')
            THEN (tag ->> 'accuracy')::numeric < %(min_confidence)s
        ELSE false
    END
    OR coalesce(tag ->> 'provider' = ANY(%(filtered_providers)s), false)
    OR lower(tag ->> 'name') = ANY(%(denylist)s)
    OR lower(tag ->> 'name') LIKE ANY(%(contains_denylist)s)
)"""
TAG_ELEMENTS = """jsonb_array_elements(
    CASE jsonb_typeof(tags) WHEN 'array' THEN tags ELSE '[]'::jsonb END
) WITH ORDINALITY AS elements(tag, position)"""
# Rewrite the tags of each record in the batch that has at least one tag to drop,
# keeping the order of the remaining tags.
QUERY_FILTER_TAGS = dedent(f"""
    UPDATE {{temp_table}}
    SET tags = (
        SELECT coalesce(jsonb_agg(tag ORDER BY position), '[]'::jsonb)
        FROM {TAG_ELEMENTS}
        WHERE NOT {TAG_IS_FILTERED}
    )
    WHERE id BETWEEN %(batch_start)s AND %(batch_end)s
        AND EXISTS (SELECT FROM {TAG_ELEMENTS} WHERE {TAG_IS_FILTERED})
""")
# Get an estimate of total rows based on the min and max auto-assigned ID
QUERY_ROW_ESTIMATE = dedent("""
    SELECT min(id), max(id) FROM {temp_table}
""")


def _like_contains_pattern(term: str) -> str:
    escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def get_tag_filter_parameters() -> dict:
    return {
        "min_confidence": TAG_MIN_CONFIDENCE,
        "filtered_providers": sorted(FILTERED_TAG_PROVIDERS),
        "denylist": sorted(TAG_DENYLIST),
        "contains_denylist": sorted(
            _like_contains_pattern(term) for term in TAG_CONTAINS_DENYLIST
        ),
    }


@task
def get_alter_batches(
    id_bounds: tuple[int, int], batch_size: int | None
) -> list[tuple[int, int]]:
    start, stop = id_bounds
    batch_size = batch_size or DEFAULT_BATCH_SIZE
    return [(x, x + batch_size - 1) for x in range(start, stop + 1, batch_size)]


@task(max_active_tis_per_dagrun=2)
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
    altered_count = postgres.run(
        QUERY_FILTER_TAGS.format(temp_table=temp_table),
        parameters={
            "batch_start": batch_start,
            "batch_end": batch_end,
            **get_tag_filter_parameters(),
        },
        handler=RETURN_ROW_COUNT,
    )
    logger.info(f"Filtered tags for {altered_count} records in batch {batch}")
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
        batch_size=data_refresh_config.alter_data_batch_size,
    )

    alter_data = alter_data_batch.partial(
        temp_table=temp_table,
        postgres_conn_id=postgres_conn_id,
    ).expand(batch=batches)

    report(alter_data)
