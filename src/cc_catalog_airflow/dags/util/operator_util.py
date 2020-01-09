from airflow.operators.bash_operator import BashOperator


def get_runner_operator(dag, source, script_location):
    return BashOperator(
        task_id='get_{}_images'.format(source),
        bash_command='python {} --mode default'.format(script_location),
        dag=dag
    )


def get_log_operator(dag, source, status):
    return BashOperator(
        task_id='{}_{}'.format(source, status),
        bash_command='echo {} {} workflow at $(date)'.format(status, source),
        dag=dag
    )
