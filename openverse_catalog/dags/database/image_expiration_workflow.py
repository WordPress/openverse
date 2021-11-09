"""
This file configures the Apache Airflow DAG to expire the outdated images
in the image table by setting the removed_from_source column value to true
"""

import logging
import os
from datetime import datetime, timedelta

from airflow import DAG
from common.loader import operators, sql


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

DAG_ID = "image_expiration_workflow"
DB_CONN_ID = os.getenv("OPENLEDGER_CONN_ID", "postgres_openledger_testing")
CONCURRENCY = len(sql.OLDEST_PER_PROVIDER)

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
    concurrency=CONCURRENCY,
    max_active_runs=CONCURRENCY,
    postgres_conn_id=DB_CONN_ID,
):
    dag = DAG(
        dag_id=dag_id,
        default_args=args,
        concurrency=concurrency,
        max_active_runs=max_active_runs,
        catchup=False,
        schedule_interval=None,
        tags=["database"],
    )

    with dag:
        [
            operators.get_image_expiration_operator(postgres_conn_id, provider)
            for provider in sql.OLDEST_PER_PROVIDER
        ]

    return dag


globals()[DAG_ID] = create_dag()
