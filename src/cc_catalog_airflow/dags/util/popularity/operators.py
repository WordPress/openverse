import logging
from airflow.operators.python_operator import PythonOperator

from util.popularity import sql

logger = logging.getLogger(__name__)


def update_image_popularity_metrics(
        dag,
        postgres_conn_id
):
    return PythonOperator(
        task_id='update_image_popularity_metrics_table',
        python_callable=sql.update_image_popularity_metrics,
        op_args=[postgres_conn_id],
        dag=dag
    )


def update_image_popularity_constants(
        dag,
        postgres_conn_id
):
    return PythonOperator(
        task_id='update_image_popularity_constants_view',
        python_callable=sql.update_image_popularity_constants,
        op_args=[postgres_conn_id],
        dag=dag
    )
