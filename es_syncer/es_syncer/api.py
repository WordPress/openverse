import falcon
import logging
import sys
import os
import json
from enum import Enum
from multiprocessing import Process
from es_syncer.sync import ElasticsearchSyncer, elasticsearch_connect


class IndexingTaskTypes(Enum):
    REINDEX = 0
    UPDATE = 1


class IndexingTask(Process):
    def __init__(self, model: str, task_type):
        Process.__init__(self)
        self.model = model
        self.task_type = task_type

    def run(self):
        elasticsearch = elasticsearch_connect()
        syncer = ElasticsearchSyncer(elasticsearch, self.model)
        if self.task_type == IndexingTaskTypes.REINDEX:
            syncer.reindex(self.model)
            logging.info('Indexing task exited.')


class CreateIndexingTask:
    def on_post(self, req, resp):
        """ Create an indexing task. """
        body = req.stream.read()
        model = body['index']
        task = IndexingTask(model, IndexingTaskTypes.REINDEX)
        task.start()
        resp.status = falcon.HTTP_202
        resp.media = {
            'message': 'Successfully scheduled indexing job',
            'task_id': task.pid
        }


class GetIndexingStatus:
    def on_get(self, req, resp):
        pass


root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s levelname)s %(filename)s:%(lineno)d %(process)d - %(message)s'
)
handler.setFormatter(formatter)
root.addHandler(handler)

api = falcon.API()
api.add_route('/indexing_task', CreateIndexingTask())
api.add_route('/indexing_task/{pid:int}', GetIndexingStatus())
