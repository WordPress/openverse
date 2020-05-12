from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.trigger_rule import TriggerRule


def get_runner_operator(dag, source, script_location):
    return BashOperator(
        task_id='get_{}_images'.format(source),
        bash_command='python {} --mode default'.format(script_location),
        dag=dag
    )


def get_dated_main_runner_operator(dag, main_function, day_shift=0):
    args_str = f'{{{{ macros.ds_add(ds, -{day_shift}) }}}}'
    return PythonOperator(
        task_id='pull_image_data',
        python_callable=main_function,
        op_args=[args_str],
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
        task_id='{}_{}'.format(source, status),
        bash_command='echo {} {} workflow at $(date)'.format(status, source),
        dag=dag
    )


def get_wait_till_done_task(dag, task_id):
    return DummyOperator(
        task_id=task_id,
        trigger_rule=TriggerRule.ALL_DONE,
        dag=dag
    )
