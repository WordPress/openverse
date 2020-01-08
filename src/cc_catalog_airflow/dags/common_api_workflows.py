import logging
import os

from airflow import DAG
from croniter import croniter

import util.config as conf
from util.operator_util import get_runner_operator, get_log_operator

logging.basicConfig(
    format='%(asctime)s: [%(levelname)s - DAG Loader] %(message)s',
    level=logging.INFO)

CRONTAB_STR = conf.CRONTAB_STR
SCRIPT = conf.SCRIPT
dag_default_args = conf.dag_default_args
dag_variables = conf.dag_variables


def load_dag_conf(source, dag_variables):
    """Validate and load configuration variables"""
    logging.info('Loading configuration for {}'.format(source))
    logging.debug('dag_variables: {}'.format(dag_variables))
    dag_id = '{}_workflow'.format(source)

    script_location = dag_variables[source].get(SCRIPT)
    try:
        assert os.path.exists(script_location)
    except Exception as e:
        logging.warning(
            'Invalid script location: {}.  Error:  {}'
            .format(script_location, e)
        )
        script_location = None

    crontab_str = dag_variables[source].get(CRONTAB_STR)
    try:
        croniter(crontab_str)
    except Exception as e:
        logging.warning(
            'Invalid crontab string: {}. Error: {}'.format(crontab_str, e)
        )
        crontab_str = None

    return script_location, dag_id, crontab_str


def create_dag(
        source,
        script_location,
        dag_id,
        crontab_str=None,
        default_args=dag_default_args):

    dag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        schedule_interval=crontab_str,
        catchup=False
    )

    with dag:
        start_task = get_log_operator(dag, source, 'starting')
        run_task = get_runner_operator(dag, source, script_location)
        end_task = get_log_operator(dag, source, 'finished')

        start_task >> run_task >> end_task

    return dag


for source in dag_variables:
    script_location, dag_id, crontab_str = load_dag_conf(source, dag_variables)
    if script_location:
        globals()[dag_id] = create_dag(
            source,
            script_location,
            dag_id,
            crontab_str
        )
