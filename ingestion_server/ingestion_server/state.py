import shelve
import datetime
import enum
import logging as log
from filelock import FileLock
"""
Indexing is distributed across multiple independent hosts. We don't want to 
"go live" in production with the newly indexed data until all of the indexing 
workers have finished their tasks. 
"""


class WorkerStatus(enum):
    RUNNING = 0
    FINISHED = 1


def register_indexing_job(workers):
    """
    Track the hosts that are running indexing jobs.
    :param workers:
    :return:
    """
    with FileLock('lock'), shelve.open('db', writeback=True) as db:
        for worker_url in workers:
            db[worker_url] = WorkerStatus.RUNNING


def worker_finished(worker_url):
    """
    The scheduler received a notification indicating an indexing worker has
    finished its task.
    :param worker_url: The private DNS of the worker.
    :return: True if all workers have finished indexing else False
    """
    with FileLock('lock'), shelve.open('db', writeback=True) as db:
        try:
            db[worker_url] = WorkerStatus.FINISHED
        except KeyError:
            log.error(
                'An indexer worker notified us it finished its task, but '
                'no indexing job has been scheduled.'
            )
        all_workers_finished = True
        for worker_key in db:
            if db[worker_key] == WorkerStatus.RUNNING:
                all_workers_finished = False
        return all_workers_finished
