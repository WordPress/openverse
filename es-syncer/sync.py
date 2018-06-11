import psycopg2
import os
import sys
import logging as log
import time
import multiprocessing
import pdb

from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.exceptions import AuthenticationException, NotFoundError
from elasticsearch_dsl import Search
from elasticsearch import helpers
from psycopg2.sql import SQL, Identifier
from elasticsearch_models import postgres_table_to_elasticsearch_model

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
ELASTICSEARCH_PORT = int(os.environ.get('ELASTICSEARCH_PORT'))
AWS_REGION = os.environ.get('AWS_REGION', 'us-west-1')

DATABASE_HOST = os.environ.get('DJANGO_DATABASE_HOST')
DATABASE_USER = os.environ.get('DJANGO_DATABASE_USER')
DATABASE_PASSWORD = os.environ.get('DJANGO_DATABASE_PASSWORD')
DATABASE_NAME = os.environ.get('DJANGO_DATABASE_NAME')
DATABASE_PORT = int(os.environ.get('DJANGO_DATABASE_PORT', 5432))

# The number of database records to load in memory at once.
DB_BUFFER_SIZE = int(os.environ.get('DB_BUFFER_SIZE', 100000))

# A comma separated list of tables in the Postgres table to replicate to
# Elasticsearch. Ex: image,docs
REP_TABLES = os.environ.get('COPY_TABLES', 'image')
replicate_tables = REP_TABLES.split(',') if ',' in REP_TABLES else [REP_TABLES]


class ElasticsearchSyncer:
    """
    A class for synchronizing Postgres with Elasticsearch. For each table to
    sync, find its largest ID. Find the corresponding largest ID in
    Elasticsearch. If the database ID is greater than the largest corresponding
    ID in Elasticsearch, copy the missing records over to Elasticsearch.

    Each table is Postgres corresponds to an identically named index in
    Elasticsearch. For instance, if Postgres has a table that we would like to
    replicate called 'image', the syncer will create an Elasticsearch called
    'image' and populate the index with documents.
    """

    def __init__(self, postgres_instance, elasticsearch_instance, tables):
        self.pg_conn = postgres_instance
        self.es = elasticsearch_instance
        self.tables_to_watch = tables

    def synchronize(self):
        for table in self.tables_to_watch:
            cur = self.pg_conn.cursor()
            # Find the last row added to the Postgres table
            cur.execute(
                SQL('SELECT id FROM {} ORDER BY id DESC LIMIT 1;').format(
                    Identifier(table)
                )
            )
            last_added_pg_id = cur.fetchone()[0]
            if not last_added_pg_id:
                log.warning('Tried to sync ' + table + ' but it was empty.')
                continue

            # Find the last document inserted into elasticsearch
            s = Search(using=self.es, index=table)
            s.aggs.bucket('highest_pg_id', 'max', field='pg_id')
            try:
                es_res = s.execute()
                last_added_es_id = int(
                    es_res.aggregations['highest_pg_id']['value']
                )
            except (TypeError, NotFoundError):
                log.info('No matching documents found in elasticsearch.'
                         ' Replicating everything.')
                last_added_es_id = 0

            # Select all documents in-between and replicate to Elasticsearch.
            if last_added_pg_id > last_added_es_id:
                log.info(
                    'Replicating range ' + str(last_added_es_id) + '-' +
                    str(last_added_pg_id)
                )
                self.replicate(last_added_es_id, last_added_pg_id, table)

    def replicate(self, start, end, table):
        # Query Postgres in chunks.
        num_to_sync = end - start
        cursor_name = table + '_table_cursor'
        with self.pg_conn.cursor(name=cursor_name) as server_cur:
            server_cur.itersize = DB_BUFFER_SIZE
            server_cur.execute(
                SQL('SELECT * FROM {} LIMIT %s OFFSET %s').format(
                    Identifier(table)
                ),
                (num_to_sync, start,)
            )

            num_converted_documents = 0
            # Fetch a chunk and push it to Elasticsearch. Repeat until we run
            # out of chunks.
            while True:
                chunk = server_cur.fetchmany(server_cur.itersize)
                if not chunk:
                    break
                es_batch = self.pg_chunk_to_es(
                    chunk, server_cur.description, table
                )
                push_start_time = time.time()
                log.info(
                    'Pushing ' + str(len(es_batch)) + ' docs to Elasticsearch.'
                )
                # Bulk upload to Elasticsearch in parallel.
                chunk_size = int(num_to_sync / multiprocessing.cpu_count())
                helpers.parallel_bulk( self.es, es_batch, chunk_size=chunk_size)

                log.info(
                    'Pushed in ' + str(time.time() - push_start_time) + 's.'
                )
                num_converted_documents += len(chunk)
            log.info(
                'Synchronized ' + str(num_converted_documents) + ' from table '
                + table + ' to Elasticsearch'
            )

    def listen(self, poll_interval=5):
        """
        Poll the database for changes every poll_interval seconds.

        :arg poll_interval: The number of seconds to wait before polling the
        database for changes.
        """
        while True:
            log.info('Polling Postgres for changes...')
            try:
                self.synchronize()
            except psycopg2.OperationalError:
                # Reconnect to the database.
                self.pg_conn = postgres_connect()

            time.sleep(poll_interval)

    @staticmethod
    def pg_chunk_to_es(pg_chunk, columns, origin_table):
        """
        Given a list of psycopg2 results, convert them all to Elasticsearch
        documents.
        """
        # Map column names to locations in the row tuple
        schema = {col[0]: idx for idx, col in enumerate(columns)}
        try:
            model = postgres_table_to_elasticsearch_model[origin_table]
        except KeyError:
            log.error(
                'Table ' + origin_table +
                ' is not defined in elasticsearch_models.'
            )
            return []

        documents = []
        for row in pg_chunk:
            converted = model.postgres_to_elasticsearch(row, schema) \
                .to_dict(include_meta=True)
            documents.append(converted)

        return documents


