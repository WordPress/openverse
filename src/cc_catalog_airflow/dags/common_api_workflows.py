from airflow import DAG
from croniter import croniter
from util.config import dag_default_args, dag_variables
from util.operator_util import get_runner_operator, get_log_operator


def create_dag(
        source,
        script_location,
        dag_id,
        cron_str=None,
        default_args=dag_default_args):

    dag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        schedule_interval=cron_str,
        catchup=False
    )

    with dag:
        start_task = get_log_operator(dag, source, 'starting')
        run_task = get_runner_operator(dag, source, script_location)
        end_task = get_log_operator(dag, source, 'finished')

        start_task >> run_task >> end_task

    return dag


for source in dag_variables:
    script_location = dag_variables[source]['script']
    dag_id = '{}_workflow'.format(source)
    cron_str = dag_variables[source].get('cron_str')

    globals()[dag_id] = create_dag(
        source,
        script_location,
        dag_id,
        cron_str
    )
