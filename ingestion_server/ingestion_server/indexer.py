"""
A utility for indexing data to Elasticsearch.

For each table to sync, find its largest ID in database. Find the corresponding largest
ID in Elasticsearch. If the database ID is greater than the largest corresponding
ID in Elasticsearch, copy the missing records over to Elasticsearch.

Each table is database corresponds to an identically named index in
Elasticsearch. For instance, if database has a table that we would like to
replicate called 'image', the indexer will create an Elasticsearch called
'image' and populate the index with documents. See elasticsearch_models.py to
change the format of Elasticsearch documents.

This can either be run as a module, CLI, or in daemon mode. In daemon mode,
it will actively monitor Postgres for updates and index them automatically. This
is useful for local development environments.
"""

import logging as log
import time
import uuid
from collections import deque
from typing import Any

import elasticsearch
import requests
from decouple import config
from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import connections
from psycopg2.sql import SQL, Identifier, Literal
from requests import RequestException

from ingestion_server import slack
from ingestion_server.db_helpers import database_connect
from ingestion_server.distributed_reindex_scheduler import schedule_distributed_index
from ingestion_server.elasticsearch_models import media_type_to_elasticsearch_model
from ingestion_server.es_helpers import get_stat
from ingestion_server.es_mapping import index_settings
from ingestion_server.queries import get_existence_queries
from ingestion_server.utils.sensitive_terms import get_sensitive_terms


# See https://www.elastic.co/guide/en/elasticsearch/reference/8.8/docs-reindex.html#docs-reindex-throttle
ES_FILTERED_INDEX_THROTTLING_RATE = config(
    "ES_FILTERED_INDEX_THROTTLING_RATE", default=20_000, cast=int
)

# The number of database records to load in memory at once.
DB_BUFFER_SIZE = config("DB_BUFFER_SIZE", default=100000, cast=int)

SYNCER_POLL_INTERVAL = config("SYNCER_POLL_INTERVAL", default=60, cast=int)

# A comma separated list of tables in the database table to replicate to
# Elasticsearch. Ex: image,docs
REP_TABLES = config(
    "COPY_TABLES", default="image", cast=lambda var: [s.strip() for s in var.split(",")]
)


def get_last_item_ids(table):
    """
    Find the last item added to Postgres and return both its sequential ID and UUID.

    :param table: The name of the database table to check.
    :return: A tuple containing a sequential ID and a UUID
    """

    pg_conn = database_connect()
    pg_conn.set_session(readonly=True)
    cur = pg_conn.cursor()
    # Find the last row added to the database table
    query = SQL(
        "SELECT id, identifier " "FROM {table} " "ORDER BY id DESC " "LIMIT 1;"
    ).format(
        table=Identifier(table),
    )
    cur.execute(query)
    last_added_pg_id, last_added_uuid = cur.fetchone()
    cur.close()
    pg_conn.close()
    return last_added_pg_id, last_added_uuid


