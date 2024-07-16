"""Simple in-memory tracking of executed tasks."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from multiprocessing.sharedctypes import Synchronized
from typing import Any


def _time_fmt(timestamp: float) -> str | None:
    """
    Format the timestamp into a human-readable date and time notation.

    :param timestamp: the timestamp to format
    :return: the human-readable form of the timestamp
    """

    if timestamp == 0:
        return None
    return str(datetime.datetime.utcfromtimestamp(timestamp))


@dataclass
class TaskInfo:
    task: Any
    start_time: float
    model: str
    target_index: str
    finish_time: Synchronized[float]
    progress: Synchronized[float]


class TaskTracker:
    def __init__(self):
        self.tasks = {}

    def add_task(self, task_id: str, **kwargs):
        """
        Store information about a new task in memory.

        :param task: the task being performed
        :param task_id: the UUID of the task
        """
        task_info = TaskInfo(
            start_time=datetime.datetime.utcnow().timestamp(), **kwargs
        )

        self.tasks[task_id] = task_info

    def get_task_status(self, task_id: str) -> dict:
        """
        Get the status of a single task with the given task ID.

        :param task_id: the ID of the task to get the status for
        :return: response dictionary containing all relevant info about the task
        """
        task_info = self.tasks[task_id]
        active = task_info.task.is_alive()
        model = task_info.model
        target_index = task_info.target_index
        start_time = task_info.start_time
        finish_time = task_info.finish_time.value
        progress = task_info.progress.value

        return {
            "task_id": task_id,
            "active": active,
            "model": model,
            "target_index": target_index,
            "progress": progress,
            "start_time": _time_fmt(start_time),
            "finish_time": _time_fmt(finish_time),
            # The task is considered to have errored if the task is no longer alive,
            # but progress did not reach 100%. This can happen if an individual chunk
            # of records fails to upload to ES.
            "error": progress < 100 and not active,
        }

    def get_task_list(self):
        """Get all listed tasks."""
        return [self.get_task_status(task_id) for task_id in self.tasks.keys()]
