"""
# Filter Data Task

This module contains the Airflow task used for filtering data from the
newly created temporary table in the downstream (API) database. This
provides an entrypoint for filtering tags that do not meet a certain
minimum accuracy, are malformed, or are from unvetted providers.
"""

import logging
from textwrap import dedent

from airflow.decorators import task, task_group
from airflow.models import Variable
from airflow.models.abstractoperator import AbstractOperator
from airflow.providers.common.sql.hooks.sql import fetch_all_handler, fetch_one_handler
from psycopg2.extras import DictCursor, Json

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

# Filter out tags that contain the following terms. All entrees should be
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
QUERY_SELECTION = dedent("""
    SELECT id, identifier, tags
    FROM {temp_table}
    WHERE id BETWEEN {batch_start} AND {batch_end}
""")
QUERY_UPDATE = dedent("""
    UPDATE {temp_table}
    SET tags = {tags_fragment}
    WHERE id = {_id}
""")
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


def generate_tag_update_fragments(tags):
    """
    Filter denylisted, low-accuracy, and unverified provider tags.

    :return: an SQL fragment if an update is needed, ``None`` otherwise
    """

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
        fragment = Json(tag_output)
        logger.debug(f"Tags fragment: {fragment}")
        return fragment
    else:
        return None


@task
def get_filter_batches(id_bounds: tuple[int, int]):
    start, stop = id_bounds
    batch_size = Variable.get(
        "DATA_REFRESH_FILTER_BATCH_SIZE",
        deserialize_json=True,
        default_var=DEFAULT_BATCH_SIZE,
    )
    return [(x, x + batch_size - 1) for x in range(start, stop, batch_size)]


@task
def filter_data_batch(
    batch: tuple[int, int],
    temp_table: str,
    postgres_conn_id: str,
    task: AbstractOperator = None,
    timeout: float = None,
) -> int:
    logger.info(f"Starting data filtering on batch: {batch}")
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
    logger.info("Data filtering worker connected to database")
    write_cur = worker_conn.cursor(cursor_factory=DictCursor)
    logger.info(f"Filtering {len(rows)} rows")

    filtered_tags: list[tuple[str, Json]] = []
    for row in rows:
        _id, identifier, tags = row
        tags_fragment = generate_tag_update_fragments(tags)
        if not tags_fragment:
            continue
        filtered_tags.append((identifier, tags_fragment))
        logger.debug(
            f"Updated tags for {identifier}\n\t"
            f"from '{tags}' \n\tto '{tags_fragment}'"
        )
        update_query = QUERY_UPDATE.format(
            temp_table=temp_table, tags_fragment=tags_fragment, _id=_id
        )
        logger.debug(f"Executing update query: \n\t{update_query}")
        write_cur.execute(update_query)
    logger.info("Worker committing changes...")
    worker_conn.commit()
    write_cur.close()
    worker_conn.close()
    return len(filtered_tags)


@task
def report(counts: list[int]):
    total_count = sum(counts)
    logger.info(f"Filtered tags for a total of {total_count} records")


@task_group(group_id="filter_table_data")
def filter_table_data(
    environment: Environment,
    data_refresh_config: DataRefreshConfig,
):
    """Perform data filtering across a number of tasks."""
    postgres_conn_id = POSTGRES_API_CONN_IDS.get(environment)
    temp_table = data_refresh_config.table_mappings[0].temp_table_name

    estimated_record_count = PGExecuteQueryOperator(
        task_id="get_estimated_record_count",
        conn_id=postgres_conn_id,
        sql=QUERY_ROW_ESTIMATE.format(temp_table=temp_table),
        handler=fetch_one_handler,
        return_last=True,
    )

    batches = get_filter_batches(estimated_record_count.output)

    filter_data = filter_data_batch.partial(
        temp_table=temp_table, postgres_conn_id=postgres_conn_id
    ).expand(batch=batches)

    report(filter_data)
