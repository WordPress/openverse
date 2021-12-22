"""
This file configures the Apache Airflow DAG to expire the outdated images
in the image table by setting the removed_from_source column value to true
"""

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from common.loader import sql


DAG_ID = "image_expiration_workflow"
DB_CONN_ID = os.getenv("OPENLEDGER_CONN_ID", "postgres_openledger_testing")
MAX_ACTIVE_TASKS = len(sql.OLDEST_PER_PROVIDER)

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
        tags=["database"],
    )

    with dag:
        for provider in sql.OLDEST_PER_PROVIDER:
            PythonOperator(
                task_id=f"expire_outdated_images_of_{provider}",
                python_callable=sql.expire_old_images,
                op_args=[postgres_conn_id, provider],
            )

    return dag


globals()[DAG_ID] = create_dag()
