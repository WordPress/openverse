import logging

from airflow.operators.python import PythonOperator
from common.popularity import sql


logger = logging.getLogger(__name__)


DROP_MEDIA_POPULARITY_RELATIONS_TASK_ID = "drop_media_popularity_relations"
DROP_MEDIA_POPULARITY_FUNCTIONS_TASK_ID = "drop_media_popularity_functions"
CREATE_MEDIA_POPULARITY_METRICS_TASK_ID = "create_media_popularity_metrics_table"
UPDATE_MEDIA_POPULARITY_METRICS_TASK_ID = "update_media_popularity_metrics_table"
CREATE_MEDIA_POPULARITY_PERCENTILE_TASK_ID = "create_media_popularity_percentile"
CREATE_MEDIA_POPULARITY_CONSTANTS_TASK_ID = "create_media_popularity_constants_view"
CREATE_MEDIA_STANDARDIZED_POPULARITY_TASK_ID = "create_media_standardized_popularity"
CREATE_DB_VIEW_TASK_ID = "create_materialized_popularity_view"


def drop_media_popularity_relations(
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=DROP_MEDIA_POPULARITY_RELATIONS_TASK_ID,
        python_callable=sql.drop_media_popularity_relations,
        op_args=[postgres_conn_id, media_type],
    )


def drop_media_popularity_functions(
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=DROP_MEDIA_POPULARITY_FUNCTIONS_TASK_ID,
        python_callable=sql.drop_media_popularity_functions,
        op_args=[postgres_conn_id, media_type],
    )


def create_media_popularity_metrics(
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=CREATE_MEDIA_POPULARITY_METRICS_TASK_ID,
        python_callable=sql.create_media_popularity_metrics,
        op_args=[postgres_conn_id, media_type],
    )


def update_media_popularity_metrics(
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=UPDATE_MEDIA_POPULARITY_METRICS_TASK_ID,
        python_callable=sql.update_media_popularity_metrics,
        op_args=[postgres_conn_id, media_type],
    )


def create_media_popularity_percentile(
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=CREATE_MEDIA_POPULARITY_PERCENTILE_TASK_ID,
        python_callable=sql.create_media_popularity_percentile_function,
        op_args=[postgres_conn_id, media_type],
    )


def create_media_popularity_constants(
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=CREATE_MEDIA_POPULARITY_CONSTANTS_TASK_ID,
        python_callable=sql.create_media_popularity_constants_view,
        op_args=[postgres_conn_id, media_type],
    )


def create_media_standardized_popularity(
    postgres_conn_id,
    media_type="image",
):
    return PythonOperator(
        task_id=CREATE_MEDIA_STANDARDIZED_POPULARITY_TASK_ID,
        python_callable=sql.create_standardized_media_popularity_function,
        op_args=[postgres_conn_id, media_type],
    )


def create_db_view(postgres_conn_id, media_type="image"):
    return PythonOperator(
        task_id=CREATE_DB_VIEW_TASK_ID,
        python_callable=sql.create_media_view,
        op_args=[postgres_conn_id, media_type],
    )
