"""A small RPC API server for scheduling data refresh and indexing tasks."""
from collections import defaultdict

import logging
import os
import time
import uuid
from multiprocessing import Process, Value
from pathlib import Path
from urllib.parse import urlparse

import falcon
import sentry_sdk
from falcon.media.validators import jsonschema
from sentry_sdk.integrations.falcon import FalconIntegration

from ingestion_server import slack
from ingestion_server.constants.media_types import MEDIA_TYPES, MediaType
from ingestion_server.db_helpers import (
    DB_UPSTREAM_CONFIG,
    DB_API_CONFIG,
    database_connect,
)
from ingestion_server.es_helpers import elasticsearch_connect, get_stat
from ingestion_server.indexer import TableIndexer
from ingestion_server.state import clear_state, worker_finished
from ingestion_server.tasks import TaskTracker, TaskTypes, perform_task


MODEL = "model"
ACTION = "action"
CALLBACK_URL = "callback_url"
SINCE_DATE = "since_date"

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    integrations=[
        FalconIntegration(),
    ],
    traces_sample_rate=os.environ.get("SENTRY_SAMPLE_RATE", 1.0),
    environment=os.environ.get("ENVIRONMENT"),
)


class HealthResource:
    @staticmethod
    def on_get(req, resp):
        """
        Health check for the service. Optionally check on resources with the
        check_deps=true parameter.
        """
        # Set the initial response, but change it if necessary
        resp.status = falcon.HTTP_200
        resp.media = {"status": "200 OK"}

        if not req.get_param_as_bool("check_deps", blank_as_true=False):
            return

        messages = defaultdict(list)
        # Elasticsearch checks
        es = elasticsearch_connect(timeout=3)
        if not es:
            messages["es"].append("Elasticsearch could not be reached")
        else:
            es_health = es.cluster.health(timeout="3s")
            if es_health["timed_out"]:
                messages["es"].append("Elasticsearch health check timed out")
            if (es_status := es_health["status"]) != "green":
                messages["es"].append(f"Elasticsearch cluster health: {es_status}")

        # Database checks
        for name, dbconfig in zip(
            ["upstream", "api"],
            [DB_UPSTREAM_CONFIG, DB_API_CONFIG],
        ):
            db = database_connect(dbconfig=dbconfig, timeout=3, attempt_reconnect=False)
            if not db:
                messages["db"].append(
                    f"Database connection for '{name}' could not be established"
                )

        if messages:
            resp.status = falcon.HTTP_503
            resp.media = {"status": "503 Service Unavailable", "dependencies": messages}


class StatResource:
    @staticmethod
    def on_get(_, res, name):
        """
        Handle an incoming GET request and provides info about the given index or alias.

        :param _: the incoming request
        :param res: the appropriate response
        :param name: the name of the index or alias
        :return: the information about the index or alias
        """

        elasticsearch = elasticsearch_connect()
        stat = get_stat(elasticsearch, name)
        res.status = falcon.HTTP_200
        res.media = stat._asdict()


