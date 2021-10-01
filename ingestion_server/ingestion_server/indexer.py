import argparse
import datetime
import logging as log
import os
import sys
import time
import uuid
from collections import deque

import elasticsearch
import psycopg2
from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch, NotFoundError, RequestsHttpConnection, helpers
from elasticsearch.exceptions import ConnectionError as ESConnectionError
from elasticsearch_dsl import Search, connections
from ingestion_server.distributed_reindex_scheduler import schedule_distributed_index
from ingestion_server.elasticsearch_models import database_table_to_elasticsearch_model
from ingestion_server.es_mapping import index_settings
from ingestion_server.qa import create_search_qa_index
from ingestion_server.queries import get_existence_queries
from psycopg2.sql import SQL, Identifier, Literal


"""
A utility for indexing data to Elasticsearch. For each table to
sync, find its largest ID in database. Find the corresponding largest ID in
Elasticsearch. If the database ID is greater than the largest corresponding
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

# For AWS IAM access to Elasticsearch
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL", "localhost")
ELASTICSEARCH_PORT = int(os.environ.get("ELASTICSEARCH_PORT", 9200))
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

DATABASE_HOST = os.environ.get("DATABASE_HOST", "localhost")
DATABASE_USER = os.environ.get("DATABASE_USER", "deploy")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", "deploy")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "openledger")
DATABASE_PORT = int(os.environ.get("DATABASE_PORT", 5432))

# The number of database records to load in memory at once.
DB_BUFFER_SIZE = int(os.environ.get("DB_BUFFER_SIZE", 100000))

SYNCER_POLL_INTERVAL = int(os.environ.get("SYNCER_POLL_INTERVAL", 60))

# A comma separated list of tables in the database table to replicate to
# Elasticsearch. Ex: image,docs
REP_TABLES = os.environ.get("COPY_TABLES", "image")
replicate_tables = REP_TABLES.split(",") if "," in REP_TABLES else [REP_TABLES]

TWELVE_HOURS_SEC = 60 * 60 * 12


def elasticsearch_connect(timeout=300):
    """
    Repeatedly try to connect to Elasticsearch until successful.
    :return: An Elasticsearch connection object.
    """
    while True:
        try:
            return _elasticsearch_connect()
        except ESConnectionError as e:
            log.exception(e)
            log.error("Reconnecting to Elasticsearch in 5 seconds. . .")
            time.sleep(5)
            continue


def _elasticsearch_connect():
    """
    Connect to configured Elasticsearch domain.

    :param timeout: How long to wait before ANY request to Elasticsearch times
    out. Because we use parallel bulk uploads (which sometimes wait long periods
    of time before beginning execution), a value of at least 30 seconds is
    recommended.
    :return: An Elasticsearch connection object.
    """

    log.info("Connecting to %s %s with AWS auth", ELASTICSEARCH_URL, ELASTICSEARCH_PORT)
    auth = AWSRequestsAuth(
        aws_access_key=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_host=ELASTICSEARCH_URL,
        aws_region=AWS_REGION,
        aws_service="es",
    )
    auth.encode = lambda x: bytes(x.encode("utf-8"))
    es = Elasticsearch(
        host=ELASTICSEARCH_URL,
        port=ELASTICSEARCH_PORT,
        connection_class=RequestsHttpConnection,
        http_auth=auth,
        timeout=TWELVE_HOURS_SEC,
    )
    es.info()
    return es


def database_connect(autocommit=False):
    """
    Repeatedly try to connect to the downstream (API) database until successful.
    :return: A database connection object
    """
    while True:
        try:
            conn = psycopg2.connect(
                dbname=DATABASE_NAME,
                user=DATABASE_USER,
                password=DATABASE_PASSWORD,
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                connect_timeout=5,
            )
            if autocommit:
                conn.set_session(autocommit=True)
        except psycopg2.OperationalError as e:
            log.exception(e)
            log.error("Reconnecting to database in 5 seconds. . .")
            time.sleep(5)
            continue
        break

    return conn


def get_last_item_ids(table):
    """
    Find the last item added to Postgres and return both its sequential ID
    and its UUID.
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
    def __init__(self, es_instance, tables, progress=None, finish_time=None):
        self.es = es_instance
        connections.connections.add_connection("default", self.es)
        self.tables_to_watch = tables
        # Optional multiprocessing.Values for examining indexing progress
        self.progress = progress
        self.finish_time = finish_time

    def _index_table(self, table, dest_idx=None):
        """
        Check that the database tables are in sync with Elasticsearch. If not,
        begin replication.
        """
        last_pg_id, _ = get_last_item_ids(table)
        if not last_pg_id:
            log.warning(f"Tried to sync {table} but it was empty.")
            return
        # Find the last document inserted into elasticsearch
        destination = dest_idx if dest_idx else table
        s = Search(using=self.es, index=destination)
        s.aggs.bucket("highest_pg_id", "max", field="id")
        try:
            es_res = s.execute()
            last_es_id = int(es_res.aggregations["highest_pg_id"]["value"])
        except (TypeError, NotFoundError):
            log.info(
                "No matching documents found in elasticsearch. "
                "Replicating everything."
            )
            last_es_id = 0
        log.info(f"highest_db_id, highest_es_id: {last_pg_id}, {last_es_id}")
        # Select all documents in-between and replicate to Elasticsearch.
        if last_pg_id > last_es_id:
            log.info(f"Replicating range {last_es_id}-{last_pg_id}")

            deleted, mature = get_existence_queries(table)
            query = SQL(
                "SELECT *, {deleted}, {mature} "
                "FROM {table} "
                "WHERE id BETWEEN {last_es_id} AND {last_pg_id} "
                "AND license_version IS NOT NULL;"
            ).format(
                deleted=deleted,
                mature=mature,
                table=Identifier(table),
                last_es_id=Literal(last_es_id),
                last_pg_id=Literal(last_pg_id),
            )
            self.es.indices.create(index=dest_idx, body=index_settings(table))
            self.replicate(table, dest_idx, query)

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

    def replicate(self, table, dest_index, query):
        """
        Replicate records from a given query.

        :param table: The table to replicate the data from.
        :param dest_index: The destination index to copy the data to.
        :param query: The SQL query used to select data to copy.
        :return:
        """
        cursor_name = table + "_indexing_cursor"
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
                    origin_table=table,
                    dest_index=dest_index,
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
                f"table '{table}' to Elasticsearch"
            )
            if self.finish_time is not None:
                self.finish_time.value = datetime.datetime.utcnow().timestamp()
        pg_conn.commit()
        pg_conn.close()

    @staticmethod
    def consistency_check(new_index, live_alias):
        """
        Indexing can fail for a number of reasons, such as a full disk inside of
        the Elasticsearch cluster, network errors that occurred during
        synchronization, and numerous other scenarios. This function does some
        basic comparison between the new search index and the database. If this
        check fails, an alert gets raised and the old index will be left in
        place. An operator must then investigate and either manually set the
        alias or remediate whatever circumstances interrupted the indexing job
        before running the indexing job once more.

        :param new_index: The newly created but not yet live index
        :param live_alias: The name of the live index
        :return: bool
        """
        es = elasticsearch_connect()
        if not es.indices.exists(index=live_alias):
            return True
        log.info("Refreshing and performing sanity check...")
        # Make sure there are roughly as many documents in Elasticsearch
        # as there are in our database.
        es.indices.refresh(index=new_index)
        _id, _ = get_last_item_ids(live_alias)
        new_count = Search(using=es, index=new_index).count()
        max_delta = 100
        delta = abs(_id - new_count)
        log.info(f"delta, max_delta: {delta}, {max_delta}")
        return delta < max_delta

    @staticmethod
    def go_live(write_index, live_alias):
        """
        Point the live index alias at the index we just created. Delete the
        previous one.
        """
        es = elasticsearch_connect()
        indices = set(es.indices.get("*"))
        # Re-enable replicas and refresh.
        es.indices.refresh(index=write_index)
        es.indices.put_settings(
            index=write_index, body={"index": {"number_of_replicas": 1}}
        )
        # Cluster status will always be yellow in development environments
        # because there will only be one node available. In production, there
        # are many nodes, and the index should not be promoted until all
        # shards have been initialized.
        environment = os.getenv("ENVIRONMENT", "local")
        if environment != "local":
            log.info("Waiting for replica shards. . .")
            es.cluster.health(index=write_index, wait_for_status="green", timeout="12h")
        # If the index exists already and it's not an alias, delete it.
        if live_alias in indices:
            log.warning("Live index already exists. Deleting and realiasing.")
            es.indices.delete(index=live_alias)
        # Create or update the alias so it points to the new index.
        if es.indices.exists_alias(live_alias):
            old = list(es.indices.get(live_alias).keys())[0]
            index_update = {
                "actions": [
                    {"remove": {"index": old, "alias": live_alias}},
                    {"add": {"index": write_index, "alias": live_alias}},
                ]
            }
            es.indices.update_aliases(index_update)
            log.info(f"Updated '{live_alias}' index alias to point to {write_index}")
            log.info(f"Deleting old index {old}")
            es.indices.delete(index=old)
        else:
            es.indices.put_alias(index=write_index, name=live_alias)
            log.info(f"Created '{live_alias}' index alias pointing to {write_index}")

    def listen(self, poll_interval=10):
        """
        Poll the database for changes every poll_interval seconds. If new data
        has been added to the database, index it.

        :arg poll_interval: The number of seconds to wait before polling the
        database for changes.
        """
        while True:
            log.info("Listening for updates...")
            try:
                for table in self.tables_to_watch:
                    self._index_table(table)
            except ESConnectionError:
                self.es = elasticsearch_connect()
            time.sleep(poll_interval)

    def reindex(self, model_name: str, distributed=True):
        """
        Copy contents of the database to a new Elasticsearch index. Create an
        index alias to make the new index the "live" index when finished.
        """
        suffix = uuid.uuid4().hex
        destination_index = model_name + "-" + suffix
        if distributed:
            self.es.indices.create(
                index=destination_index, body=index_settings(model_name)
            )
            schedule_distributed_index(database_connect(), destination_index)
        else:
            self._index_table(model_name, dest_idx=destination_index)
            self.go_live(destination_index, model_name)

    def update(self, model_name: str, since_date):
        log.info(f"Updating index {model_name} with changes since {since_date}")
        query = SQL(
            "SELECT * FROM {model_name} " "WHERE updated_on >= {since_date};"
        ).format(model_name=Identifier(model_name), since_date=Literal(since_date))
        self.replicate(model_name, model_name, query)

    @staticmethod
    def load_test_data(table):
        """Create test indices in Elasticsearch for QA."""
        create_search_qa_index(table)

    @staticmethod
    def pg_chunk_to_es(pg_chunk, columns, origin_table, dest_index):
        """
        Given a list of psycopg2 results, convert them all to Elasticsearch
        documents.
        """
        # Map column names to locations in the row tuple
        schema = {col[0]: idx for idx, col in enumerate(columns)}
        try:
            model = database_table_to_elasticsearch_model[origin_table]
        except KeyError:
            log.error(f"Table {origin_table} is not defined in elasticsearch_models.")
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reindex",
        default=None,
        help="Reindex data from a specific model in the database. Data is "
        "copied to a new index and then made 'live' using index aliases,"
        " making it possible to reindex without downtime.",
    )
    parser.add_argument(
        "--update",
        nargs=2,
        default=None,
        help="Update the Elasticsearch index with all changes since a UTC date."
        "ex: --update image 2018-11-09",
    )
    parsed = parser.parse_args()
    fmt = "%(asctime)s %(message)s"
    log.basicConfig(stream=sys.stdout, level=log.INFO, format=fmt)
    log.getLogger(TableIndexer.__name__).setLevel(log.INFO)
    log.info("Connecting to Elasticsearch")
    elasticsearch_client = elasticsearch_connect()
    syncer = TableIndexer(elasticsearch_client, replicate_tables)
    if parsed.reindex:
        log.info(f"Reindexing {parsed.reindex}")
        syncer.reindex(parsed.reindex)
    elif parsed.update:
        index, date = parsed.update
        syncer.update(index, date)
        log.info("Update finished.")
    else:
        log.info("Beginning indexer in daemon mode")
        syncer.listen(SYNCER_POLL_INTERVAL)
