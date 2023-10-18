"""Simple in-memory tracking of executed tasks."""

import datetime
import logging
from enum import Enum, auto
from functools import wraps
from multiprocessing import Value

import sentry_sdk

from ingestion_server import slack
from ingestion_server.constants.media_types import MediaType
from ingestion_server.es_helpers import elasticsearch_connect
from ingestion_server.indexer import TableIndexer
from ingestion_server.ingest import promote_api_table, refresh_api_table


class TaskTypes(Enum):
    @staticmethod
    def _generate_next_value_(name: str, *args, **kwargs) -> str:
        """
        Generate the value for ``auto()`` given the name of the enum item.

        Therefore, this function must be defined before any of the enum items.

        :param name: the enum variable name
        :return: the enum value
        """

        return name.lower()

    # Major index update

    REINDEX = auto()
    """create a new index for a given model in Elasticsearch"""

    POINT_ALIAS = auto()
    """map a given index to a given alias, used when going live with an index"""

    # Periodic data refresh

    INGEST_UPSTREAM = auto()  # includes `REINDEX`
    """refresh the API tables from the upstream database, then ``REINDEX``"""

    PROMOTE = auto()  # includes `POINT_ALIAS`
    """promote the refreshed table, then ``POINT_ALIAS``"""

    # Other

    UPDATE_INDEX = auto()  # TODO: delete eventually, rarely used
    """reindex updates to a model from the database since the given date"""

    DELETE_INDEX = auto()
    """delete the given index after it has been superseded by a new one"""

    CREATE_AND_POPULATE_FILTERED_INDEX = auto()
    """create a filtered index based on existing alias index"""

    def __str__(self):
        """
        Get the string representation of this enum.

        Unlike other objects, this does not default to ``__repr__``.

        :return: the string representation
        """

        return self.name


class TaskTracker:
    def __init__(self):
        self.tasks = {}

    def _prune_old_tasks(self):
        # TODO: Populate, document or delete function stub
        pass

    def add_task(self, task_id: str, **kwargs):
        """
        Store information about a new task in memory.

        :param task: the task being performed
        :param task_id: the UUID of the task
        """

        self._prune_old_tasks()

        self.tasks[task_id] = {
            "start_time": datetime.datetime.utcnow().timestamp(),
        } | kwargs

    @staticmethod
    def serialize_task_info(task_info: dict) -> dict:
        """
        Generate a response dictionary containing all relevant information about a task.

        :param task_info: the stored information about the task
        :return: the details of the task to show to the user
        """

        def _time_fmt(timestamp: int) -> str | None:
            """
            Format the timestamp into a human-readable date and time notation.

            :param timestamp: the timestamp to format
            :return: the human-readable form of the timestamp
            """

            if timestamp == 0:
                return None
            return str(datetime.datetime.utcfromtimestamp(timestamp))

        active = task_info["task"].is_alive()
        start_time = task_info["start_time"]
        finish_time = task_info["finish_time"].value
        progress = task_info["progress"].value
        active_workers = task_info["active_workers"].value
        is_bad_request = task_info["is_bad_request"].value
        return {
            "active": active,
            "model": task_info["model"],
            "action": str(task_info["action"]),
            "progress": progress,
            "start_timestamp": start_time,
            "start_time": _time_fmt(start_time),
            "finish_timestamp": finish_time,
            "finish_time": _time_fmt(finish_time),
            "active_workers": bool(active_workers),
            "error": progress < 100 and not active,
            "is_bad_request": bool(is_bad_request),
        }

    def list_task_statuses(self) -> list:
        """
        Get the statuses of all tasks.

        :return: the statuses of all tasks
        """

        results = [self.get_task_status(task_id) for task_id in self.tasks.keys()]
        results.sort(key=lambda task: task["finish_timestamp"])
        return results

    def get_task_status(self, task_id) -> dict:
        """
        Get the status of a single task with the given task ID.

        :param task_id: the ID of the task to get the status for
        :return: the status of the task
        """

        self._prune_old_tasks()

        task_info = self.tasks[task_id]
        return {"task_id": task_id} | self.serialize_task_info(task_info)


def _with_sentry(fn):
    """
    Wrap the decorated function for Sentry multiprocessing.

    Convenience function to wrap ``perform_task`` in such a way
    to extract the ``sentry_hub`` kwarg passed by ``api.py``, send
    exceptions to Sentry, and fully flush the client's Sentry
    queue before the worker exits.

    We cannot use the convenient ``ThreadingIntegration`` because it
    does not support ``multiprocessing``, only the legacy ``threading``
    module (we use ``multiprocessing``)
    """

    @wraps(fn)
    def fn_with_sentry(*args, **kwargs):
        hub = kwargs.pop("sentry_hub")
        with hub:
            try:
                result = fn(*args, **kwargs)
            except Exception as exc:
                result = None
                logging.error(exc, exc_info=exc)
                sentry_sdk.capture_exception(exc)

        client = hub.client
        if client is not None:
            # Sentry does not send events right away (it handles messages async)
            # and because the task finishing will shut down the worker thread
            # we need to flush the client before exiting the function.
            # ``client.flush`` will block until all messages in Sentry's queue are sent.
            # We do this _outside_ the try/except so that _anything_ passed to sentry
            # (like messages, etc) also get sent before the worker thread is closed.
            client.flush(timeout=5)

        return result

    return fn_with_sentry


@_with_sentry
def perform_task(
    task_id: str,
    model: MediaType,
    action: TaskTypes,
    callback_url: str | None,
    progress: Value,
    finish_time: Value,
    active_workers: Value,
    is_bad_request: Value,
    **kwargs,
):
    """
    Perform the requested task by invoking the task function with the correct arguments.

    Any additional keyword arguments will be forwarded to the task functions.

    :param task_id: the UUID assigned to the task for tracking
    :param model: the media type for which the action is being performed
    :param action: the name of the action being performed
    :param callback_url: the URL to which to make a request after the task is completed
    :param progress: shared memory for tracking the task's progress
    :param finish_time: shared memory for tracking the finish time of the task
    :param active_workers: shared memory for counting workers assigned to the task
    :param is_bad_request: shared memory that flags tasks that fail due to bad requests
    """

    elasticsearch = elasticsearch_connect()
    indexer = TableIndexer(
        elasticsearch,
        task_id,
        callback_url,
        progress,
        active_workers,
        is_bad_request,
    )

    # Task functions
    # ==============
    # These functions must have a signature of ``Callable[[], None]``.

    def ingest_upstream():  # includes ``reindex``
        refresh_api_table(model, model, progress)
        # For audio, also refresh the audioset view
        if model == "audio":
            refresh_api_table("audioset_view", "audioset", progress, approach="basic")
        indexer.reindex(model, f"temp_import_{model}", **kwargs)

    def promote():  # includes point alias
        promote_api_table(model, progress)
        if model == "audio":
            promote_api_table("audioset", progress)
        indexer.point_alias(model, **kwargs)

    try:
        locs = locals()  # contains all the task functions defined above
        if func := locs.get(action.value):
            func()  # Run the task function if it is defined
        elif func := getattr(indexer, action.value):
            func(model, **kwargs)  # Directly invoke indexer methods if no task function
    except Exception as err:
        exception_type = f"{err.__class__.__module__}.{err.__class__.__name__}"
        slack.error(
            f":x_red: Error processing task `{action}` for `{model}` "
            f"(`{exception_type}`): \n"
            f"```\n{err}\n```"
        )
        raise

    finish_time.value = datetime.datetime.utcnow().timestamp()
    logging.info(f"Task {task_id} completed.")
