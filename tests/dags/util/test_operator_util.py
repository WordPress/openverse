from datetime import datetime, timedelta, timezone

import util.operator_util as op_util
from airflow import DAG
from airflow.models.taskinstance import TaskInstance


def dated(dag_date):
    print(dag_date)


def test_get_runner_operator_creates_valid_string():
    dag = DAG(dag_id="test_dag", start_date=datetime.strptime("2019-01-01", "%Y-%m-%d"))
    with dag:
        runner = op_util.get_runner_operator("test_source", "/test/script/location.py")
        expected_command = "python /test/script/location.py --mode default"
        assert runner.bash_command == expected_command


def test_get_dated_main_runner_handles_zero_shift(capsys):
    dag = DAG(dag_id="test_dag", start_date=datetime.strptime("2019-01-01", "%Y-%m-%d"))
    execution_date = datetime.strptime("2019-01-01", "%Y-%m-%d").replace(
        tzinfo=timezone.utc
    )
    main_func = dated
    with dag:
        runner = op_util.get_dated_main_runner_operator(main_func, timedelta(minutes=1))
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
        runner = op_util.get_dated_main_runner_operator(
            main_func, timedelta(minutes=1), day_shift=1
        )
        ti = TaskInstance(runner, execution_date)
        ti.run(ignore_task_deps=True, ignore_ti_state=True, test_mode=True)
        # main_func.assert_called_with('2018-12-31')
        # Mocking main_func causes errors because Airflow JSON-encodes it,
        # and MagicMock is not JSON-serializable.
        captured = capsys.readouterr()
        assert captured.out == "2018-12-31\n"
