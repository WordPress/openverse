"""
This file configures the Apache Airflow DAG to alert regarding new
smithsonian unit codes which are not seen in the SMITHSONIAN_SUB_PROVIDERS
dictionary
"""

from datetime import datetime, timedelta
import logging
from airflow import DAG

from util.loader import operators


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

DAG_ID = 'check_new_smithsonian_unit_codes_workflow'

DAG_DEFAULT_ARGS = {
    'owner': 'data-eng-admin',
    'depends_on_past': False,
    'start_date': datetime(2020, 1, 15),
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(seconds=15),
    'schedule_interval': None,
}


def create_dag(
        dag_id=DAG_ID,
        args=DAG_DEFAULT_ARGS
):
    dag = DAG(
        dag_id=dag_id,
        default_args=args,
        schedule_interval=None
    )

    with dag:
        check_unit_codes = operators.get_smithsonian_unit_code_operator(
          dag
        )
        found_new_unit_codes = operators.found_new_unit_codes_switch(
          dag
        )
        no_new_unit_codes = operators.no_new_unit_codes_switch(
          dag
        )

        found_new_unit_codes.set_upstream(check_unit_codes)
        no_new_unit_codes.set_upstream(check_unit_codes)

    return dag


globals()[DAG_ID] = create_dag()
