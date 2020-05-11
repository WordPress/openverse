from copy import deepcopy
from airflow import DAG
import util.operator_util as ops
import util.config as conf


def create_provider_api_workflow(
        dag_id,
        main_function,
        default_args=conf.DAG_DEFAULT_ARGS,
        start_date=None,
        concurrency=1,
        schedule_string='@daily',
        dated=True,
        day_shift=0
):
    args = deepcopy(default_args)
    args.update(start_date=start_date)
    print(args)
    dag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        concurrency=concurrency,
        max_active_runs=concurrency,
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
