from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from provider_api_scripts import phylopic
from util.operator_util import get_log_operator


DAG_DEFAULT_ARGS = {
    "owner": "data-eng-admin",
    "depends_on_past": False,
    "start_date": datetime(2011, 1, 1),
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=15),
}

DAG_ID = "phylopic_workflow"


def get_runner_operator(dag):
    return PythonOperator(
        task_id="pull_phylopic_data",
        python_callable=phylopic.main,
        op_args=["{{ ds }}"],
        depends_on_past=False,
        dag=dag,
    )


def create_dag():
    dag = DAG(
        dag_id=DAG_ID,
        default_args=DAG_DEFAULT_ARGS,
        concurrency=1,
        max_active_runs=1,
        start_date=datetime(2011, 1, 1),
        schedule_interval="@daily",
        catchup=False,
    )

    with dag:
        start_task = get_log_operator(dag, DAG_ID, "Starting")
        run_task = get_runner_operator(dag)
        end_task = get_log_operator(dag, DAG_ID, "Finished")

        start_task >> run_task >> end_task

    return dag


globals()[DAG_ID] = create_dag()
