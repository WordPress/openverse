"""
This file configures the Apache Airflow DAG to expire the outdated images
in the image table by setting the removed_from_source column value to true
"""

from datetime import timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID
from common.loader import sql


DAG_ID = "image_expiration_workflow"
MAX_ACTIVE_TASKS = len(sql.OLDEST_PER_PROVIDER)

dag = DAG(
    dag_id=DAG_ID,
    default_args={
        **DAG_DEFAULT_ARGS,
        "retry_delay": timedelta(seconds=15),
        "execution_timeout": None,
    },
    max_active_tasks=MAX_ACTIVE_TASKS,
    max_active_runs=MAX_ACTIVE_TASKS,
    catchup=False,
    schedule_interval=None,
    tags=["database"],
)

with dag:
    for provider in sql.OLDEST_PER_PROVIDER:
        PythonOperator(
            task_id=f"expire_outdated_images_of_{provider}",
            python_callable=sql.expire_old_images,
            op_args=[POSTGRES_CONN_ID, provider],
        )
