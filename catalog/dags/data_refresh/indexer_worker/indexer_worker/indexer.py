import logging as log
import time
from collections import deque

import elasticsearch
from decouple import config
from elasticsearch import helpers
from indexer_worker.db_helpers import database_connect
from indexer_worker.elasticsearch_models import media_type_to_elasticsearch_model
from indexer_worker.es_helpers import elasticsearch_connect
from indexer_worker.queries import get_reindex_query


# The number of database records to load in memory at once.
DB_BUFFER_SIZE = config("DB_BUFFER_SIZE", default=100000, cast=int)


def launch_reindex(
    model_name: str,
    table_name: str,
    target_index: str,
    start_id: int,
    end_id: int,
    progress: float,
    finish_time: int,
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
    """
    try:
        reindex(model_name, table_name, target_index, start_id, end_id, progress)
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
            )

            # Bulk upload to Elasticsearch in parallel.
            log.info(f"Pushing {len(es_batch)} docs to Elasticsearch.")
            push_start_time = time.time()
            try:
                _bulk_upload(es_conn, es_batch)
            except ValueError:
                log.error("Failed to index chunk.")

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


def pg_chunk_to_es(pg_chunk, columns, model_name, target_index):
    """Convert the given list of psycopg2 results to Elasticsearch documents."""

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

    return documents


def _bulk_upload(es_conn, es_batch):
    max_attempts = 4
    attempts = 0
    # Initial time to wait between indexing attempts
    # Grows exponentially
    cooloff = 5
    while True:
        try:
            deque(helpers.parallel_bulk(es_conn, es_batch, chunk_size=400))
        except elasticsearch.ApiError:
            # Something went wrong during indexing.
            log.warning(
                f"Elasticsearch rejected bulk query. We will retry in"
                f" {cooloff}s. Attempt {attempts}. Details: ",
                exc_info=True,
            )
            time.sleep(cooloff)
            cooloff *= 2
            if attempts >= max_attempts:
                raise ValueError("Exceeded maximum bulk index retries")
            attempts += 1
            continue
        break
