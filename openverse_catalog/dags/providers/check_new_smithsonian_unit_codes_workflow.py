"""
This file configures the Apache Airflow DAG to alert regarding new
smithsonian unit codes which are not seen in the SMITHSONIAN_SUB_PROVIDERS
dictionary
"""

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from common.loader import smithsonian_unit_codes


DAG_ID = "check_new_smithsonian_unit_codes_workflow"
DB_CONN_ID = os.getenv("OPENLEDGER_CONN_ID", "postgres_openledger_testing")
MAX_ACTIVE_TASKS = 5

DAG_DEFAULT_ARGS = {
    "owner": "data-eng-admin",
    "depends_on_past": False,
    "start_date": datetime(2020, 1, 15),
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(seconds=15),
    "schedule_interval": None,
}


def create_dag(
    dag_id=DAG_ID,
    args=DAG_DEFAULT_ARGS,
    max_active_tasks=MAX_ACTIVE_TASKS,
    max_active_runs=MAX_ACTIVE_TASKS,
    postgres_conn_id=DB_CONN_ID,
):
    dag = DAG(
        dag_id=dag_id,
        default_args=args,
        max_active_tasks=max_active_tasks,
        max_active_runs=max_active_runs,
        catchup=False,
        schedule_interval=None,
        tags=["provider-metadata"],
    )

    with dag:
        PythonOperator(
            task_id="check_new_smithsonian_unit_codes",
            python_callable=smithsonian_unit_codes.alert_unit_codes_from_api,
            op_args=[postgres_conn_id],
        )

    return dag


globals()[DAG_ID] = create_dag()
