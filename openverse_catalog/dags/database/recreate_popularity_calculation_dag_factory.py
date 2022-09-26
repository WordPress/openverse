"""
This file generates Apache Airflow DAGs that, for the given media type,
completely wipe out the PostgreSQL relations and functions involved in
calculating our standardized popularity metric. It then recreates relations
and functions to make the calculation, and performs an initial calculation.
The results are available in the materialized view for that media type.

These DAGs are not on a schedule, and should only be run manually when new
SQL code is deployed for the calculation.
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID
from common.popularity import sql
from data_refresh.data_refresh_types import DATA_REFRESH_CONFIGS, DataRefresh


def create_recreate_popularity_calculation_dag(data_refresh: DataRefresh):
    media_type = data_refresh.media_type
    default_args = {
        **DAG_DEFAULT_ARGS,
        **data_refresh.default_args,
    }

    dag = DAG(
        dag_id=f"recreate_{media_type}_popularity_calculation",
        default_args=default_args,
        max_active_runs=1,
        schedule=None,
        catchup=False,
        doc_md=__doc__,
        tags=["database", "data_refresh"],
    )
    with dag:
        drop_relations = PythonOperator(
            task_id="drop_popularity_relations",
            python_callable=sql.drop_media_popularity_relations,
            op_kwargs={
                "postgres_conn_id": POSTGRES_CONN_ID,
                "media_type": media_type,
            },
            doc="Drop the existing popularity views and tables.",
        )

        drop_functions = PythonOperator(
            task_id="drop_popularity_functions",
            python_callable=sql.drop_media_popularity_functions,
            op_kwargs={
                "postgres_conn_id": POSTGRES_CONN_ID,
                "media_type": media_type,
            },
            doc="Drop the existing popularity functions.",
        )

        create_metrics_table = PythonOperator(
            task_id="create_popularity_metrics_table",
            python_callable=sql.create_media_popularity_metrics,
            op_kwargs={
                "postgres_conn_id": POSTGRES_CONN_ID,
                "media_type": media_type,
            },
            doc=(
                "Create the popularity metrics table, which stores popularity "
                "metrics and target percentiles per provider."
            ),
        )

        update_metrics_table = PythonOperator(
            task_id="update_popularity_metrics_table",
            python_callable=sql.update_media_popularity_metrics,
            op_kwargs={
                "postgres_conn_id": POSTGRES_CONN_ID,
                "media_type": media_type,
            },
            doc="Update the popularity metrics table with values for each provider.",
        )

        create_percentile_function = PythonOperator(
            task_id="create_popularity_percentile_function",
            python_callable=sql.create_media_popularity_percentile_function,
            op_kwargs={
                "postgres_conn_id": POSTGRES_CONN_ID,
                "media_type": media_type,
            },
            doc=(
                "Create the function for calculating popularity percentile values, "
                "used for calculating the popularity constants for each provider."
            ),
        )

        create_constants_view = PythonOperator(
            task_id="create_popularity_constants_view",
            python_callable=sql.create_media_popularity_constants_view,
            op_kwargs={
                "postgres_conn_id": POSTGRES_CONN_ID,
                "media_type": media_type,
            },
            execution_timeout=data_refresh.create_pop_constants_view_timeout,
            doc=(
                "Create the materialized view with popularity constants for each "
                "provider, using the percentile function."
            ),
        )

        create_popularity_function = PythonOperator(
            task_id="create_standardized_popularity_function",
            python_callable=sql.create_standardized_media_popularity_function,
            op_kwargs={
                "postgres_conn_id": POSTGRES_CONN_ID,
                "media_type": media_type,
            },
            doc=(
                "Create the function that calculates popularity data for a given "
                "record, standardizing across providers with the generated popularity "
                "constants."
            ),
        )

        create_matview = PythonOperator(
            task_id="create_materialized_popularity_view",
            python_callable=sql.create_media_view,
            op_kwargs={
                "postgres_conn_id": POSTGRES_CONN_ID,
                "media_type": media_type,
            },
            execution_timeout=data_refresh.create_materialized_view_timeout,
            doc=(
                "Create the materialized view containing standardized popularity data "
                "for all records."
            ),
        )

        (
            [drop_relations, drop_functions]
            >> create_metrics_table
            >> [update_metrics_table, create_percentile_function]
            >> create_constants_view
            >> create_popularity_function
            >> create_matview
        )

    return dag


# Generate a recreate_popularity_calculation DAG for each DATA_REFRESH_CONFIG.
for data_refresh in DATA_REFRESH_CONFIGS:
    recreate_popularity_calculation_dag = create_recreate_popularity_calculation_dag(
        data_refresh
    )
    globals()[
        recreate_popularity_calculation_dag.dag_id
    ] = recreate_popularity_calculation_dag
