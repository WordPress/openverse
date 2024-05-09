import logging as log
import time
from collections import deque

import elasticsearch
from decouple import config
from elasticsearch import helpers

# from ingestion_server import slack
from indexer_worker.db_helpers import database_connect

# from indexer_worker.distributed_reindex_scheduler import schedule_distributed_index
from indexer_worker.elasticsearch_models import media_type_to_elasticsearch_model


# from indexer_worker.es_helpers import get_stat
# from indexer_worker.es_mapping import index_settings
# from indexer_worker.queries import get_existence_queries
# from indexer_worker.utils.sensitive_terms import get_sensitive_terms


# The number of database records to load in memory at once.
DB_BUFFER_SIZE = config("DB_BUFFER_SIZE", default=100000, cast=int)


def pg_chunk_to_es(pg_chunk, columns, model_name, dest_index):
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
            if dest_index:
                converted["_index"] = dest_index
            documents.append(converted)

    return documents


def _bulk_upload(es, es_batch):
    max_attempts = 4
    attempts = 0
    # Initial time to wait between indexing attempts
    # Grows exponentially
    cooloff = 5
    while True:
        try:
            deque(helpers.parallel_bulk(es, es_batch, chunk_size=400))
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


def replicate(es, model_name, table_name, target_index, query):
    """
    Copy data from the given PostgreSQL table to the given Elasticsearch index.

    :param model_name: the name of the ES models to use to generate the ES docs
    :param table_name: the name of the PostgreSQL table from which to copy data
    :param index_name: the name of the Elasticsearch index to which to upload data
    :param query: the SQL query to use to select rows from the table
    """

    cursor_name = f"{table_name}_indexing_cursor"
    # Enable writing to Postgres so we can create a server-side cursor.
    pg_conn = database_connect()
    total_indexed_so_far = 0
    with pg_conn.cursor(name=cursor_name) as server_cur:
        server_cur.itersize = DB_BUFFER_SIZE
        server_cur.execute(query)
        num_converted_documents = 0
        # Fetch a chunk and push it to Elasticsearch. Repeat until we run
        # out of chunks.
        while True:
            dl_start_time = time.time()
            chunk = server_cur.fetchmany(server_cur.itersize)
            # num_to_index = server_cur.rowcount
            dl_end_time = time.time() - dl_start_time
            dl_rate = len(chunk) / dl_end_time
            if not chunk:
                break
            log.info(
                f"PSQL indexer down: batch_size={len(chunk)}, "
                f"downloaded_per_second={dl_rate}"
            )
            es_batch = pg_chunk_to_es(
                pg_chunk=chunk,
                columns=server_cur.description,
                model_name=model_name,
                dest_index=target_index,
            )
            push_start_time = time.time()
            num_docs = len(es_batch)
            log.info(f"Pushing {num_docs} docs to Elasticsearch.")
            # Bulk upload to Elasticsearch in parallel.
            try:
                _bulk_upload(es, es_batch)
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
            # if self.progress is not None:
            #     self.progress.value = (total_indexed_so_far / num_to_index) * 100
        log.info(
            f"Synchronized {num_converted_documents} from "
            f"table '{table_name}' to Elasticsearch"
        )
    pg_conn.commit()
    pg_conn.close()