class BaseTaskResource:
    """Base class for all resource that need access to a task tracker."""

    def __init__(self, tracker: TaskTracker, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tracker = tracker


class TaskResource(BaseTaskResource):
    @staticmethod
    def _get_base_url(req):
        parsed = urlparse(req.url)
        return parsed.scheme + "://" + parsed.netloc

    @jsonschema.validate(
        req_schema={
            "type": "object",
            "properties": {
                "model": {"type": "string", "enum": MEDIA_TYPES},
                "action": {
                    "type": "string",
                    "enum": list(task_type.name for task_type in TaskTypes),
                },
                # Accepts all forms described in the PostgreSQL documentation:
                # https://www.postgresql.org/docs/current/datatype-datetime.html
                "since_date": {"type": "string"},
                "index_suffix": {"type": "string"},
                "alias": {"type": "string"},
                "force_delete": {"type": "boolean"},
                "origin_index_suffix": {"type": "string"},
                "destination_index_suffix": {"type": "string"},
            },
            "required": ["model", "action"],
            "allOf": [
                {
                    "if": {
                        "properties": {"action": {"const": TaskTypes.POINT_ALIAS.name}}
                    },
                    "then": {"required": ["index_suffix", "alias"]},
                },
                {
                    "if": {"properties": {"action": {"const": TaskTypes.PROMOTE.name}}},
                    "then": {"required": ["index_suffix", "alias"]},
                },
                # TODO: delete eventually, rarely used
                {
                    "if": {
                        "properties": {"action": {"const": TaskTypes.UPDATE_INDEX.name}}
                    },
                    "then": {"required": ["index_suffix", "since_date"]},
                },
                {
                    "if": {
                        "properties": {"action": {"const": TaskTypes.DELETE_INDEX.name}}
                    },
                    "then": {
                        "oneOf": [
                            {"required": ["alias"]},
                            {"required": ["index_suffix"]},
                        ]
                    },
                },
            ],
        }
    )
    def on_post(self, req, res):
        """
        Handle an incoming POST request and schedule the specified task.

        :param req: the incoming request
        :param res: the appropriate response
        """

        body = req.get_media()

        # Generated fields
        task_id = uuid.uuid4().hex  # no hyphens

        # Required fields

        model: MediaType = body[MODEL]
        action = TaskTypes[body[ACTION]]

        # Optional fields
        callback_url = body.get("callback_url")
        since_date = body.get("since_date")
        index_suffix = body.get("index_suffix", task_id)
        origin_index_suffix = body.get("origin_index_suffix")
        destination_index_suffix = body.get("destination_index_suffix")
        alias = body.get("alias")
        force_delete = body.get("force_delete", False)

        # Shared memory
        progress = Value("d", 0.0)
        finish_time = Value("d", 0.0)
        active_workers = Value("i", int(False))
        is_bad_request = Value("i", 0)

        task_sentry_hub = sentry_sdk.Hub(sentry_sdk.Hub.current)
        task = Process(
            target=perform_task,
            kwargs={
                "task_id": task_id,
                "model": model,
                "action": action,
                "callback_url": callback_url,
                "progress": progress,
                "finish_time": finish_time,
                "active_workers": active_workers,
                "is_bad_request": is_bad_request,
                # Task-specific keyword arguments
                "since_date": since_date,
                "index_suffix": index_suffix,
                "origin_index_suffix": origin_index_suffix,
                "destination_index_suffix": destination_index_suffix,
                "alias": alias,
                "force_delete": force_delete,
                "sentry_hub": task_sentry_hub,
            },
        )
        task.start()

        self.tracker.add_task(
            task_id,
            task=task,
            model=model,
            action=action,
            callback_url=callback_url,
            progress=progress,
            finish_time=finish_time,
            active_workers=active_workers,
            is_bad_request=is_bad_request,
        )

        base_url = self._get_base_url(req)
        status_url = f"{base_url}/task/{task_id}"

        # Give the task a moment to start so we can detect immediate failure.
        # TODO: Use IPC to detect if the job launched successfully instead
        # of giving it 100ms to crash. This is prone to race conditions.
        time.sleep(0.1)
        if task.is_alive():
            res.status = falcon.HTTP_202
            res.media = {
                "message": "Successfully scheduled task",
                "task_id": task_id,
                "status_check": status_url,
            }
        elif progress.value == 100:
            res.status = falcon.HTTP_202
            res.media = {
                "message": "Successfully completed task",
                "task_id": task_id,
                "status_check": status_url,
            }
        elif is_bad_request.value == 1:
            res.status = falcon.HTTP_400
            res.media = {
                "message": (
                    "Failed during task execution due to bad request. "
                    "Check scheduler logs."
                )
            }
        else:
            res.status = falcon.HTTP_500
            res.media = {
                "message": (
                    "Failed to schedule task due to an internal server error. "
                    "Check scheduler logs."
                )
            }

    def on_get(self, _, res):
        """
        Handle an incoming GET request and provide information about all past tasks.

        :param _: the incoming request
        :param res: the appropriate response
        """

        res.media = self.tracker.list_task_statuses()


class TaskStatus(BaseTaskResource):
    def on_get(self, _, res, task_id):
        """
        Handle an incoming GET request and provide information about a single task.

        :param _: the incoming request
        :param res: the appropriate response
        :param task_id: the ID of the task for which to get the information
        """

        try:
            result = self.tracker.get_task_status(task_id)
            res.media = result
        except KeyError:
            res.status = falcon.HTTP_404
            res.media = {"message": f"No task found with id {task_id}."}


class WorkerFinishedResource(BaseTaskResource):
    def on_post(self, req, _):
        """
        Handle an incoming POST request and record messages sent from indexer workers.

        :param req: the incoming request
        :param _: the appropriate response
        """

        task_data = worker_finished(str(req.remote_addr), req.media["error"])
        task_id = task_data.task_id
        target_index = task_data.target_index
        task_info = self.tracker.tasks[task_id]
        active_workers = task_info["active_workers"]

        # Update global task progress based on worker results
        task_info["progress"].value = task_data.percent_successful

        if task_data.percent_successful == 100:
            logging.info(f"All indexer workers succeeded! New index: {target_index}")
            index_type = target_index.split("-")[0]
            if index_type not in MEDIA_TYPES:
                index_type = "image"
            slack.verbose(
                f"`{index_type}`: Elasticsearch reindex complete | "
                f"_Next: re-apply indices & constraints_"
            )

            elasticsearch = elasticsearch_connect()
            indexer = TableIndexer(
                elasticsearch,
                task_id,
                task_info["callback_url"],
                task_info["progress"],
                task_info["active_workers"],
            )
            task = Process(
                target=indexer.refresh,
                kwargs={
                    "index_name": target_index,
                    "change_settings": True,
                },
            )
            task.start()
            indexer.ping_callback()
        elif task_data.percent_completed == 100:
            # All workers finished, but not all were successful. Mark
            # workers as complete and do not attempt to go live with the new
            # indices.
            active_workers.value = int(False)


class StateResource:
    @staticmethod
    def on_delete(_, __):
        """Forget about the last scheduled indexing job."""

        clear_state()


def create_api():
    """Create an instance of the Falcon API server."""

    _api = falcon.App()

    task_tracker = TaskTracker()

    _api.add_route("/", HealthResource())
    _api.add_route("/stat/{name}", StatResource())
    _api.add_route("/task", TaskResource(task_tracker))
    _api.add_route("/task/{task_id}", TaskStatus(task_tracker))
    _api.add_route("/worker_finished", WorkerFinishedResource(task_tracker))
    _api.add_route("/state", StateResource())
    _api.add_static_route("/static", (Path(".") / "static").absolute())

    return _api


api = create_api()
