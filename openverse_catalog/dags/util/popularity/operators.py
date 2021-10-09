import logging

from airflow.operators.python import PythonOperator
from util.popularity import sql


logger = logging.getLogger(__name__)


def drop_media_popularity_relations(
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id="drop_media_popularity_relations",
        python_callable=sql.drop_media_popularity_relations,
        op_args=[postgres_conn_id, media_type],
    )


def drop_media_popularity_functions(
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=f"drop_{media_type}_popularity_functions",
        python_callable=sql.drop_media_popularity_functions,
        op_args=[postgres_conn_id, media_type],
    )


def create_media_popularity_metrics(
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=f"create_{media_type}_popularity_metrics_table",
        python_callable=sql.create_media_popularity_metrics,
        op_args=[postgres_conn_id, media_type],
    )


def update_media_popularity_metrics(
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=f"update_{media_type}_popularity_metrics_table",
        python_callable=sql.update_media_popularity_metrics,
        op_args=[postgres_conn_id, media_type],
    )


def create_media_popularity_percentile(
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=f"create_{media_type}_popularity_percentile",
        python_callable=sql.create_media_popularity_percentile_function,
        op_args=[postgres_conn_id, media_type],
    )


def create_media_popularity_constants(
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=f"create_{media_type}_popularity_constants_view",
        python_callable=sql.create_media_popularity_constants_view,
        op_args=[postgres_conn_id, media_type],
    )


def update_media_popularity_constants(
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=f"update_{media_type}_popularity_constants_view",
        python_callable=sql.update_media_popularity_constants,
        op_args=[postgres_conn_id, media_type],
    )


def create_media_standardized_popularity(
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=f"create_{media_type}_standardized_popularity",
        python_callable=sql.create_standardized_media_popularity_function,
        op_args=[postgres_conn_id, media_type],
    )


def create_db_view(postgres_conn_id, media_type="image"):
    return PythonOperator(
        task_id=f"create_{media_type}_view",
        python_callable=sql.create_media_view,
        op_args=[postgres_conn_id, media_type],
    )


def update_db_view(postgres_conn_id, media_type="image"):
    return PythonOperator(
        task_id=f"update_{media_type}_view",
        python_callable=sql.update_db_view,
        op_args=[postgres_conn_id, media_type],
    )
