"""
This file generates Apache Airflow DAGs that, for the given media type,
completely wipes out and recreates the PostgreSQL functions involved in
calculating our standardized popularity metric.

Note that they do not drop any tables or views related to popularity, and
they do not perform any popularity calculations. Once this DAG has been run,
the associated popularity refresh DAG must be run in order to actually
recalculate popularity constants and standardized popularity scores using
the new functions.

These DAGs are not on a schedule, and should only be run manually when new
SQL code is deployed for the calculation.
"""

from airflow import DAG

from common.constants import DAG_DEFAULT_ARGS, POSTGRES_CONN_ID
from popularity import sql
from popularity.popularity_refresh_types import (
    POPULARITY_REFRESH_CONFIGS,
    PopularityRefresh,
)


def create_recreate_popularity_calculation_dag(popularity_refresh: PopularityRefresh):
    media_type = popularity_refresh.media_type
    default_args = {
        **DAG_DEFAULT_ARGS,
        **popularity_refresh.default_args,
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
        drop_functions = sql.drop_media_popularity_functions(
            postgres_conn_id=POSTGRES_CONN_ID,
            media_type=media_type,
        )
        drop_functions.doc = "Drop the existing popularity functions."

        create_percentile_function = sql.create_media_popularity_percentile_function(
            postgres_conn_id=POSTGRES_CONN_ID,
            media_type=media_type,
        )
        create_percentile_function.doc = (
            "Create the function for calculating popularity percentile values, "
            "used for calculating the popularity constants for each provider."
        )

        create_popularity_function = sql.create_standardized_media_popularity_function(
            postgres_conn_id=POSTGRES_CONN_ID,
            media_type=media_type,
        )
        create_popularity_function.doc = (
            "Create the function that calculates popularity data for a given "
            "record, standardizing across providers with the generated popularity "
            "constants."
        )

        (drop_functions >> create_percentile_function >> create_popularity_function)

    return dag


# Generate a recreate_popularity_calculation DAG for each POPULARITY_REFRESH_CONFIGS.
for popularity_refresh in POPULARITY_REFRESH_CONFIGS:
    recreate_popularity_calculation_dag = create_recreate_popularity_calculation_dag(
        popularity_refresh
    )
    globals()[recreate_popularity_calculation_dag.dag_id] = (
        recreate_popularity_calculation_dag
    )
