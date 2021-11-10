import logging

from airflow.operators.python import PythonOperator
from common.loader import smithsonian_unit_codes, sql


logger = logging.getLogger(__name__)

TIMESTAMP_TEMPLATE = "{{ ts_nodash }}"


def get_smithsonian_unit_code_operator(postgres_conn_id):
    return PythonOperator(
        task_id="check_new_smithsonian_unit_codes",
        python_callable=smithsonian_unit_codes.alert_unit_codes_from_api,
        op_args=[postgres_conn_id],
    )


def get_image_expiration_operator(postgres_conn_id, provider):
    return PythonOperator(
        task_id=f"expire_outdated_images_of_{provider}",
        python_callable=sql.expire_old_images,
        op_args=[postgres_conn_id, provider],
    )
