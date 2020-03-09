from datetime import datetime
import os
import time

from airflow.models import DAG, DagBag
from airflow.models.taskinstance import TaskInstance
import psycopg2
import pytest

import loader_workflow

FILE_DIR = os.path.abspath(os.path.dirname(__file__))
POSTGRES_CONN_ID = os.getenv('TEST_CONN_ID')
POSTGRES_TEST_URI = os.getenv('AIRFLOW_CONN_POSTGRES_OPENLEDGER_TESTING')
TEST_ID = 'testing'
TEST_LOAD_TABLE = f'provider_image_data{TEST_ID}'


@pytest.fixture
def postgres_cursor():
    conn = psycopg2.connect(POSTGRES_TEST_URI)
    cur = conn.cursor()
    drop_command = f'DROP TABLE IF EXISTS {TEST_LOAD_TABLE}'
    cur.execute(drop_command)
    conn.commit()
    yield cur
    cur.execute(drop_command)
    cur.close()
    conn.commit()
    conn.close()


def test_dag_loads_with_no_errors(tmpdir):
    tmp_directory = str(tmpdir)
    dag_bag = DagBag(dag_folder=tmp_directory, include_examples=False)
    dag_bag.process_file(os.path.join(FILE_DIR, 'loader_workflow.py'))
    print(dag_bag.dags)
    assert len(dag_bag.import_errors) == 0
    assert len(dag_bag.dags) == 1


def test_stager_stages_file(tmpdir):
    tmp_directory = str(tmpdir)
    staging_subdirectory = loader_workflow.STAGING_SUBDIRECTORY
    identifier = TEST_ID
    test_tsv = 'test.tsv'
    path = tmpdir.join(test_tsv)
    path.write('')
    dag = DAG(
        dag_id='test_dag',
        start_date=datetime.strptime('2019-01-01', '%Y-%m-%d')
    )
    stager = loader_workflow._get_file_staging_operator(
        dag, tmp_directory, 0, identifier=identifier
    )
    stager_ti = TaskInstance(task=stager, execution_date=datetime.now())
    stager.execute(stager_ti.get_template_context())
    staged_path = tmpdir.join(staging_subdirectory, identifier, test_tsv)
    assert staged_path.check(file=1)


def test_stager_stages_older_file(tmpdir):
    tmp_directory = str(tmpdir)
    staging_subdirectory = loader_workflow.STAGING_SUBDIRECTORY
    identifier = TEST_ID
    test_one_tsv = 'test1.tsv'
    test_two_tsv = 'test2.tsv'
    path_one = tmpdir.join(test_one_tsv)
    path_one.write('')
    time.sleep(0.01)
    path_two = tmpdir.join(test_two_tsv)
    path_two.write('')
    dag = DAG(
        dag_id='test_dag',
        start_date=datetime.strptime('2019-01-01', '%Y-%m-%d')
    )
    stager = loader_workflow._get_file_staging_operator(
        dag, tmp_directory, 0, identifier=identifier
    )
    stager_ti = TaskInstance(task=stager, execution_date=datetime.now())
    stager.execute(stager_ti.get_template_context())
    staged_path = tmpdir.join(staging_subdirectory, identifier, test_one_tsv)
    assert staged_path.check(file=1)
    staged_path_two = tmpdir.join(
        staging_subdirectory, identifier, test_two_tsv
    )
    assert staged_path_two.check(file=0)
    assert path_one.check(file=0)
    assert path_two.check(file=1)


def test_stager_ignores_non_tsv(tmpdir):
    tmp_directory = str(tmpdir)
    staging_subdirectory = loader_workflow.STAGING_SUBDIRECTORY
    identifier = TEST_ID
    test = 't'
    path = tmpdir.join(test)
    path.write('')
    dag = DAG(
        dag_id='test_dag',
        start_date=datetime.strptime('2019-01-01', '%Y-%m-%d')
    )
    stager = loader_workflow._get_file_staging_operator(
        dag, tmp_directory, 0, identifier=identifier
    )
    stager_ti = TaskInstance(task=stager, execution_date=datetime.now())
    stager.execute(stager_ti.get_template_context())
    staged_path = tmpdir.join(staging_subdirectory, identifier, test)
    assert staged_path.check(file=0)
    assert path.check(file=1)


def test_table_creator_creates_table(postgres_cursor):
    dag = DAG(
        dag_id='test_dag',
        start_date=datetime.strptime('2019-01-01', '%Y-%m-%d')
    )
    postgres_conn_id = POSTGRES_CONN_ID
    identifier = TEST_ID
    creator = loader_workflow._get_table_creator_operator(
        dag, postgres_conn_id, identifier=identifier
    )
    creator_ti = TaskInstance(task=creator, execution_date=datetime.now())
    creator.execute(creator_ti.get_template_context())
    check_command = (
        f"SELECT EXISTS ("
        f"SELECT FROM pg_tables WHERE tablename='{TEST_LOAD_TABLE}');"
    )
    postgres_cursor.execute(check_command)
    check_result = postgres_cursor.fetchone()[0]
    print(check_result)
    assert check_result