def elasticsearch_connect(timeout=300):
    """
    Connect to Elasticsearch.
    :param timeout: How long to wait before ANY request to Elasticsearch times
    out. Because we use parallel bulk uploads (which sometimes wait long periods
    of time before beginning execution), a value of at least 30 seconds is
    recommended.
    :return:
    """
    try:
        log.info('Trying to connect to Elasticsearch without authentication...')
        # Try to connect to Elasticsearch without credentials.
        es = Elasticsearch(host=ELASTICSEARCH_URL,
                           port=ELASTICSEARCH_PORT,
                           connection_class=RequestsHttpConnection,
                           timeout=timeout,
                           max_retries=10)
        log.info(str(es.info()))
        log.info('Connected to Elasticsearch without authentication.')
    except AuthenticationException:
        # If that fails, supply AWS authentication object and try again.
        log.info("Connecting to %s %s with AWS auth", ELASTICSEARCH_URL,
                 ELASTICSEARCH_PORT)
        auth = AWSRequestsAuth(aws_access_key=AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                               aws_host=ELASTICSEARCH_URL,
                               aws_region=AWS_REGION,
                               aws_service='es')
        auth.encode = lambda x: bytes(x.encode('utf-8'))
        es = Elasticsearch(host=ELASTICSEARCH_URL,
                           port=ELASTICSEARCH_PORT,
                           connection_class=RequestsHttpConnection,
                           timeout=timeout,
                           max_retries=10, retry_on_timeout=True,
                           http_auth=auth)
        es.info()
    return es


def postgres_connect():
    while True:
        try:
            conn = psycopg2.connect(dbname=DATABASE_NAME,
                                    user=DATABASE_USER,
                                    password=DATABASE_PASSWORD,
                                    host=DATABASE_HOST,
                                    port=DATABASE_PORT,
                                    connect_timeout=5)
        except psycopg2.OperationalError as e:
            log.exception(e)
            log.error('Reconnecting to Postgres in 5 seconds. . .')
            time.sleep(5)
            continue
        break

    return conn


if __name__ == '__main__':
    log.basicConfig(stream=sys.stdout, level=log.INFO)
    log.getLogger(ElasticsearchSyncer.__name__).setLevel(log.DEBUG)
    log.info('Connecting to Postgres')
    postgres = postgres_connect()
    log.info('Connecting to Elasticsearch')
    elasticsearch = elasticsearch_connect()
    syncer = ElasticsearchSyncer(postgres, elasticsearch, replicate_tables)
    log.info('Beginning synchronizer')
    syncer.listen()
