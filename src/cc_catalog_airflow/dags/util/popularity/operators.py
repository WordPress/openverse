import logging
from airflow.operators.python import PythonOperator

from util.popularity import sql

logger = logging.getLogger(__name__)


def drop_image_popularity_relations(dag, postgres_conn_id):
    return PythonOperator(
        task_id="drop_image_popularity_relations",
        python_callable=sql.drop_image_popularity_relations,
        op_args=[postgres_conn_id],
        dag=dag,
    )


def drop_image_popularity_functions(dag, postgres_conn_id):
    return PythonOperator(
        task_id="drop_image_popularity_functions",
        python_callable=sql.drop_image_popularity_functions,
        op_args=[postgres_conn_id],
        dag=dag,
    )


def create_image_popularity_metrics(dag, postgres_conn_id):
    return PythonOperator(
        task_id="create_image_popularity_metrics_table",
        python_callable=sql.create_image_popularity_metrics,
        op_args=[postgres_conn_id],
        dag=dag,
    )


def update_image_popularity_metrics(dag, postgres_conn_id):
    return PythonOperator(
        task_id="update_image_popularity_metrics_table",
        python_callable=sql.update_image_popularity_metrics,
        op_args=[postgres_conn_id],
        dag=dag,
    )


def create_image_popularity_percentile(dag, postgres_conn_id):
    return PythonOperator(
        task_id="create_image_popularity_percentile",
        python_callable=sql.create_image_popularity_percentile_function,
        op_args=[postgres_conn_id],
        dag=dag,
    )


def create_image_popularity_constants(dag, postgres_conn_id):
    return PythonOperator(
        task_id="create_image_popularity_constants_view",
        python_callable=sql.create_image_popularity_constants_view,
        op_args=[postgres_conn_id],
        dag=dag,
    )


def update_image_popularity_constants(dag, postgres_conn_id):
    return PythonOperator(
        task_id="update_image_popularity_constants_view",
        python_callable=sql.update_image_popularity_constants,
        op_args=[postgres_conn_id],
        dag=dag,
    )


def create_image_standardized_popularity(dag, postgres_conn_id):
    return PythonOperator(
        task_id="create_image_standardized_popularity",
        python_callable=sql.create_standardized_popularity_function,
        op_args=[postgres_conn_id],
        dag=dag,
    )


def create_image_view(dag, postgres_conn_id):
    return PythonOperator(
        task_id="create_image_view",
        python_callable=sql.create_image_view,
        op_args=[postgres_conn_id],
        dag=dag,
    )


def update_image_view(dag, postgres_conn_id):
    return PythonOperator(
        task_id="update_image_view",
        python_callable=sql.update_image_view,
        op_args=[postgres_conn_id],
        dag=dag,
    )