class TableIndexer:
    def __init__(
        self,
        es_instance: Elasticsearch,
        task_id: str | None = None,
        callback_url: str | None = None,
        # The following arguments should be typed as ``Synchronized | None``.
        # https://github.com/python/typeshed/issues/8799
        progress: Any = None,
        active_workers: Any = None,
        is_bad_request: Any = None,
    ):
        self.es = es_instance
        connections.connections.add_connection("default", self.es)

        self.task_id = task_id
        self.callback_url = callback_url
        self.progress = progress
        self.active_workers = active_workers
        self.is_bad_request = is_bad_request

    # Helpers
    # =======

    @staticmethod
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

    def _bulk_upload(self, es_batch):
        max_attempts = 4
        attempts = 0
        # Initial time to wait between indexing attempts
        # Grows exponentially
        cooloff = 5
        while True:
            try:
                deque(helpers.parallel_bulk(self.es, es_batch, chunk_size=400))
            except elasticsearch.ElasticsearchException:
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

    # Job components
    # ==============

    def replicate(self, model_name: str, table_name: str, index_name: str, query: str):
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
                num_to_index = server_cur.rowcount
                dl_end_time = time.time() - dl_start_time
                dl_rate = len(chunk) / dl_end_time
                if not chunk:
                    break
                log.info(
                    f"PSQL indexer down: batch_size={len(chunk)}, "
                    f"downloaded_per_second={dl_rate}"
                )
                es_batch = self.pg_chunk_to_es(
                    pg_chunk=chunk,
                    columns=server_cur.description,
                    model_name=model_name,
                    dest_index=index_name,
                )
                push_start_time = time.time()
                num_docs = len(es_batch)
                log.info(f"Pushing {num_docs} docs to Elasticsearch.")
                # Bulk upload to Elasticsearch in parallel.
                try:
                    self._bulk_upload(es_batch)
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
                if self.progress is not None:
                    self.progress.value = (total_indexed_so_far / num_to_index) * 100
            log.info(
                f"Synchronized {num_converted_documents} from "
                f"table '{table_name}' to Elasticsearch"
            )
        pg_conn.commit()
        pg_conn.close()

    def refresh(self, index_name: str, change_settings: bool = False):
        """
        Re-enable replicas and refresh the given index.

        :param index_name: the name of the index to replicate and refresh
        :param change_settings: whether to set replication settings
        """

        self.es.indices.refresh(index=index_name)
        if change_settings:
            self.es.indices.put_settings(
                index=index_name,
                body={"index": {"number_of_replicas": 1}},
            )

    def ping_callback(self):
        """Send a request to the callback URL indicating the completion of the task."""

        if not self.callback_url:
            return

        try:
            log.info("Sending callback request")
            res = requests.post(self.callback_url)
            log.info(f"Response: {res.text}")
        except RequestException as err:
            log.error("Failed to send callback!")
            log.error(err)

    # Public API
    # ==========

    def reindex(
        self, model_name: str, table_name: str = None, index_suffix: str = None, **_
    ):
        """
        Copy contents of the database to a new Elasticsearch index.

        :param model_name: the name of the media type
        :param table_name: the name of the DB table, if different from model name
        :param index_suffix: the unique suffix to add to the index name
        """

        if not index_suffix:
            index_suffix = uuid.uuid4().hex
        if not table_name:
            table_name = model_name
        destination_index = f"{model_name}-{index_suffix}"

        log.info(
            f"Creating index {destination_index} for model {model_name} "
            f"from table {table_name}."
        )
        self.es.indices.create(
            index=destination_index,
            body=index_settings(model_name),
        )

        log.info("Running distributed index using indexer workers.")
        self.active_workers.value = int(True)
        schedule_distributed_index(
            database_connect(), model_name, table_name, destination_index, self.task_id
        )

    def update_index(self, model_name: str, index_suffix: str, since_date: str, **_):
        """
        Update index based on changes in the database after the given date.

        :param model_name: the name of the media type
        :param index_suffix: the unique suffix of the index to update
        :param since_date: the date after which to update the records
        """

        destination_index = f"{model_name}-{index_suffix}"

        log.info(f"Updating index {destination_index} with changes since {since_date}.")
        deleted, mature = get_existence_queries(model_name)
        query = SQL(
            "SELECT *, {deleted}, {mature} "
            "FROM {model_name} "
            "WHERE updated_on >= {since_date};"
        ).format(
            deleted=deleted,
            mature=mature,
            model_name=Identifier(model_name),
            since_date=Literal(since_date),
        )
        self.replicate(model_name, model_name, destination_index, query)
        self.refresh(destination_index)
        self.ping_callback()

    def point_alias(self, model_name: str, index_suffix: str, alias: str, **_):
        """
        Map the given index to the given alias. If the alias is in use by another
        index, it will first be unlinked from that index.

        :param model_name: the name of the media type
        :param index_suffix: the suffix of the index for which to assign the alias
        :param alias: the name of the alias to assign to the index
        """

        dest_index = f"{model_name}-{index_suffix}"

        environment = config("ENVIRONMENT", default="local")
        if environment != "local":
            # Cluster status will always be yellow in development environments
            # because there will only be one node available. In production, there
            # are many nodes, and the index should not be promoted until all
            # shards have been initialized.
            log.info("Waiting for replica shards. . .")
            self.es.cluster.health(
                index=dest_index,
                wait_for_status="green",
                timeout="12h",
            )

        alias_stat = get_stat(self.es, alias)
        curr_index = alias_stat.alt_names
        if alias_stat.exists:
            if not alias_stat.is_alias:
                # Alias is an index, this is fatal.
                message = f"There is an index named `{alias}`, cannot proceed."
                slack.error(message)
                return
            elif alias_stat.is_alias and curr_index != dest_index:
                # Alias is in use, atomically remap it to the new index.
                self.es.indices.update_aliases(
                    body={
                        "actions": [
                            # unlink alias from the old index
                            {"remove": {"index": curr_index, "alias": alias}},
                            # link alias to the new index
                            {"add": {"index": dest_index, "alias": alias}},
                        ]
                    }
                )
                message = (
                    f"Migrated alias `{alias}` from index `{curr_index}` to "
                    f"index `{dest_index}` | _Next: delete old index_"
                )
                slack.status(model_name, message)
            else:
                # Alias is already mapped.
                log.info(
                    f"`{model_name}`: Alias `{alias}` already points to "
                    f"index `{dest_index}`."
                )
        else:
            # Alias does not exist, create it.
            self.es.indices.put_alias(index=dest_index, name=alias)
            message = f"Created alias `{alias}` pointing to index `{dest_index}`."
            slack.status(model_name, message)

        if self.progress is not None:
            self.progress.value = 100  # mark job as completed
        self.ping_callback()

    def delete_index(
        self,
        model_name: str,
        index_suffix: str | None = None,
        alias: str | None = None,
        force_delete: bool = False,
        **_,
    ):
        """
        Delete the given index ensuring that it is not in use.

        :param model_name: the name of the media type
        :param index_suffix: the suffix of the index to delete
        :param alias: the alias to delete, including the index it points to
        :param force_delete: whether to delete the index even if it is in use
        """

        target = alias if alias is not None else f"{model_name}-{index_suffix}"

        target_stat = get_stat(self.es, target)
        if target_stat.exists:
            if target_stat.is_alias:
                if not force_delete:
                    # Alias cannot be deleted unless forced.
                    if self.is_bad_request is not None:
                        self.is_bad_request.value = 1
                    message = (
                        f"Alias `{target}` might be in use so it cannot be deleted. "
                        f"Verify that the API does not use this alias and then use the "
                        f"`force_delete` parameter."
                    )
                    slack.error(message)
                    return
                target = target_stat.alt_names
            else:
                if target_stat.alt_names:
                    # Index mapped to alias cannot be deleted.
                    if self.is_bad_request is not None:
                        self.is_bad_request.value = 1
                    message = (
                        f"Index `{target}` is associated with aliases "
                        f"{target_stat.alt_names}, cannot delete. Delete aliases first."
                    )
                    slack.error(message)
                    return

            self.es.indices.delete(index=target)
            message = f"Index `{target}` was deleted"
            slack.status(model_name, message)
        else:
            # Cannot delete as target does not exist.
            if self.is_bad_request is not None:
                self.is_bad_request.value = 1
            message = f"Target `{target}` does not exist and cannot be deleted."
            slack.status(model_name, message)

        if self.progress is not None:
            self.progress.value = 100
        self.ping_callback()

    def create_and_populate_filtered_index(
        self,
        model_name: str,
        origin_index_suffix: str | None = None,
        destination_index_suffix: str | None = None,
        **_,
    ):
        """
        Create and populate a filtered index without documents with sensitive terms.

        :param model_name: The model/media type the filtered index is for.
        :param origin_index_suffix: The suffix of the origin index on which the
        filtered index should be based. If not supplied, the filtered index will be
        based upon the index aliased to ``model_name`` at the time of execution.
        :param destination_index_suffix: The suffix to use for the destination index.
        This can be configured independently of the origin index suffix to allow for
        multiple filtered index creations to occur against the same origin index, i.e.,
        in the case where sensitive terms change before a data refresh creates a new
        origin index and we wish to update the filtered index immediately. If not
        supplied, a UUID based suffix will be generated. This does not affect the
        final alias used.
        """
        # Allow relying on the model-name-based alias by
        # not supplying `origin_index_suffix`
        source_index = (
            f"{model_name}-{origin_index_suffix}" if origin_index_suffix else model_name
        )

        # Destination and origin index suffixes must be possible to separate
        # to allow for re-runs of filtered index creation based on the same
        # origin index.
        destination_index_suffix = destination_index_suffix or uuid.uuid4().hex
        destination_index = f"{model_name}-{destination_index_suffix}-filtered"

        self.es.indices.create(
            index=destination_index,
            body=index_settings(model_name),
        )

        sensitive_terms = get_sensitive_terms()

        self.es.reindex(
            body={
                "source": {
                    "index": source_index,
                    "query": {
                        "bool": {
                            "must_not": [
                                # Use `terms` query for exact matching against
                                # unanalyzed raw fields
                                {"terms": {f"{field}.raw": sensitive_terms}}
                                for field in ["tags.name", "title", "description"]
                            ]
                        }
                    },
                },
                "dest": {"index": destination_index},
            },
            slices="auto",
            wait_for_completion=True,
            requests_per_second=ES_FILTERED_INDEX_THROTTLING_RATE,
            # Temporary workaround to allow the action to complete.
            request_timeout=48 * 3600,
        )

        self.refresh(index_name=destination_index, change_settings=True)

        if self.progress is not None:
            self.progress.value = 100  # mark job as completed
        self.ping_callback()
