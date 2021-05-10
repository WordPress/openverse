from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule


def get_runner_operator(dag, source, script_location):
    return BashOperator(
        task_id=f'get_{source}_images',
        bash_command=f'python {script_location} --mode default',
        dag=dag
    )


def get_dated_main_runner_operator(
        dag,
        main_function,
        execution_timeout,
        day_shift=0,
        task_id='pull_image_data',
):
    args_str = f'{{{{ macros.ds_add(ds, -{day_shift}) }}}}'
    return PythonOperator(
        task_id=task_id,
        python_callable=main_function,
        op_args=[args_str],
        execution_timeout=execution_timeout,
        depends_on_past=False,
        dag=dag
    )


def get_main_runner_operator(dag, main_function):
    return PythonOperator(
        task_id='pull_image_data',
        python_callable=main_function,
        depends_on_past=False,
        dag=dag
    )


def get_log_operator(dag, source, status):
    return BashOperator(
        task_id=f'{source}_{status}',
        bash_command=f'echo {status} {source} workflow at $(date)',
        dag=dag
    )


def get_wait_till_done_operator(dag, task_id):
    return DummyOperator(
        task_id=task_id,
        trigger_rule=TriggerRule.ALL_DONE,
        dag=dag
    )
