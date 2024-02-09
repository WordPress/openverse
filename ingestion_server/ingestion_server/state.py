"""
Handles operations pertaining to the state of indexe workers.

Indexing is distributed across multiple independent hosts. We don't want to
"go live" in production with the newly indexed data until all of the indexing
workers have finished their tasks. To that end, we need to track the state of
each worker, and be notified when the job has finished.

State is persisted to the disk using shelve. Concurrent writes aren't allowed,
so all operations need to acquire a lock.
"""

import datetime
import enum
import logging as log
import shelve
from typing import NamedTuple

from decouple import config
from filelock import FileLock


lock_path = config("LOCK_PATH", default="lock")
shelf_path = config("SHELF_PATH", default="db")


class WorkerStatus(enum.Enum):
    RUNNING = 0
    FINISHED = 1
    ERROR = 2


class TaskData(NamedTuple):
    target_index: int
    task_id: str
    percent_successful: float
    percent_completed: float


def is_indexing_in_progress(db):
    """
    Determine whether any indexing is in progress, by checking to see if there are any
    registered workers with the RUNNING status.

    :param db: the Shelf object representing worker state on disk.
    :return: True if there are any active indexer workers.
    """
    if "worker_statuses" in db:
        for worker in db["worker_statuses"]:
            if db["worker_statuses"][worker] == WorkerStatus.RUNNING:
                return True
    return False


def register_indexing_job(worker_ips, target_index, task_id):
    """
    Track the active indexer workers to prevent concurrent indexing jobs.

    :param worker_ips: A list of private IP addresses corresponding to the pool
    of relevant indexer-worker instances.
    :param target_index: The name of the Elasticsearch index that will be
    promoted to production after indexing is complete
    :param task_id: The id of the data_refresh task scheduling these workers.
    :return: Return True if scheduling succeeds
    """
    with FileLock(lock_path), shelve.open(shelf_path, writeback=True) as db:
        if is_indexing_in_progress(db):
            log.error("Failed to schedule indexing job; another one is running.")
            return False

        # Register the workers.
        worker_statuses = {}
        for worker_url in worker_ips:
            worker_statuses[worker_url] = WorkerStatus.RUNNING
        db["worker_statuses"] = worker_statuses
        db["start_time"] = datetime.datetime.now()
        db["target_index"] = target_index
        db["task_id"] = task_id
        return True


def has_active_workers_for_task_id(task_id):
    """
    Determine whether there are any actively running indexer-worker instances
    for the given task_id, even if the parent task has completed.

    :param task_id: The id of the data_refresh task to check.
    :return: Return True if there are any active workers for this task.
    """
    with FileLock(lock_path), shelve.open(shelf_path) as db:
        if "task_id" in db and db["task_id"] == task_id:
            return is_indexing_in_progress(db)

        # There can only be one indexing job happening at a time, so if the currently
        # registered `task_id` does not match the one we're looking for, we can
        # be sure there are no active workers for this task.
        return False


def worker_finished(worker_ip, error):
    """
    Receive the notifications indicating an indexing worker has finished its task.

    :param worker_ip: The private IP of the worker.
    :param error: Whether this worker had an error during processing.
    :return: TaskData namedtuple containing the target index, task_id, and the
    percent of workers that have completed and that were successful.
    """
    with FileLock(lock_path), shelve.open(shelf_path, writeback=True) as db:
        try:
            _ = db["worker_statuses"][worker_ip]
            db["worker_statuses"][worker_ip] = (
                WorkerStatus.FINISHED if not error else WorkerStatus.ERROR
            )
            log.info(f"Received worker_finished signal from {worker_ip}")
        except KeyError:
            log.error(
                "An indexer worker notified us it finished its task, but "
                "we are not tracking it."
            )
        total_workers = len(db["worker_statuses"])
        completed_workers = 0
        running_workers = 0
        for worker_key in db["worker_statuses"]:
            status = db["worker_statuses"][worker_key]
            if status == WorkerStatus.RUNNING:
                log.info(f"{worker_key} is still indexing")
                running_workers += 1
            elif status == WorkerStatus.FINISHED:
                completed_workers += 1
        return TaskData(
            target_index=db["target_index"],
            task_id=db["task_id"],
            percent_successful=(completed_workers / total_workers) * 100,
            percent_completed=((total_workers - running_workers) / total_workers) * 100,
        )


def clear_state():
    """Forget about all running index jobs. Use with care."""

    with FileLock(lock_path), shelve.open(shelf_path, writeback=True) as db:
        for key in db:
            log.info("Deleting " + str(db[key]))
            del db[key]
    log.info("Cleared indexing state.")
