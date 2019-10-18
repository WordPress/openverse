"""
Accept an HTTP request specifying a range of image IDs to reindex. After the
data has been indexed, notify Ingestion Server and stop the instance.
"""
import falcon
import sys
import logging as log
from multiprocessing import Value
from psycopg2.sql import SQL
from ingestion_server.indexer import elasticsearch_connect, TableIndexer


class IndexingJobResource:
    def on_post(self, req, resp):
        j = req.media
        start_id = j['start_id']
        end_id = j['end_id']
        target_index = j['target_index']
        try:
            _execute_indexing_task(target_index, start_id, end_id)
        finally:
            _self_destruct()
        resp.status = falcon.HTTP_201


class HealthcheckResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200


def _execute_indexing_task(target_index, start_id, end_id):
    table = 'image'
    elasticsearch = elasticsearch_connect()
    progress = Value('d', 0.0)
    finish_time = Value('d', 0.0)
    query = SQL('SELECT * FROM {}'
                ' WHERE id BETWEEN {} AND {}'
                .format('image', start_id, end_id))
    log.info('Querying {}'.format(query))
    indexer = TableIndexer(
        elasticsearch, table, progress, finish_time
    )
    log.info('Starting indexing task')
    indexer.replicate(table, target_index, query)
    log.info('Finished replication')


def _self_destruct():
    """
    Stop this instance once the task is finished.
    """
    log.info('Shutting self down')
    pass


root = log.getLogger()
root.setLevel(log.DEBUG)
handler = log.StreamHandler(sys.stdout)
handler.setLevel(log.INFO)
formatter = log.Formatter(
    '%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(message)s'
)
handler.setFormatter(formatter)
root.addHandler(handler)
api = falcon.API()
api.add_route('/indexing_task', IndexingJobResource())
api.add_route('/healthcheck', HealthcheckResource())
