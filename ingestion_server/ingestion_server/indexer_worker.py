"""
A single worker responsible for indexing a subset of the records stored in the
database.

Accept an HTTP request specifying a range of image IDs to reindex. After the
data has been indexed, notify Ingestion Server and stop the instance.
"""
import falcon
import sys
import logging as log
import os
import boto3
import requests
from multiprocessing import Value, Process
from psycopg2.sql import SQL

from ingestion_server.constants import MEDIA_TYPES
from ingestion_server.indexer import elasticsearch_connect, TableIndexer


ec2_client = boto3.client(
    'ec2',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', None),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', None)
)


class IndexingJobResource:
    def on_post(self, req, resp):
        j = req.media
        start_id = j['start_id']
        end_id = j['end_id']
        target_index = j['target_index']
        notify_url = f'http://{req.remote_addr}:8001/worker_finished'
        _execute_indexing_task(target_index, start_id, end_id, notify_url)
        log.info(f'Received indexing request for records {start_id}-{end_id}')
        resp.status = falcon.HTTP_201


class HealthcheckResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200


def _execute_indexing_task(target_index, start_id, end_id, notify_url):
    # Defaulting to 'image' for backward compatibility
    table_name = target_index.split('-')[0]
    if table_name not in MEDIA_TYPES:
        table_name = 'image'
    elasticsearch = elasticsearch_connect()
    progress = Value('d', 0.0)
    finish_time = Value('d', 0.0)
    exists_in_table = \
        'exists(SELECT 1 FROM {table} ' \
        'WHERE identifier = {table_name}.identifier) as "{name}"'
    exists_in_deleted_table = exists_in_table.format(
        table=f'api_deleted{table_name}', name='deleted',
        table_name=table_name
    )
    exists_in_mature_table = exists_in_table.format(
        table=f'api_mature{table_name}', name='mature'
    )

    query = SQL(f'''
                SELECT *,
                  {exists_in_deleted_table}, {exists_in_mature_table}
                FROM {table_name}
                WHERE id BETWEEN {start_id} AND {end_id}
                ''')
    log.info(f'Querying {query}')
    indexer = TableIndexer(
        elasticsearch, table_name, progress, finish_time
    )
    p = Process(
        target=_launch_reindex,
        args=(table_name, target_index, query, indexer, notify_url)
    )
    p.start()
    log.info('Started indexing task')


def _launch_reindex(table, target_index, query, indexer, notify_url):
    try:
        indexer.replicate(table, target_index, query)
    except Exception:
        log.error("Indexing error occurred: ", exc_info=True)

    log.info(f'Notifying {notify_url}')
    requests.post(notify_url)
    _self_destruct()
    return


def _self_destruct():
    """
    Stop this EC2 instance once the task is finished.
    """
    # Get instance ID from AWS metadata service
    if os.getenv('ENVIRONMENT', 'local') == 'local':
        log.info(
            'Skipping self destruction because worker is in local environment'
        )
        return
    endpoint = 'http://169.254.169.254/latest/meta-data/instance-id'
    response = requests.get(endpoint)
    instance_id = response.content.decode('utf8')
    log.info('Shutting self down')
    ec2_client.stop_instances(InstanceIds=[instance_id])


root = log.getLogger()
root.setLevel(log.DEBUG)
handler = log.StreamHandler(sys.stdout)
handler.setLevel(log.INFO)
formatter = log.Formatter(
    '%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(message)s'
)
handler.setFormatter(formatter)
root.addHandler(handler)
api = falcon.App()
api.add_route('/indexing_task', IndexingJobResource())
api.add_route('/healthcheck', HealthcheckResource())
