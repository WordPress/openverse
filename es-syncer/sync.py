import psycopg2
import os
import sys
import logging as log
import pdb
import time

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
AWS_REGION = os.environ.get('AWS_REGION')
AWS_SERVICE = 'es'

DATABASE_HOST = os.environ.get('DJANGO_DATABASE_HOST')
DATABASE_USER = os.environ.get('DJANGO_DATABASE_USER')
DATABASE_PASSWORD = os.environ.get('DJANGO_DATABASE_PASSWORD')
DATABASE_NAME = os.environ.get('DJANGO_DATABASE_NAME')

# The number of database records to load in memory at once.
ITER_BUFFER_SIZE = int(os.environ.get('SYNC_DATABASE_BUFFER_RECORD_COUNT', 100000))

# A comma separated list of tables in the Postgres table to replicate to Elasticsearch.
# Ex: image,docs
WATCH_TABLES = os.environ.get('WATCH_TABLES', 'image')
monitor_tables = WATCH_TABLES.split(',') if ',' in WATCH_TABLES else [WATCH_TABLES]


class ElasticsearchSyncer:
    """
    A class for synchronizing Postgres with Elasticsearch. For each table to
    sync, find its largest ID. Find the corresponding largest ID in
    Elasticsearch. If the database ID is greater than the largest corresponding
    ID in Elasticsearch, copy the missing records over.
    """

    def __init__(self, postgres_instance, elasticsearch_instance, tables_to_watch):
        self.pg_conn = postgres_instance
        self.es = elasticsearch_instance
        self.tables_to_watch = tables_to_watch

    def synchronize(self):
        for table in self.tables_to_watch:
            cur = self.pg_conn.cursor()
            # Find the last row added to the Postgres table
            cur.execute(SQL('SELECT id FROM {} ORDER BY id DESC LIMIT 1;').format(Identifier(table)))
            last_added_pg_id = cur.fetchone()[0]
            if not last_added_pg_id:
                log.warning('Tried to sync ' + table + ' but it was empty.')
                continue

            # Find the last document inserted into elasticsearch
            s = Search(using=self.es, index=table)
            s.aggs.bucket('highest_pg_id', 'max', field='pg_id')
            try:
                es_res = s.execute()
                last_added_es_id = int(es_res.aggregations['highest_pg_id']['value'])
            except (TypeError, NotFoundError):
                log.info('No matching documents found in elasticsearch. Replicating everything.')
                last_added_es_id = 0

            # Select all documents in-between and replicate them to Elasticsearch.
            if last_added_pg_id > last_added_es_id:
                log.info('Replicating range ' + str(last_added_es_id) + '-' + str(last_added_pg_id))
                # Query Postgres in chunks. Push each chunk to Elasticsearch in sequence.
                num_to_sync = last_added_pg_id - last_added_es_id
                cursor_name = table + '_table_cursor'
                server_cur = self.pg_conn.cursor(name=cursor_name)
                server_cur.itersize = ITER_BUFFER_SIZE
                server_cur.execute(SQL('SELECT * FROM {} LIMIT %s OFFSET %s').format(Identifier(table)),
                                   (num_to_sync, last_added_es_id,))
                num_converted_documents = 0

                chunk = 1
                while chunk:
                    chunk = server_cur.fetchmany(server_cur.itersize)
                    es_batch = self.pg_chunk_to_es(chunk, server_cur.description, table)
                    push_start_time = time.time()
                    log.info('Pushing ' + str(len(es_batch)) + ' documents to Elasticsearch.')
                    helpers.bulk(self.es, es_batch)
                    log.info('Pushed in ' + str(time.time() - push_start_time) + ' seconds.')
                    num_converted_documents += len(chunk)
                log.info('Synchronized ' + str(num_converted_documents) + ' to Elasticsearch')

    @staticmethod
    def pg_chunk_to_es(pg_chunk, columns, origin_table):
        """
        Given a list of psycopg2 results, convert them all to Elasticsearch documents.
        """
        # Map column names to locations in the row tuple
        schema = {col[0]: idx for idx, col in enumerate(columns)}
        try:
            model = postgres_table_to_elasticsearch_model[origin_table]
        except KeyError:
            log.error('Table ' + origin_table + ' is not defined in elasticsearch_models.')
            return []

        documents = []
        for row in pg_chunk:
            converted = model.postgres_to_elasticsearch(row, schema) \
                .to_dict(include_meta=True)
            documents.append(converted)

        return documents


def elasticsearch_connect(timeout=5):
    try:
        log.info('Trying to connect to Elasticsearch without authentication. . .')
        # Try to connect to Elasticsearch without credentials.
        es = Elasticsearch(host=ELASTICSEARCH_URL,
                           port=ELASTICSEARCH_PORT,
                           connection_class=RequestsHttpConnection,
                           timeout=10,
                           max_retries=3)
        log.info(str(es.info()))
        log.info('Connected to Elasticsearch without authentication.')
    except AuthenticationException:
        # If that fails, supply AWS authentication object and try again.
        log.info("Connecting to %s %s with AWS auth", ELASTICSEARCH_URL, ELASTICSEARCH_PORT)
        auth = AWSRequestsAuth(aws_access_key=AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                               aws_host=ELASTICSEARCH_URL,
                               aws_region='us-west-1',
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
    return psycopg2.connect(dbname=DATABASE_NAME,
                            user=DATABASE_USER,
                            password=DATABASE_PASSWORD,
                            host=DATABASE_HOST,
                            connect_timeout=5)


if __name__ == '__main__':
    log.basicConfig(stream=sys.stdout, level=log.INFO)
    log.info('Connecting to Postgres')
    postgres = postgres_connect()
    log.info('Connecting to Elasticsearch')
    elasticsearch = elasticsearch_connect()
    syncer = ElasticsearchSyncer(postgres, elasticsearch, monitor_tables)
    log.info('Beginning synchronization')
    syncer.synchronize()
