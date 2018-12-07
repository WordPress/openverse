import falcon
import logging
import sys
import json
import uuid
import os
from enum import Enum
from multiprocessing import Process, Value
from es_syncer.sync import elasticsearch_connect, TableIndexer


class IndexingTaskTypes(Enum):
    REINDEX = 0
    UPDATE = 1


class TaskTracker:
    def __init__(self):
        self.id_to_task = {}
        self.id_to_action = {}
        self.id_to_progress = {}

    def add_task(self, task, action, progress):
        task_id = str(uuid.uuid4())
        self.id_to_task[task_id] = task
        self.id_to_action[task_id] = action
        self.id_to_progress[task_id] = progress
        return task_id


class IndexingTask(Process):
    def __init__(self, model: str, task_type, since_date: str, progress):
        Process.__init__(self)
        self.model = model
        self.task_type = task_type
        self.since_date = since_date
        self.progress = progress

    def run(self):
        elasticsearch = elasticsearch_connect()
        indexer = TableIndexer(elasticsearch, self.model, self.progress)
        if self.task_type == IndexingTaskTypes.REINDEX:
            indexer.reindex(self.model)
            logging.info('Indexing task exited.')
        elif self.task_type == IndexingTaskTypes.UPDATE:
            indexer.update(self.model, self.since_date)


class CreateIndexingTask:
    def __init__(self, tracker: TaskTracker):
        self.tracker = tracker

    def on_post(self, req, resp):
        """ Create an indexing task. """
        body = json.loads(req.stream.read().decode('utf-8'))
        model = body['model']
        action = body['action']
        since_date = body['since_date'] if 'since_date' in body else None
        progress = Value('d', 0.0)
        task = IndexingTask(
            model,
            IndexingTaskTypes[action],
            since_date,
            progress
        )
        task_id = self.tracker.add_task(task, action, progress)
        task.start()
        resp.status = falcon.HTTP_202
        resp.media = {
            'message': 'Successfully scheduled indexing job',
            'task_id': task_id
        }


class GetIndexingTaskStatus:
    def __init__(self, tracker: TaskTracker):
        self.tracker = tracker

    def on_get(self, req, resp, task_id):
        task = self.tracker.id_to_task[task_id]
        active = True
        if os.path.isdir('/proc/{}'.format(task.pid)):
            with open('/proc/{}'.format(task.pid) + '/status') as procfile:
                if 'zombie' in procfile.read():
                    active = False
        else:
            active = False

        percent_completed = self.tracker.id_to_progress[task_id].value
        failed = percent_completed < 100 and not active
        resp.media = {
            'active': active,
            'percent_completed': percent_completed,
            'error': failed
        }


root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s levelname)s %(filename)s:%(lineno)d - %(message)s'
)
handler.setFormatter(formatter)
root.addHandler(handler)

api = falcon.API()
task_tracker = TaskTracker()
create_indexing_task = CreateIndexingTask(task_tracker)
get_task_status = GetIndexingTaskStatus(task_tracker)
api.add_route('/indexing_task', create_indexing_task)
api.add_route('/indexing_task/{task_id}', get_task_status)
