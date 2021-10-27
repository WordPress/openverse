import os
from datetime import datetime, timedelta, timezone

import common_api_workflows as caw
import util.config as conf
import util.dag_factory
from airflow import DAG
from airflow.models import DagBag, TaskInstance


SCRIPT = conf.SCRIPT
CRONTAB_STR = conf.CRONTAB_STR
FILE_DIR = os.path.abspath(os.path.dirname(__file__))


def dated(dag_date):
    print(dag_date)


def test_get_dated_main_runner_handles_zero_shift(capsys):
    dag = DAG(dag_id="test_dag", start_date=datetime.strptime("2019-01-01", "%Y-%m-%d"))
    execution_date = datetime.strptime("2019-01-01", "%Y-%m-%d").replace(
        tzinfo=timezone.utc
    )
    main_func = dated
    with dag:
        runner = util.dag_factory.get_dated_main_runner_operator(
            main_func, timedelta(minutes=1)
        )
        ti = TaskInstance(runner, execution_date)
        ti.run(ignore_task_deps=True, ignore_ti_state=True, test_mode=True)
        # main_func.assert_called_with('2019-01-01')
        # Mocking main_func causes errors because Airflow JSON-encodes it,
        # and MagicMock is not JSON-serializable.
        captured = capsys.readouterr()
        assert captured.out == "2019-01-01\n"


def test_get_dated_main_runner_handles_day_shift(capsys):
    dag = DAG(dag_id="test_dag", start_date=datetime.strptime("2019-01-01", "%Y-%m-%d"))
    execution_date = datetime.strptime("2019-01-01", "%Y-%m-%d").replace(
        tzinfo=timezone.utc
    )
    main_func = dated
    with dag:
        runner = util.dag_factory.get_dated_main_runner_operator(
            main_func, timedelta(minutes=1), day_shift=1
        )
        ti = TaskInstance(runner, execution_date)
        ti.run(ignore_task_deps=True, ignore_ti_state=True, test_mode=True)
        # main_func.assert_called_with('2018-12-31')
        # Mocking main_func causes errors because Airflow JSON-encodes it,
        # and MagicMock is not JSON-serializable.
        captured = capsys.readouterr()
        assert captured.out == "2018-12-31\n"


def test_dags_load_with_no_errors(tmpdir):
    tmp_directory = str(tmpdir)
    dag_bag = DagBag(dag_folder=tmp_directory, include_examples=False)
    dag_bag.process_file(os.path.join(FILE_DIR, "../../dags/common_api_workflows.py"))
    assert len(dag_bag.import_errors) == 0


def test_create_dag_creates_correct_dependencies():
    dag = caw.create_dag("test_source", "test_script_location", "test_dag_id")
    run_id = "get_test_source_images"
    run_task = dag.get_task(run_id)
    assert run_task.downstream_task_ids == set()


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
    expected_script_location = os.path.join(
        os.path.join(FILE_DIR, "provider_api_scripts/resources"), "FakeSource.py"
    )
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
