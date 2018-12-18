import falcon
import logging
import sys
import json
import uuid
import time
from urllib.parse import urlparse
from multiprocessing import Value
from es_syncer.tasks import TaskTracker, Task, TaskTypes

"""
A small API server for scheduling ingestion of upstream data and Elasticsearch 
indexing tasks.
"""


class TaskResource:
    def __init__(self, tracker: TaskTracker):
        self.tracker = tracker

    @staticmethod
    def _get_base_url(req):
        parsed = urlparse(req.url)
        return parsed.scheme + '://' + parsed.netloc

    @staticmethod
    def _validate_create_task(request):
        """
        Validate an index creation task.
        :return: None if valid else a string containing an error message.
        """
        if request == b'':
            return "Expected JSON request body but found nothing."
        request = json.loads(request.decode('utf-8'))
        if 'model' not in request:
            return "No model supplied in request body."
        if 'action' not in request:
            return "No action supplied in request body."
        if request['action'] not in [x.name for x in TaskTypes]:
            return "Invalid action. Must be UPDATE_INDEX or REINDEX."
        if request['action'] == 'UPDATE_INDEX' and 'since_date' not in request:
            return "Received UPDATE request but no since_date."

        return None

    def on_post(self, req, resp):
        """ Create a task. """
        raw_body = req.stream.read()
        request_error = self._validate_create_task(raw_body)
        if request_error:
            logging.warning(
                'Invalid request made. Reason: {}'.format(request_error)
            )
            resp.status = falcon.HTTP_400
            resp.media = {
                'message': request_error
            }
            return
        body = json.loads(raw_body.decode('utf-8'))
        model = body['model']
        action = body['action']
        since_date = body['since_date'] if 'since_date' in body else None
        task_id = str(uuid.uuid4())
        # Inject shared memory
        progress = Value('d', 0.0)
        finish_time = Value('d', 0.0)
        task = Task(
            model=model,
            task_type=TaskTypes[action],
            since_date=since_date,
            progress=progress,
            task_id=task_id,
            finish_time=finish_time
        )
        task.start()
        task_id = self.tracker \
            .add_task(task, task_id, action, progress, finish_time)
        base_url = self._get_base_url(req)
        status_url = base_url + '/task/{}'.format(task_id)
        # Give the task a moment to start so we can detect immediate failure.
        # TODO: Use IPC to detect if the job launched successfully instead
        # of giving it 100ms to crash. This is prone to race conditions.
        time.sleep(0.1)
        if task.is_alive():
            resp.status = falcon.HTTP_202
            resp.media = {
                'message': 'Successfully scheduled task',
                'task_id': task_id,
                'status_check': status_url
            }
            return
        else:
            resp.status = falcon.HTTP_500
            resp.media = {
                'message': 'Failed to schedule task due to an internal server '
                           'error. Check scheduler logs.'
            }
            return

    def on_get(self, req, resp):
        """ List all indexing tasks. """
        resp.media = self.tracker.list_task_statuses()


class TaskStatus:
    def __init__(self, tracker: TaskTracker):
        self.tracker = tracker

    def on_get(self, req, resp, task_id):
        """ Check the status of a single task."""
        task = self.tracker.id_task[task_id]
        active = task.is_alive()

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
task_resource = TaskResource(task_tracker)
get_task_status = TaskStatus(task_tracker)
api.add_route('/task', task_resource)
api.add_route('/task/{task_id}', get_task_status)
