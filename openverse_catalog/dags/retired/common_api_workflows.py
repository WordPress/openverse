import logging
import os

import common.config as conf
from airflow import DAG
from airflow.operators.bash import BashOperator
from croniter import croniter


logging.basicConfig(
    format="%(asctime)s: [%(levelname)s - DAG Loader] %(message)s", level=logging.INFO
)

CRONTAB_STR = conf.CRONTAB_STR
SCRIPT = conf.SCRIPT
DAG_DEFAULT_ARGS = conf.DAG_DEFAULT_ARGS
DAG_VARIABLES = conf.DAG_VARIABLES


def load_dag_conf(source, DAG_VARIABLES):
    """Validate and load configuration variables"""
    logging.info(f"Loading configuration for {source}")
    logging.debug(f"DAG_VARIABLES: {DAG_VARIABLES}")
    dag_id = f"{source}_workflow"

    script_location = DAG_VARIABLES[source].get(SCRIPT)
    try:
        assert os.path.exists(script_location)
    except Exception as e:
        logging.warning(f"Invalid script location: {script_location}.  Error:  {e}")
        script_location = None

    crontab_str = DAG_VARIABLES[source].get(CRONTAB_STR)
    try:
        croniter(crontab_str)
    except Exception as e:
        logging.warning(f"Invalid crontab string: {crontab_str}. Error: {e}")
        crontab_str = None

    return script_location, dag_id, crontab_str


def create_dag(
    source, script_location, dag_id, crontab_str=None, default_args=DAG_DEFAULT_ARGS
):

    dag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        schedule_interval=crontab_str,
        catchup=False,
    )

    with dag:
        BashOperator(
            task_id=f"get_{source}_images",
            bash_command=f"python {script_location} --mode default",
        )

    return dag


for source in DAG_VARIABLES:
    script_location, dag_id, crontab_str = load_dag_conf(source, DAG_VARIABLES)
    if script_location:
        globals()[dag_id] = create_dag(source, script_location, dag_id, crontab_str)
