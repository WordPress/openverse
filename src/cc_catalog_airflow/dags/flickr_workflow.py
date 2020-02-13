from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from provider_api_scripts import flickr
from util.operator_util import get_log_operator


DAG_DEFAULT_ARGS = {
    'owner': 'data-eng-admin',
    'depends_on_past': False,
    'start_date': datetime(1970, 1, 1),
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=15),
}

DAG_ID = 'flickr_workflow'


def get_runner_operator(dag):
    return PythonOperator(
        task_id='pull_flickr_data',
        python_callable=flickr.main,
        op_args=['{{ ds }}'],
        depends_on_past=False,
        dag=dag
    )


def create_dag():
    dag = DAG(
        dag_id=DAG_ID,
        default_args=DAG_DEFAULT_ARGS,
        # It is important that we don't run the Flickr job in parallel;
        # Otherwise, we might blow through the rate limit
        concurrency=1,
        max_active_runs=1,
        # Flickr has a few images which claim to be uploaded at Unix
        # Timestamp 0 (1 Jan 1970)
        start_date=datetime(1970, 1, 1),
        schedule_interval='@daily',
        catchup=False,
    )

    with dag:
        start_task = get_log_operator(dag, DAG_ID, 'Starting')
        run_task = get_runner_operator(dag)
        end_task = get_log_operator(dag, DAG_ID, 'Finished')

        start_task >> run_task >> end_task

    return dag


globals()[DAG_ID] = create_dag()
