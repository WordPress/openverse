import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from util.operator_util import get_log_operator
from util.tsv_cleaner import clean_tsv_directory

airflowHome = os.environ['AIRFLOW_HOME']

DAG_DEFAULT_ARGS = {
    'owner': 'data-eng-admin',
    'depends_on_past': False,
    'start_date': datetime(2020, 1, 15),
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(days=1)
}

DAG_ID = "sync_commoncrawl_workflow"

DEFAULT_OUTPUT_DIR = '/tmp'
TSV_SUBDIR = "common_crawl_tsvs/"

CRAWL_OUTPUT_DIR = os.path.join(
    os.environ.get("OUTPUT_DIR", DEFAULT_OUTPUT_DIR), TSV_SUBDIR
)


def get_creator_operator(dag):
    return PythonOperator(
        task_id="create_tsv_directory",
        python_callable=os.makedirs,
        op_args=[CRAWL_OUTPUT_DIR],
        op_kwargs={'exist_ok': True},
        depends_on_past=False,
        dag=dag,
    )


def get_syncer_operator(dag):
    return BashOperator(
        task_id="sync_commoncrawl_workflow",
        bash_command=(
            f"python {airflowHome}/dags/"
            "commoncrawl_s3_syncer/SyncImageProviders.py"
        ),
        dag=dag,
        env={
            "S3_BUCKET": os.environ["S3_BUCKET"],
            "OUTPUT_DIR": CRAWL_OUTPUT_DIR,
            "AWS_ACCESS_KEY": os.environ["AWS_ACCESS_KEY"],
            "AWS_SECRET_KEY": os.environ["AWS_SECRET_KEY"],
        },
    )


def get_cleaner_operator(dag):
    return PythonOperator(
        task_id="clean_commoncrawl_tsvs",
        python_callable=clean_tsv_directory,
        op_args=[CRAWL_OUTPUT_DIR],
        depends_on_past=False,
        dag=dag
    )


def get_deleter_operator(dag):
    return PythonOperator(
        task_id="empty_tsv_directory",
        python_callable=_empty_tsv_dir,
        op_args=[CRAWL_OUTPUT_DIR],
        depends_on_past=False,
        dag=dag
    )


def _empty_tsv_dir(tsv_directory):
    for tsv in os.listdir(tsv_directory):
        os.remove(os.path.join(tsv_directory, tsv))


def create_dag():
    dag = DAG(
        dag_id=DAG_ID,
        default_args=DAG_DEFAULT_ARGS,
        start_date=datetime(2020, 1, 15),
        schedule_interval="0 16 15 * *",
        catchup=False
    )

    with dag:
        start_task = get_log_operator(dag, DAG_ID, "Starting")
        create_dir_task = get_creator_operator(dag)
        sync_tsvs_task = get_syncer_operator(dag)
        clean_tsvs_task = get_cleaner_operator(dag)
        empty_dir_task = get_deleter_operator(dag)
        end_task = get_log_operator(dag, DAG_ID, "Finished")

        (
            start_task
            >> create_dir_task
            >> sync_tsvs_task
            >> clean_tsvs_task
            >> empty_dir_task
            >> end_task
        )
    return dag


globals()[DAG_ID] = create_dag()
