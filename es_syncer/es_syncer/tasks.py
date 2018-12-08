import logging
import os
import datetime as dt
from enum import Enum
from multiprocessing import Process
from es_syncer.sync import elasticsearch_connect, TableIndexer
from collections import OrderedDict


class TaskTracker:
    def __init__(self):
        self.id_task = {}
        self.id_action = {}
        self.id_progress = {}
        self.id_finish_time = {}

    def add_task(self, task, task_id, action, progress, finish_time):
        self._prune_old_tasks()
        self.id_task[task_id] = task
        self.id_action[task_id] = action
        self.id_progress[task_id] = progress
        self.id_finish_time[task_id] = finish_time
        return task_id

    def _prune_old_tasks(self):
        # TODO Delete old and irrelevant tasks from the TaskTracker
        pass

    def list_task_statuses(self):
        results = []
        for _id, task in self.id_task.items():
            percent_completed = self.id_progress[_id].value
            active = process_alive(task.pid)
            finish_time = self.id_finish_time[_id].value
            results.append({
                'task_id': _id,
                'active': active,
                'action': self.id_action[_id],
                'progress': percent_completed,
                'error': percent_completed < 100 and not active,
                'finish_time': finish_time
            })
        sorted_results = sorted(
            results,
            key=lambda x: x['finish_time']
        )

        # Convert date to a readable format
        for idx, task in enumerate(sorted_results):
            finish_time = task['finish_time']
            if finish_time != 0.0:
                sorted_results[idx]['finish_time'] =\
                    str(dt.datetime.utcfromtimestamp(finish_time))
            else:
                sorted_results[idx]['finish_time'] = None

        return sorted_results


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


def process_alive(pid: int):
    active = True
    if os.path.isdir('/proc/{}'.format(pid)):
        with open('/proc/{}'.format(pid) + '/status') as procfile:
            if 'zombie' in procfile.read():
                active = False
    else:
        active = False
    return active


class IndexingTaskTypes(Enum):
    REINDEX = 0
    UPDATE = 1
