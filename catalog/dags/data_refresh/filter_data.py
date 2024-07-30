"""
# Filter Data Task

This module contains the Airflow task used for filtering data from the
newly created temporary table in the downstream (API) database. This
provides an entrypoint for filtering tags that do not meet a certain
minimum accuracy, are malformed, or are from unvetted providers.
"""

import logging
import multiprocessing
import time
import uuid

from airflow.decorators import task
from airflow.models.abstractoperator import AbstractOperator
from psycopg2.extras import DictCursor, Json

from common.constants import POSTGRES_API_CONN_IDS, Environment
from common.sql import PostgresHook
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


def _filter_data_worker(rows: dict, temp_table: str, postgres: PostgresHook) -> int:
    logger.info("Starting data filtering worker")
    worker_conn = postgres.get_conn()
    logger.info("Data filtering worker connected to database")
    write_cur = worker_conn.cursor(cursor_factory=DictCursor)
    logger.info(f"Filtering {len(rows)} rows")

    start_time = time.perf_counter()
    filtered_tags: list[tuple[str, Json]] = []
    for row in rows:
        _id, identifier, tags = row["id"], row["identifier"], row["tags"]
        tags_fragment = generate_tag_update_fragments(tags)
        if not tags_fragment:
            continue
        filtered_tags.append((identifier, tags_fragment))
        logger.debug(
            f"Updated tags for {identifier}\n\t"
            f"from '{tags}' \n\tto '{tags_fragment}'"
        )
        update_query = f"""
        UPDATE {temp_table} SET
        tags = {tags_fragment} WHERE id = {_id}
        """
        logger.debug(f"Executing update query: \n\t{update_query}")
        write_cur.execute(update_query)
    logger.info("Worker committing changes...")
    worker_conn.commit()
    write_cur.close()
    worker_conn.close()
    end_time = time.perf_counter()
    total_time = end_time - start_time
    logger.info(f"Worker finished batch in {total_time}")
    return len(filtered_tags)


@task
def filter_table_data(
    environment: Environment,
    data_refresh_config: DataRefreshConfig,
    task: AbstractOperator = None,
    timeout: float = None,
):
    downstream_conn_id = POSTGRES_API_CONN_IDS.get(environment)
    temp_table = data_refresh_config.table_mappings[0].temp_table_name
    selection_query = f"SELECT id, identifier, tags from {temp_table};"
    postgres = PostgresHook(
        postgres_conn_id=downstream_conn_id,
        default_statement_timeout=(
            timeout if timeout else PostgresHook.get_execution_timeout(task)
        ),
    )
    conn = postgres.get_conn()
    postgres.set_autocommit(conn, True)
    cursor_name = f"{data_refresh_config.media_type}-{uuid.uuid4()}"
    with conn.cursor(
        name=cursor_name, cursor_factory=DictCursor, withhold=True
    ) as iter_cur:
        iter_cur.itersize = DEFAULT_BATCH_SIZE
        iter_cur.execute(selection_query)

        logger.info("Fetching first batch")
        batch = iter_cur.fetchmany(size=DEFAULT_BATCH_SIZE)
        jobs = []
        num_workers = multiprocessing.cpu_count()
        num_filtered = 0

        while batch:
            # Divide updates into jobs for parallel execution.
            batch_start_time = time.perf_counter()
            job_size = int(len(batch) / num_workers)
            last_end = -1
            logger.info("Dividing work")
            for n in range(1, num_workers + 1):
                logger.info(f"Scheduling job {n}")
                start = last_end + 1
                end = job_size * n
                last_end = end
                # Arguments for parallel _filter_data_worker calls
                jobs.append(
                    (
                        batch[start:end],
                        temp_table,
                        postgres,
                    )
                )
            with multiprocessing.Pool(processes=num_workers) as pool:
                logger.info(f"Starting {len(jobs)} filtering jobs")

                for filtered_count in pool.starmap(_filter_data_worker, jobs):
                    num_filtered += filtered_count
                pool.close()
                pool.join()

            batch_end_time = time.perf_counter()
            rate = len(batch) / (batch_end_time - batch_start_time)
            logger.info(
                f"Batch finished, records/s: filter_rate={rate}, "
                f"items filtered: {num_filtered}.\n"
                f"Fetching next batch."
            )
            jobs = []
            batch = iter_cur.fetchmany(size=DEFAULT_BATCH_SIZE)
    conn.commit()
    iter_cur.close()
    conn.close()
