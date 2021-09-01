import logging

from airflow.operators.python import PythonOperator
from util.popularity import sql


logger = logging.getLogger(__name__)


def drop_media_popularity_relations(
    dag,
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id="drop_media_popularity_relations",
        python_callable=sql.drop_media_popularity_relations,
        op_args=[postgres_conn_id, media_type],
        dag=dag,
    )


def drop_media_popularity_functions(
    dag,
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=f"drop_{media_type}_popularity_functions",
        python_callable=sql.drop_media_popularity_functions,
        op_args=[postgres_conn_id, media_type],
        dag=dag,
    )


def create_media_popularity_metrics(
    dag,
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=f"create_{media_type}_popularity_metrics_table",
        python_callable=sql.create_media_popularity_metrics,
        op_args=[postgres_conn_id, media_type],
        dag=dag,
    )


def update_media_popularity_metrics(
    dag,
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=f"update_{media_type}_popularity_metrics_table",
        python_callable=sql.update_media_popularity_metrics,
        op_args=[postgres_conn_id, media_type],
        dag=dag,
    )


def create_media_popularity_percentile(
    dag,
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=f"create_{media_type}_popularity_percentile",
        python_callable=sql.create_media_popularity_percentile_function,
        op_args=[postgres_conn_id, media_type],
        dag=dag,
    )


def create_media_popularity_constants(
    dag,
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=f"create_{media_type}_popularity_constants_view",
        python_callable=sql.create_media_popularity_constants_view,
        op_args=[postgres_conn_id, media_type],
        dag=dag,
    )


def update_media_popularity_constants(
    dag,
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=f"update_{media_type}_popularity_constants_view",
        python_callable=sql.update_media_popularity_constants,
        op_args=[postgres_conn_id, media_type],
        dag=dag,
    )


def create_media_standardized_popularity(
    dag,
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=f"create_{media_type}_standardized_popularity",
        python_callable=sql.create_standardized_media_popularity_function,
        op_args=[postgres_conn_id, media_type],
        dag=dag,
    )


def create_db_view(dag, postgres_conn_id, media_type="image"):
    return PythonOperator(
        task_id=f"create_{media_type}_view",
        python_callable=sql.create_media_view,
        op_args=[postgres_conn_id, media_type],
        dag=dag,
    )


def update_db_view(dag, postgres_conn_id, media_type="image"):
    return PythonOperator(
        task_id=f"update_{media_type}_view",
        python_callable=sql.update_db_view,
        op_args=[postgres_conn_id, media_type],
        dag=dag,
    )
