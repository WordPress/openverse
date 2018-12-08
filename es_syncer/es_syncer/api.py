import falcon
import logging
import sys
import json
import uuid
import os
import datetime as dt
from urllib.parse import urlparse
from enum import Enum
from multiprocessing import Process, Value
from es_syncer.sync import elasticsearch_connect, TableIndexer


class IndexingTaskTypes(Enum):
    REINDEX = 0
    UPDATE = 1


class TaskTracker:
    def __init__(self):
        self.id_task = {}
        self.id_action = {}
        self.id_progress = {}
        self.id_finish_time = {}

    def add_task(self, task, task_id, action, progress, finish_time):
        self.prune_old_tasks()
        self.id_task[task_id] = task
        self.id_action[task_id] = action
        self.id_progress[task_id] = progress
        self.id_finish_time[task_id] = finish_time
        return task_id

    def prune_old_tasks(self):
        # TODO Delete old and irrelevant tasks from the TaskTracker
        pass

    def list_task_statuses(self):
        results = {}
        for _id, task in self.id_task.items():
            percent_completed = self.id_progress[_id].value
            active = _process_alive(task.pid)
            finish_time = self.id_finish_time[_id].value
            if finish_time == 0.0:
                finish_time = None
            else:
                finish_time = str(dt.datetime.utcfromtimestamp(finish_time))
            results[_id] = {
                'active': active,
                'action': self.id_action[_id],
                'progress': percent_completed,
                'error': percent_completed < 100 and not active,
                'finish_time': finish_time
            }
        return results


class IndexingTask(Process):
    def __init__(self, model, task_type, since_date, progress, task_id,
                 finish_time):
        Process.__init__(self)
        self.model = model
        self.task_type = task_type
        self.since_date = since_date
        self.progress = progress
        self.task_id = task_id
        self.finish_time = finish_time

    def run(self):
        elasticsearch = elasticsearch_connect()
        indexer = TableIndexer(
            elasticsearch, self.model, self.progress, self.finish_time
        )
        if self.task_type == IndexingTaskTypes.REINDEX:
            indexer.reindex(self.model)
        elif self.task_type == IndexingTaskTypes.UPDATE:
            indexer.update(self.model, self.since_date)
        logging.info('Indexing task exited.')


def _process_alive(pid: int):
    active = True
    if os.path.isdir('/proc/{}'.format(pid)):
        with open('/proc/{}'.format(pid) + '/status') as procfile:
            if 'zombie' in procfile.read():
                active = False
    else:
        active = False
    return active


class CreateIndexingTask:
    def __init__(self, tracker: TaskTracker):
        self.tracker = tracker

    @staticmethod
    def _get_base_url(req):
        parsed = urlparse(req.url)
        return parsed.scheme + '://' + parsed.netloc

    def on_post(self, req, resp):
        """ Create an indexing task. """
        body = json.loads(req.stream.read().decode('utf-8'))
        model = body['model']
        action = body['action']
        since_date = body['since_date'] if 'since_date' in body else None
        progress = Value('d', 0.0)
        finish_time = Value('d', 0.0)
        task_id = str(uuid.uuid4())
        task = IndexingTask(
            model,
            IndexingTaskTypes[action],
            since_date,
            progress,
            task_id,
            finish_time
        )
        task.start()
        task_id = self.tracker \
            .add_task(task, task_id, action, progress, finish_time)
        base_url = self._get_base_url(req)
        status_url = base_url + '/indexing_task/{}'.format(task_id)
        resp.status = falcon.HTTP_202
        resp.media = {
            'message': 'Successfully scheduled indexing job',
            'task_id': task_id,
            'status_check': status_url
        }

    def on_get(self, req, resp):
        """ List all indexing tasks. """
        resp.media = self.tracker.list_task_statuses()


class GetIndexingTaskStatus:
    def __init__(self, tracker: TaskTracker):
        self.tracker = tracker

    def on_get(self, req, resp, task_id):
        task = self.tracker.id_task[task_id]
        active = _process_alive(task.pid)

        percent_completed = self.tracker.id_progress[task_id].value
        resp.media = {
            'active': active,
            'percent_completed': percent_completed,
            'error': percent_completed < 100 and not active
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
