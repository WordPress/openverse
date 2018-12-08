import falcon
import logging
import sys
import json
import uuid
from urllib.parse import urlparse
from multiprocessing import Value
from es_syncer.tasks import TaskTracker, IndexingTask, process_alive, \
    IndexingTaskTypes


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
        active = process_alive(task.pid)

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
