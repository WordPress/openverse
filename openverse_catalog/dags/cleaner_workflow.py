import logging
import os
from copy import deepcopy
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from util import config, operator_util, pg_cleaner


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

DAG_ID = "postgres_image_cleaner"
DB_CONN_ID = os.getenv("OPENLEDGER_CONN_ID", "postgres_openledger_testing")
PREFIX_LENGTH = 1
DESIRED_PREFIX_LENGTH = 3
CONCURRENCY = 8


def create_id_partitioned_cleaner_dag(
    dag_id=DAG_ID,
    prefix_length=PREFIX_LENGTH,
    postgres_conn_id=DB_CONN_ID,
    start_date=datetime(1970, 1, 1),
    concurrency=CONCURRENCY,
    default_args=config.DAG_DEFAULT_ARGS,
):
    args = deepcopy(default_args)
    args.update(start_date=start_date)
    dag = DAG(
        dag_id=dag_id,
        default_args=args,
        concurrency=concurrency,
        max_active_runs=concurrency,
        schedule_interval=None,
        start_date=start_date,
        catchup=False,
    )
    hex_prefixes = pg_cleaner.hex_counter(prefix_length)
    with dag:
        cleaner_list = [
            _get_pg_cleaner_operator(dag, prefix, postgres_conn_id)
            for prefix in hex_prefixes
        ]
        start_task = operator_util.get_log_operator(dag, dag.dag_id, "Started")
        end_task = operator_util.get_log_operator(dag, dag.dag_id, "Ended")
        start_task >> cleaner_list >> end_task
    return dag


def _get_pg_cleaner_operator(
    dag,
    prefix,
    postgres_conn_id,
    desired_length=DESIRED_PREFIX_LENGTH,
    delay=CONCURRENCY,
):
    task_id = f"clean_{prefix}"
    return PythonOperator(
        task_id=task_id,
        python_callable=pg_cleaner.clean_prefix_loop,
        op_args=[postgres_conn_id, prefix],
        op_kwargs={
            "desired_prefix_length": desired_length,
            "delay_minutes": delay,
        },
        depends_on_past=False,
        dag=dag,
    )


globals()[DAG_ID] = create_id_partitioned_cleaner_dag()
