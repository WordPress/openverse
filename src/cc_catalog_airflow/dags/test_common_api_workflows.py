from datetime import datetime
import os
import subprocess

from airflow.models import DagBag

import common_api_workflows

subprocess.call(['airflow', 'resetdb', '-y'])


def test_dags_load_with_no_errors():
    dag_bag = DagBag(include_examples=False)
    dag_bag.process_file('common_api_workflows.py')
    assert len(dag_bag.import_errors) == 0


def test_create_dag_creates_correct_dependencies():
    dag = common_api_workflows.create_dag(
        'test_source',
        'test_script_location',
        'test_dag_id'
    )
    start_id = 'test_source_starting'
    run_id = 'get_test_source_images'
    finish_id = 'test_source_finished'
    start_task = dag.get_task(start_id)
    assert start_task.upstream_task_ids == set()
    assert start_task.downstream_task_ids == set([run_id])
    run_task = dag.get_task(run_id)
    assert run_task.upstream_task_ids == set([start_id])
    assert run_task.downstream_task_ids == set([finish_id])
    finish_task = dag.get_task(finish_id)
    assert finish_task.upstream_task_ids == set([run_id])
    assert finish_task.downstream_task_ids == set()


def test_create_dag_adds_schedule_interval():
    cron_str = '0 * * * *'
    dag = common_api_workflows.create_dag(
        'test_source',
        'test_script_location',
        'test_dag_id',
        cron_str=cron_str
    )
    assert dag.schedule_interval == cron_str
