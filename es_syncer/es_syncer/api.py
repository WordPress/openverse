import falcon
import logging
import sys
import json
import uuid
import time
from urllib.parse import urlparse
from multiprocessing import Value
from es_syncer.tasks import TaskTracker, IndexingTask, process_alive, \
    IndexingTaskTypes

"""
A small API server for scheduling Elasticsearch indexing tasks.
"""


class IndexingTaskResource:
    def __init__(self, tracker: TaskTracker):
        self.tracker = tracker

    @staticmethod
    def _get_base_url(req):
        parsed = urlparse(req.url)
        return parsed.scheme + '://' + parsed.netloc

    @staticmethod
    def _validate_create_task(req_body):
        """
        Validate an index creation task.
        :return: None if valid else a string containing an error message.
        """
        if not req_body:
            return "No request body supplied."
        if 'model' not in req_body:
            return "No model supplied in request body."
        if 'action' not in req_body:
            return "No action supplied in request body."
        if req_body['action'] not in [x.name for x in IndexingTaskTypes]:
            return "Invalid action. Must be UPDATE or REINDEX."
        if req_body['action'] == 'UPDATE' and 'since_date' not in req_body:
            return "Received UPDATE request but no since_date."
        return None

    def on_post(self, req, resp):
        """ Create an indexing task. """
        body = json.loads(req.stream.read().decode('utf-8'))
        request_error = self._validate_create_task(body)
        if request_error:
            resp.status = falcon.HTTP_400
            resp.media = {
                'message': request_error
            }
            return
        model = body['model']
        action = body['action']
        since_date = body['since_date'] if 'since_date' in body else None
        task_id = str(uuid.uuid4())
        # Inject shared memory
        progress = Value('d', 0.0)
        finish_time = Value('d', 0.0)
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
        # Give the task a moment to start so we can detect immediate failure.
        time.sleep(0.1)
        if task.is_alive():
            resp.status = falcon.HTTP_202
            resp.media = {
                'message': 'Successfully scheduled indexing job',
                'task_id': task_id,
                'status_check': status_url
            }
        else:
            resp.status = falcon.HTTP_500
            resp.media = {
                'message': 'Failed to schedule task due to an internal server '
                           'error. Check indexing logs.'
            }

    def on_get(self, req, resp):
        """ List all indexing tasks. """
        resp.media = self.tracker.list_task_statuses()


class IndexingTaskStatus:
    def __init__(self, tracker: TaskTracker):
        self.tracker = tracker

    def on_get(self, req, resp, task_id):
        """ Check the status of a single task."""
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
indexing_task_resource = IndexingTaskResource(task_tracker)
get_task_status = IndexingTaskStatus(task_tracker)
api.add_route('/indexing_task', indexing_task_resource)
api.add_route('/indexing_task/{task_id}', get_task_status)
