"""
A single worker responsible for indexing a subset of the records stored in the database.

Accept an HTTP request specifying a range of image IDs to reindex.
"""

import logging as log
import uuid
from multiprocessing import Process, Value
from urllib.parse import urlparse

import boto3
import falcon
from decouple import config
from indexer_worker.indexer import launch_reindex
from indexer_worker.tasks import TaskTracker


ec2_client = boto3.client(
    "ec2",
    region_name=config("AWS_REGION", default="us-east-1"),
    aws_access_key_id=config("AWS_ACCESS_KEY_ID", default=None),
    aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY", default=None),
)


class HealthcheckResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200


class BaseTaskResource:
    """Base class for all resource that need access to a task tracker."""

    def __init__(self, tracker: TaskTracker, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tracker = tracker


class IndexingJobResource(BaseTaskResource):
    @staticmethod
    def _get_base_url(req):
        parsed = urlparse(req.url)
        return parsed.scheme + "://" + parsed.netloc

    def on_post(self, req, resp):
        body = req.get_media()

        task_id = uuid.uuid4().hex  # no hyphens
        model_name = body.get("model_name")
        table_name = body.get("table_name")
        target_index = body.get("target_index")
        start_id = body.get("start_id")
        end_id = body.get("end_id")
        log.info(f"Received indexing request for records {start_id}-{end_id}")

        # Shared memory
        progress = Value("d", 0.0)
        finish_time = Value("d", 0.0)

        task = Process(
            target=launch_reindex,
            kwargs={
                "model_name": model_name,
                "table_name": table_name,
                "target_index": target_index,
                "start_id": start_id,
                "end_id": end_id,
                # Task tracking arguments
                "progress": progress,
                "finish_time": finish_time,
            },
        )
        task.start()

        # Begin tracking the task
        self.tracker.add_task(
            task_id,
            task=task,
            model=model_name,
            progress=progress,
            finish_time=finish_time,
        )

        resp.status = falcon.HTTP_202
        resp.media = {
            "message": "Successfully scheduled task.",
            "task_id": task_id,
            "status_check": f"{self._get_base_url(req)}/task/{task_id}",
        }


class TaskStatusResource(BaseTaskResource):
    def on_get(self, _, resp, task_id):
        """Handle an incoming GET request and provide information about a single task."""

        try:
            result = self.tracker.get_task_status(task_id)
            resp.media = result
        except KeyError:
            resp.status = falcon.HTTP_404
            resp.media = {"message": f"No task found with id {task_id}."}


def create_api():
    """Create an instance of the Falcon API server."""
    _api = falcon.App()

    task_tracker = TaskTracker()

    _api.add_route("/healthcheck", HealthcheckResource())
    _api.add_route("/task", IndexingJobResource(task_tracker))
    _api.add_route("/task/{task_id}", TaskStatusResource(task_tracker))

    return _api


api = create_api()
