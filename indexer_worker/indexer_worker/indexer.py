import logging as log
import sys
import time

import elasticsearch
from decouple import config
from elasticsearch import helpers

from indexer_worker.db_helpers import database_connect
from indexer_worker.elasticsearch_models import (
    media_type_to_elasticsearch_model,
)
from indexer_worker.es_helpers import elasticsearch_connect
from indexer_worker.queries import get_reindex_query


# The number of database records to load in memory at once.
DB_BUFFER_SIZE = config("DB_BUFFER_SIZE", default=100000, cast=int)

# Bulk statuses that mean the cluster is overloaded or briefly unavailable, so
# the rejected docs are sent again after a backoff.
RETRYABLE_BULK_STATUSES = {429, 502, 503, 504}
# With the default backoff, 10 retries wait about 25 minutes in total.
BULK_MAX_RETRIES = config("BULK_MAX_RETRIES", default=10, cast=int)
BULK_INITIAL_BACKOFF = config("BULK_INITIAL_BACKOFF", default=5, cast=int)  # seconds
BULK_MAX_BACKOFF = config("BULK_MAX_BACKOFF", default=300, cast=int)  # seconds

# Matches the `generic` formatter in `gunicorn.conf.py`.
LOG_FORMAT = "[%(asctime)s - %(name)s - %(lineno)3d][%(levelname)s] %(message)s"


def launch_reindex(
    model_name: str,
    table_name: str,
    target_index: str,
    start_id: int,
    end_id: int,
    progress: float,
    finish_time: int,
    filtered_target_index: str | None = None,
):
    """
    Copy data from the given PostgreSQL table to the given Elasticsearch index.

    Required Arguments:

    model_name:   the name of the ES models to use to generate the ES docs
    table_name:   the name of the PostgreSQL table from which to copy data
    target_index: the name of the Elasticsearch index to which to upload data
    start_id:     the index of the first record to be copied
    end_id:       the index of the last record to be copied
    progress:     tracks the percentage of records that have been copied so far
    finish_time:  the time at which the task finishes

    Optional Arguments:

    filtered_target_index: the name of a second index that also gets every document.
                           The data refresh deletes the sensitive documents from it
                           afterwards to make the filtered index.
    """
    # Python 3.14 starts this process with forkserver instead of fork, so it does
    # not inherit gunicorn's logging configuration. `basicConfig` does nothing
    # if the root logger already has handlers.
    log.basicConfig(level=log.INFO, stream=sys.stdout, format=LOG_FORMAT)
    try:
        reindex(
            model_name,
            table_name,
            target_index,
            start_id,
            end_id,
            progress,
            filtered_target_index,
        )
        finish_time.value = time.time()
    except Exception as err:
        exception_type = f"{err.__class__.__module__}.{err.__class__.__name__}"
        log.error(
            f":x_red: Error in worker while reindexing `{target_index}`"
            f"(`{exception_type}`): \n"
            f"```\n{err}\n```"
        )
        log.error("Indexing error occurred: ", exc_info=True)


def reindex(
    model_name: str,
    table_name: str,
    target_index: str,
    start_id: int,
    end_id: int,
    progress: float,
    filtered_target_index: str | None = None,
):
    # Enable writing to Postgres so we can create a server-side cursor.
    pg_conn = database_connect()
    es_conn = elasticsearch_connect()

    query = get_reindex_query(model_name, table_name, start_id, end_id)

    total_indexed_so_far = 0
    with pg_conn.cursor(name=f"{table_name}_indexing_cursor") as server_cur:
        server_cur.itersize = DB_BUFFER_SIZE
        server_cur.execute(query)

        # Keep track of how many documents have been indexed so far
        num_converted_documents = 0
        # Number of documents we expect to index
        num_to_index = end_id - start_id

        # Repeatedly fetch chunks and push to Elasticsearch until we run
        # out of data.
        while True:
            # Fetch chunk of records
            dl_start_time = time.time()
            chunk = server_cur.fetchmany(server_cur.itersize)

            if not chunk:
                log.info("No data left to process.")
                break

            dl_end_time = time.time() - dl_start_time
            dl_rate = len(chunk) / dl_end_time
            log.info(
                f"PSQL indexer down: batch_size={len(chunk)}, "
                f"downloaded_per_second={dl_rate}"
            )

            # Create a batch of Elasticsearch documents from the fetched
            # records
            es_batch = pg_chunk_to_es(
                pg_chunk=chunk,
                columns=server_cur.description,
                model_name=model_name,
                target_index=target_index,
                filtered_target_index=filtered_target_index,
            )

            # Bulk upload to Elasticsearch in parallel.
            log.info(f"Pushing {len(es_batch)} docs to Elasticsearch.")
            push_start_time = time.time()
            _bulk_upload(es_conn, es_batch)

            upload_time = time.time() - push_start_time
            upload_rate = len(es_batch) / upload_time
            log.info(
                f"Elasticsearch up: batch_size={len(es_batch)},"
                f" uploaded_per_second={upload_rate}"
            )

            num_converted_documents += len(chunk)
            total_indexed_so_far += len(chunk)
            if progress is not None:
                progress.value = (total_indexed_so_far / num_to_index) * 100

        log.info(
            f"Synchronized {num_converted_documents} from "
            f"table '{table_name}' to Elasticsearch"
        )
    pg_conn.commit()
    pg_conn.close()


