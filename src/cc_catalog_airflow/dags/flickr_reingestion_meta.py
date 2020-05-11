from datetime import datetime, timedelta
import logging

from airflow import DAG
from airflow.operators.subdag_operator import SubDagOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.helpers import cross_downstream
from airflow.utils.trigger_rule import TriggerRule

from provider_api_scripts import flickr
from util.operator_util import get_log_operator
from util.dag_factory import create_provider_api_workflow

logging.basicConfig(
    format='%(asctime)s: [%(levelname)s - DAG Loader] %(message)s',
    level=logging.DEBUG)


logger = logging.getLogger(__name__)

DAG_ID = 'flickr_reingestion_meta'

DAG_DEFAULT_ARGS = {
    'owner': 'data-eng-admin',
    'depends_on_past': False,
    'start_date': datetime(1970, 1, 1),
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=15),
}

ONE_MONTH_LIST_LENGTH = 24
THREE_MONTH_LIST_LENGTH = 36
SIX_MONTH_LIST_LENGTH = 48


def get_reingestion_day_lists(
        n1=ONE_MONTH_LIST_LENGTH,
        n3=THREE_MONTH_LIST_LENGTH,
        n6=SIX_MONTH_LIST_LENGTH
):
    L1 = [i + 1 for i in range(n1)]
    L3 = [3 * (i + 1) + n1 for i in range(n3)]
    L6 = [6 * (i + 1) + 3 * n3 + n1 for i in range(n6)]
    # We approximate a month by 30 days for simplicity
    reingestion_day_lists = (
        [m * 30 for m in L1],
        [m * 30 for m in L3],
        [m * 30 for m in L6],
    )
    return reingestion_day_lists


def get_wait_task(dag, task_id):
    return DummyOperator(
        task_id=task_id,
        trigger_rule=TriggerRule.ALL_DONE,
        dag=dag
    )


def get_flickr_workflow_operator(dag, child_name, day_shift):
    dag_id = f'{dag.dag_id}.{child_name}'
    return SubDagOperator(
        task_id=child_name,
        subdag=create_provider_api_workflow(
            dag_id,
            flickr.main,
            start_date=datetime(1970, 1, 1),
            concurrency=1,
            schedule_string='@daily',
            dated=True,
            day_shift=day_shift
        ),
        trigger_rule=TriggerRule.ALL_DONE
    )


dag = DAG(
    dag_id=DAG_ID,
    default_args=DAG_DEFAULT_ARGS,
    concurrency=1,
    max_active_runs=1,
    schedule_interval='@daily',
    catchup=False
)

reingestion_days = get_reingestion_day_lists()

with dag:
    # start_task = get_log_operator(dag, DAG_ID, 'Starting')
    current_day_ingest = get_flickr_workflow_operator(dag, 'ingest_0', 0)
    every_month_reingest = [
        get_flickr_workflow_operator(dag, f'reingest_{d}', d)
        for d in reingestion_days[0]
    ]
    wait_for_every_month = get_wait_task(
        dag, 'wait_for_every_month_reingest'
    )
    every_three_month_reingest = [
        get_flickr_workflow_operator(dag, f'reingest_{d}', d)
        for d in reingestion_days[1]
    ]
    wait_for_every_three_month = get_wait_task(
        dag, 'wait_for_every_three_month_reingest'
    )
    every_six_month_reingest = [
        get_flickr_workflow_operator(dag, f'reingest_{d}', d)
        for d in reingestion_days[2]
    ]
    end_task = get_log_operator(dag, DAG_ID, 'Finished')

    current_day_ingest >> every_month_reingest + [end_task]
    cross_downstream(
        every_month_reingest,
        [
            wait_for_every_month,
            end_task
        ]
    )
    wait_for_every_month >> every_three_month_reingest
    cross_downstream(
        every_three_month_reingest,
        [
            wait_for_every_three_month,
            end_task
        ]
    )
    wait_for_every_three_month >> every_six_month_reingest >> end_task
