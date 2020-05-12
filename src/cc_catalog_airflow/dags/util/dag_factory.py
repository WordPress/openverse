from copy import deepcopy
from datetime import timedelta
import logging
from airflow import DAG
from airflow.operators.subdag_operator import SubDagOperator
from airflow.utils.helpers import cross_downstream
from airflow.utils.trigger_rule import TriggerRule
import util.operator_util as ops
import util.config as conf

logger = logging.getLogger(__name__)


def create_provider_api_workflow(
        dag_id,
        main_function,
        default_args=conf.DAG_DEFAULT_ARGS,
        start_date=None,
        concurrency=1,
        schedule_string='@daily',
        dated=True,
        day_shift=0,
        dagrun_timeout=timedelta(minutes=30),
):
    args = deepcopy(default_args)
    args.update(start_date=start_date)
    print(args)
    dag = DAG(
        dag_id=dag_id,
        default_args=args,
        concurrency=concurrency,
        max_active_runs=concurrency,
        dagrun_timeout=dagrun_timeout,
        start_date=start_date,
        schedule_interval=schedule_string,
        catchup=False,
    )

    with dag:
        start_task = ops.get_log_operator(dag, dag_id, 'Starting')
        if dated:
            run_task = ops.get_dated_main_runner_operator(
                dag, main_function, day_shift=day_shift
            )
        else:
            run_task = ops.get_runner_operator(dag, main_function)
        end_task = ops.get_log_operator(dag, dag_id, 'Finished')

        start_task >> run_task >> end_task

    return dag


def create_day_partitioned_reingestion_meta_dag(
        dag_id,
        main_function,
        reingestion_day_list_list,
        start_date=None,
        concurrency=1,
        default_args=conf.DAG_DEFAULT_ARGS,
        dagrun_timeout=timedelta(hours=23)
):
    args = deepcopy(default_args)
    args.update(start_date=start_date)
    print(args)
    dag = DAG(
        dag_id=dag_id,
        default_args=args,
        concurrency=concurrency,
        max_active_runs=concurrency,
        dagrun_timeout=dagrun_timeout,
        schedule_interval='@daily',
        start_date=start_date,
        catchup=False,
    )
    if reingestion_day_list_list[0] != [0]:
        reingestion_day_list_list = [[0]] + reingestion_day_list_list
    with dag:
        operator_list_list = [
            [
                _get_daily_provider_api_workflow_operator(
                    dag,
                    f'ingest_{d}',
                    main_function,
                    start_date=start_date,
                    concurrency=concurrency,
                    day_shift=d
                )
                for d in L
            ] for L in reingestion_day_list_list
        ]
        end_task = ops.get_log_operator(dag, dag_id, 'Finished')
        for i in range(len(operator_list_list) - 1):
            wait_operator = ops.get_wait_till_done_operator(
                dag,
                f'wait_L{i}'
            )
            cross_downstream(
                operator_list_list[i],
                [
                    wait_operator,
                    end_task
                ]
            )
            wait_operator >> operator_list_list[i + 1]
            operator_list_list[-1] >> end_task

    return dag


def _get_daily_provider_api_workflow_operator(
        dag,
        child_name,
        main_function,
        start_date=None,
        concurrency=1,
        day_shift=0
):
    dag_id = f'{dag.dag_id}.{child_name}'
    DAILY = '@daily'
    return SubDagOperator(
        task_id=child_name,
        subdag=create_provider_api_workflow(
            dag_id,
            main_function,
            start_date=start_date,
            concurrency=concurrency,
            schedule_string=DAILY,
            dated=True,
            day_shift=day_shift
        ),
        trigger_rule=TriggerRule.ALL_DONE
    )
