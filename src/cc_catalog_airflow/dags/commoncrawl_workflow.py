from datetime import datetime,timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from commoncrawl_s3_syncer import SyncImageProviders
from util.operator_util import get_log_operator


DAG_DEFAULT_ARGS = {
    'owner': 'data-eng-admin',
    'depends_on_past': False,
    'start_date': datetime(2020, 1, 15, 16),
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(days=1)
}

DAG_ID="commoncrawl_workflow"


def get_runner_operator(dag):
    return PythonOperator(
        task_id="sync_commoncrawl",
        python_callable=SyncImageProviders.main,
        depends_on_past=False,
        dag=dag
    )


def create_dag():
    dag = DAG(
        dag_id=DAG_ID,
        default_args=DAG_DEFAULT_ARGS,
        start_date=datetime(2020, 1, 15, 16),
        schedule_interval="@monthly",
        catchup=False
    )

    with dag:
        start_task = get_log_operator(dag, DAG_ID, "Starting")
        run_task = get_runner_operator(dag)
        end_task = get_log_operator(dag, DAG_ID, "Finished")

        start_task >> run_task >> end_task

    return dag


globals()[DAG_ID] = create_dag()
