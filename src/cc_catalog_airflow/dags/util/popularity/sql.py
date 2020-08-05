from collections import namedtuple
from textwrap import dedent
from airflow.hooks.postgres_hook import PostgresHook

from util.loader import column_names as col
from util.loader.sql import IMAGE_TABLE_NAME

DEFAULT_PERCENTILE = 0.85

IMAGE_VIEW_NAME = "image_view"
POPULARITY_CONSTANTS_VIEW_NAME = "image_popularity_constants"
POPULARITY_PERCENTILE_FUNCTION_NAME = "image_popularity_percentile"
STANDARDIZED_POPULARITY_FUNCTION_NAME = "standardized_popularity"

# Column name constants
CONSTANT = 'constant'
FID = col.FOREIGN_ID
IDENTIFIER = 'identifier'
METADATA_COLUMN = col.META_DATA
METRIC = 'metric'
PARTITION = col.PROVIDER
PERCENTILE = 'percentile'
PROVIDER = col.PROVIDER
STANDARDIZED_POPULARITY = 'standardized_popularity'

Column = namedtuple('Column', ['name', 'definition'])

POPULARITY_METRICS_TABLE_NAME = "image_popularity_metrics"
POPULARITY_METRICS_TABLE_COLUMNS = [
    Column(name=PARTITION, definition="character varying(80) PRIMARY KEY"),
    Column(name=METRIC, definition="character varying(80)"),
    Column(name=PERCENTILE, definition="float"),
]


POPULARITY_METRICS = {
    "flickr": {"metric": "views"},
    "wikimedia": {"metric": "global_usage_count"},
}


