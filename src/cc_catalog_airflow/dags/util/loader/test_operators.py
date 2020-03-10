from datetime import datetime
import time
import os

from airflow.models import DAG
from airflow.models.taskinstance import TaskInstance
import psycopg2
import pytest

from util.loader import operators


TEST_ID = 'testing'
POSTGRES_CONN_ID = os.getenv('TEST_CONN_ID')
POSTGRES_TEST_URI = os.getenv('AIRFLOW_CONN_POSTGRES_OPENLEDGER_TESTING')
TEST_LOAD_TABLE = f'provider_image_data{TEST_ID}'


# @pytest.fixture
# def postgres_cursor():
#     conn = psycopg2.connect(POSTGRES_TEST_URI)
#     cur = conn.cursor()
#     drop_command = f'DROP TABLE IF EXISTS {TEST_LOAD_TABLE}'
#     cur.execute(drop_command)
#     conn.commit()
#     yield cur
#     cur.execute(drop_command)
#     cur.close()
#     conn.commit()
#     conn.close()
# 
# 
# def test_table_creator_creates_table(postgres_cursor):
#     dag = DAG(
#         dag_id='test_dag',
#         start_date=datetime.strptime('2019-01-01', '%Y-%m-%d')
#     )
#     postgres_conn_id = POSTGRES_CONN_ID
#     identifier = TEST_ID
#     creator = operators.get_table_creator_operator(
#         dag, postgres_conn_id, identifier=identifier
#     )
#     creator_ti = TaskInstance(task=creator, execution_date=datetime.now())
#     creator.execute(creator_ti.get_template_context())
#     check_command = (
#         f"SELECT EXISTS ("
#         f"SELECT FROM pg_tables WHERE tablename='{TEST_LOAD_TABLE}');"
#     )
#     postgres_cursor.execute(check_command)
#     check_result = postgres_cursor.fetchone()[0]
#     print(check_result)
#     assert check_result
