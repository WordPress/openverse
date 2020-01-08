import os
import sys
from airflow import DAG
from datetime import datetime
import util.operator_util as o


def test_get_runner_operator_creates_valid_string():
    dag = DAG(
        dag_id='test_dag',
        start_date=datetime.strptime('2019-01-01', '%Y-%m-%d')
    )
    runner = o.get_runner_operator(
        dag, 'test_source', '/test/script/location.py'
    )
    expected_command = 'python /test/script/location.py --mode default'
    assert runner.bash_command == expected_command
