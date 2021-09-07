import os

import common_api_workflows as caw
import util.config as conf
from airflow.models import DagBag


SCRIPT = conf.SCRIPT
CRONTAB_STR = conf.CRONTAB_STR
RESOURCES = os.path.join(conf.API_SCRIPT_PATH, "tests/resources")
FILE_DIR = os.path.abspath(os.path.dirname(__file__))


def test_dags_load_with_no_errors(tmpdir):
    tmp_directory = str(tmpdir)
    dag_bag = DagBag(dag_folder=tmp_directory, include_examples=False)
    dag_bag.process_file(os.path.join(FILE_DIR, "common_api_workflows.py"))
    assert len(dag_bag.import_errors) == 0


def test_create_dag_creates_correct_dependencies():
    dag = caw.create_dag("test_source", "test_script_location", "test_dag_id")
    start_id = "test_source_starting"
    run_id = "get_test_source_images"
    finish_id = "test_source_finished"
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
    crontab_str = "0 * * * *"
    dag = caw.create_dag(
        "test_source", "test_script_location", "test_dag_id", crontab_str=crontab_str
    )
    assert dag.schedule_interval == crontab_str


def test_load_dag_conf_handles_missing_script():
    source = "test_source"
    dag_variables = {"test_source": {}}
    script_location, dag_id, crontab_str = caw.load_dag_conf(source, dag_variables)
    assert script_location is None


def test_load_dag_conf_validates_script_location():
    source = "test_source"
    dag_variables = {"test_source": {SCRIPT: "/this/path/does/not/exist/hopefully"}}
    script_location, dag_id, crontab_str = caw.load_dag_conf(source, dag_variables)
    assert script_location is None


def test_load_dag_conf_returns_valid_script_location():
    source = "test_source"
    expected_script_location = os.path.join(RESOURCES, "FakeSource.py")
    dag_variables = {"test_source": {SCRIPT: expected_script_location}}
    script_location, dag_id, crontab_str = caw.load_dag_conf(source, dag_variables)
    assert script_location == expected_script_location


def test_load_dag_conf_validates_crontab_str():
    source = "test_source"
    bad_crontab_str = "abc123"
    dag_variables = {"test_source": {CRONTAB_STR: bad_crontab_str}}
    script_location, dag_id, crontab_str = caw.load_dag_conf(source, dag_variables)
    assert crontab_str is None


def test_load_dag_conf_handles_missing_crontab_str():
    source = "test_source"
    dag_variables = {"test_source": {}}
    script_location, dag_id, crontab_str = caw.load_dag_conf(source, dag_variables)
    assert crontab_str is None


def test_load_dag_conf_uses_proper_crontab_str():
    source = "test_source"
    good_crontab_str = "0 * * * *"
    dag_variables = {"test_source": {CRONTAB_STR: good_crontab_str}}
    script_location, dag_id, crontab_str = caw.load_dag_conf(source, dag_variables)
    assert crontab_str == good_crontab_str