def drop_image_popularity_relations(
        postgres_conn_id,
        image_view=IMAGE_VIEW_NAME,
        constants=POPULARITY_CONSTANTS_VIEW_NAME,
        metrics=POPULARITY_METRICS_TABLE_NAME,
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    drop_image_view = (
        f"DROP MATERIALIZED VIEW IF EXISTS public.{image_view} CASCADE;"
    )
    drop_popularity_constants = (
        f"DROP MATERIALIZED VIEW IF EXISTS public.{constants} CASCADE;"
    )
    drop_popularity_metrics = (
        f"DROP TABLE IF EXISTS public.{metrics} CASCADE;"
    )
    postgres.run(drop_image_view)
    postgres.run(drop_popularity_constants)
    postgres.run(drop_popularity_metrics)


def drop_image_popularity_functions(
        postgres_conn_id,
        standardized_popularity=STANDARDIZED_POPULARITY_FUNCTION_NAME,
        popularity_percentile=POPULARITY_PERCENTILE_FUNCTION_NAME,
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    drop_image_view = (
        f"DROP FUNCTION IF EXISTS public.{standardized_popularity} CASCADE;"
    )
    drop_popularity_constants = (
        f"DROP MATERIALIZED VIEW IF EXISTS public.{constants} CASCADE;"
    postgres.run(drop_standardized_popularity)
    postgres.run(drop_popularity_percentile)


def create_image_popularity_metrics(
        postgres_conn_id,
        popularity_metrics_table=POPULARITY_METRICS_TABLE_NAME,
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    popularity_metrics_columns_string = ',\n          '.join(
        f"{c.name} {c.definition}" for c in POPULARITY_METRICS_TABLE_COLUMNS
    )
    query = dedent(
        f"""
        CREATE TABLE public.{popularity_metrics_table} (
          {popularity_metrics_columns_string}
        );
        """
    )
    postgres.run(query)


def update_image_popularity_metrics(
        postgres_conn_id,
        popularity_metrics_table=POPULARITY_METRICS_TABLE_NAME,
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    column_names = [c.name for c in POPULARITY_METRICS_TABLE_COLUMNS]
    updates_string = ",\n          ".join(
        f"{c}=EXCLUDED.{c}" for c in column_names if c != PARTITION
    )

    query = dedent(
        f"""
        INSERT INTO public.{popularity_metrics_table} (
          {', '.join(column_names)}
        ) VALUES
          {_get_popularity_metric_insert_values_string()}
        ON CONFLICT ({PARTITION})
        DO UPDATE SET
          {updates_string}
        ;
        """
    )
    postgres.run(query)


def create_image_popularity_percentile_function(
        postgres_conn_id,
        popularity_percentile=POPULARITY_PERCENTILE_FUNCTION_NAME,
        partition_column=PARTITION,
        metadata_column=METADATA_COLUMN,
        image_table=IMAGE_TABLE_NAME
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    query = dedent(
        f"""
        CREATE OR REPLACE FUNCTION public.{popularity_percentile}(
            provider text, pop_field text, percentile float
        ) RETURNS FLOAT AS $$
          SELECT percentile_disc($3) WITHIN GROUP (
            ORDER BY ({metadata_column}->>$2)::float
          )
          FROM {image_table} WHERE {partition_column}=$1;
        $$
        LANGUAGE SQL
        STABLE
        RETURNS NULL ON NULL INPUT;
        """
    )
    postgres.run(query)


def create_image_popularity_constants_view(
        postgres_conn_id,
        popularity_constants=POPULARITY_CONSTANTS_VIEW_NAME,
        popularity_metrics=POPULARITY_METRICS_TABLE_NAME,
        popularity_percentile=POPULARITY_PERCENTILE_FUNCTION_NAME,
        constant=CONSTANT,
        metric=METRIC,
        partition=PARTITION,
        percentile=PERCENTILE,

):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    query = dedent(
        f"""
        CREATE MATERIALIZED VIEW public.{popularity_constants} AS
          WITH popularity_metric_values AS (
            SELECT
            *,
            {popularity_percentile}({partition}, {metric}, {percentile}) AS val
            FROM {popularity_metrics}
          )
          SELECT *, ((1 - {percentile}) / {percentile}) * val AS {constant}
          FROM popularity_metric_values;
        """
    )
    postgres.run(query)


def create_standardized_popularity_function(
        postgres_conn_id,
        function_name=STANDARDIZED_POPULARITY_FUNCTION_NAME,
        popularity_constants=POPULARITY_CONSTANTS_VIEW_NAME,
        metric=METRIC,
        constant=CONSTANT
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    query = dedent(
        f"""
        CREATE OR REPLACE FUNCTION public.{function_name}(
          provider text, meta_data jsonb
        ) RETURNS FLOAT AS $$
          SELECT ($2->>{metric})::float / (($2->>{metric})::float + {constant})
          FROM {popularity_constants} WHERE provider=$1;
        $$
        LANGUAGE SQL
        STABLE
        RETURNS NULL ON NULL INPUT;
        """
    )
    postgres.run(query)


def update_image_popularity_constants(
    postgres_conn_id, popularity_constants_view=POPULARITY_CONSTANTS_VIEW_NAME,
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.run(
        f"REFRESH MATERIALIZED VIEW CONCURRENTLY {popularity_constants_view};"
    )


def create_image_view(
        postgres_conn_id,
        standardized_popularity_func=STANDARDIZED_POPULARITY_FUNCTION_NAME,
        image_table_name=IMAGE_TABLE_NAME,
        image_view_name=IMAGE_VIEW_NAME,
        partition=PARTITION,
        meta_data=METADATA_COLUMN,
        standardized_popularity_col=STANDARDIZED_POPULARITY
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    create_view_query = dedent(
        f"""
        CREATE MATERIALIZED VIEW public.{image_view_name} AS
          SELECT
            *,
            {standardized_popularity_func}(
              {image_table_name}.{partition}, {image_table_name}.{meta_data}
            ) AS {standardized_popularity_col}
          FROM {image_table_name};
        """
    )
    add_idx_query = dedent(
        f"""
        CREATE UNIQUE INDEX image_view_identifier_idx
          ON public.{image_view_name} ({IDENTIFIER});
        CREATE UNIQUE INDEX image_view_provider_fid_idx
          ON public.{image_view_name}
          USING btree({PROVIDER}, {FID});
        """
    )
    postgres.run(create_view_query)
    postgres.run(add_idx_query)


def update_image_view(
    postgres_conn_id, image_view_name=IMAGE_VIEW_NAME,
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.run(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {image_view_name};")


def _get_popularity_metric_insert_values_string(
    popularity_metrics=POPULARITY_METRICS,
    default_percentile=DEFAULT_PERCENTILE,
):
    return ",\n          ".join(
        _format_popularity_metric_insert_tuple_string(
            provider,
            provider_info["metric"],
            provider_info.get("percentile", default_percentile),
        )
        for provider, provider_info in popularity_metrics.items()
    )


def _format_popularity_metric_insert_tuple_string(
    provider, metric, percentile, popularity_metrics=POPULARITY_METRICS,
):
    return f"('{provider}', '{metric}', {percentile})"