def pg_chunk_to_es(
    pg_chunk, columns, model_name, target_index, filtered_target_index=None
):
    """
    Convert the given list of psycopg2 results to Elasticsearch documents, with a
    copy of each for `filtered_target_index` if it is given.
    """

    # Map column names to locations in the row tuple
    schema = {col[0]: idx for idx, col in enumerate(columns)}
    model = media_type_to_elasticsearch_model.get(model_name)
    if model is None:
        log.error(f"Table {model_name} is not defined in elasticsearch_models.")
        return []

    documents = []
    for row in pg_chunk:
        if not (row[schema["removed_from_source"]] or row[schema["deleted"]]):
            converted = model.database_row_to_elasticsearch_doc(row, schema)
            converted = converted.to_dict(include_meta=True)
            if target_index:
                converted["_index"] = target_index
            documents.append(converted)
            if filtered_target_index:
                documents.append({**converted, "_index": filtered_target_index})

    return documents


class BulkUploadError(Exception):
    """Documents could not be indexed, so the worker must fail rather than skip them."""


def _bulk_upload(es_conn, es_batch):
    """
    Index ``es_batch``, retrying the documents Elasticsearch rejects while overloaded.

    Only the rejected documents are sent again, with exponential backoff. Any other
    document failure, or a rejection that outlasts every retry, raises
    ``BulkUploadError`` so that no documents are silently left out of the index.
    """
    pending = es_batch
    for attempt in range(BULK_MAX_RETRIES + 1):
        if attempt:
            backoff = min(BULK_MAX_BACKOFF, BULK_INITIAL_BACKOFF * 2 ** (attempt - 1))
            log.warning(
                f"Elasticsearch rejected {len(pending)} docs. Retrying in {backoff}s "
                f"(retry {attempt} of {BULK_MAX_RETRIES})."
            )
            time.sleep(backoff)

        # A doc is written to both the main and the filtered index with the same
        # `_id`. Bulk responses return `_id` as a string.
        pending_by_key = {(doc["_index"], str(doc["_id"])): doc for doc in pending}
        rejected = []
        failed = []
        try:
            for ok, item in helpers.parallel_bulk(
                es_conn,
                pending,
                chunk_size=400,
                raise_on_error=False,
                raise_on_exception=False,
            ):
                if ok:
                    continue
                info = next(iter(item.values()))
                if info.get("status") in RETRYABLE_BULK_STATUSES:
                    rejected.append(pending_by_key[(info["_index"], str(info["_id"]))])
                else:
                    failed.append(
                        {
                            key: info.get(key)
                            for key in ("_index", "_id", "status", "error")
                        }
                    )
        except elasticsearch.TransportError:
            # The connection failed, so it is unknown which docs were indexed.
            # Indexing a doc again is harmless, so retry all of them.
            log.warning("Bulk request to Elasticsearch failed.", exc_info=True)
            rejected = pending

        if failed:
            raise BulkUploadError(
                f"{len(failed)} docs failed to index. First failures: {failed[:5]}"
            )
        if not rejected:
            return
        pending = rejected

    raise BulkUploadError(
        f"Elasticsearch still rejected {len(pending)} docs after "
        f"{BULK_MAX_RETRIES} retries."
    )
