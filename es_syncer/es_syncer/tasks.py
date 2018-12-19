import logging
import datetime as dt
from enum import Enum
from multiprocessing import Process
from es_syncer.indexer import elasticsearch_connect, TableIndexer
from es_syncer.ingest import get_upstream_updates


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
        pass

    def list_task_statuses(self):
        self._prune_old_tasks()
        results = []
        for _id, task in self.id_task.items():
            percent_completed = self.id_progress[_id].value
            active = task.is_alive()
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


class Task(Process):
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
        # Set of tasks that require us to instantiate the table indexer.
        indexing_required = {TaskTypes.REINDEX, TaskTypes.UPDATE_INDEX}
        # Map task types to actions.
        if self.task_type in indexing_required:
            elasticsearch = elasticsearch_connect()
            indexer = TableIndexer(
                elasticsearch, self.model, self.progress, self.finish_time
            )
            if self.task_type == TaskTypes.REINDEX:
                indexer.reindex(self.model)
            elif self.task_type == TaskTypes.UPDATE_INDEX:
                indexer.update(self.model, self.since_date)
        elif self.task_type == TaskTypes.INGEST_UPSTREAM:
            get_upstream_updates(self.model, self.progress, self.finish_time)
        logging.info('Task {} exited.'.format(self.task_id))


class TaskTypes(Enum):
    # Completely reindex all data for a given model.
    REINDEX = 0
    # Reindex updates to a model from the database since a certain date.
    UPDATE_INDEX = 1
    # Download the latest copy of the data from the intermediary database.
    INGEST_UPSTREAM = 2
