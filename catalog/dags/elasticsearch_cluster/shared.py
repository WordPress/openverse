from airflow.decorators import task
from airflow.models.connection import Connection
from airflow.models.xcom_arg import XComArg

from common.constants import Environment


@task
def get_es_host(environment: Environment) -> XComArg:
    conn = Connection.get_connection_from_secrets(f"elasticsearch_http_{environment}")
    return conn.host
