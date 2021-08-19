"""
This file configures the Apache Airflow DAG to update the database table to
reflect appropriate Smithsonian sub provider names in the source field
"""

from datetime import datetime, timedelta
import logging
import os
import util.operator_util as ops
from airflow import DAG

from util.loader import operators


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

DAG_ID = 'smithsonian_sub_provider_update_workflow'
DB_CONN_ID = os.getenv('OPENLEDGER_CONN_ID', 'postgres_openledger_testing')
CONCURRENCY = 5

DAG_DEFAULT_ARGS = {
    'owner': 'data-eng-admin',
    'depends_on_past': False,
    'start_date': datetime(2020, 1, 15),
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(seconds=15),
    'schedule_interval': None,
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
    )

    with dag:
        start_task = ops.get_log_operator(dag, dag.dag_id, 'Starting')
        run_task = operators.get_smithsonian_sub_provider_update_operator(
          dag,
          postgres_conn_id
        )
        end_task = ops.get_log_operator(dag, dag.dag_id, 'Finished')

        start_task >> run_task >> end_task

    return dag


globals()[DAG_ID] = create_dag()
