from collections import namedtuple
from textwrap import dedent

from airflow.providers.postgres.hooks.postgres import PostgresHook
from common.constants import AUDIO, IMAGE
from common.loader.sql import TABLE_NAMES
from common.storage import columns as col


DEFAULT_PERCENTILE = 0.85

IMAGE_VIEW_NAME = "image_view"
AUDIO_VIEW_NAME = "audio_view"
IMAGE_POPULARITY_CONSTANTS_VIEW = "image_popularity_constants"
AUDIO_POPULARITY_CONSTANTS_VIEW = "audio_popularity_constants"
IMAGE_POPULARITY_PERCENTILE_FUNCTION = "image_popularity_percentile"
AUDIO_POPULARITY_PERCENTILE_FUNCTION = "audio_popularity_percentile"
STANDARDIZED_IMAGE_POPULARITY_FUNCTION = "standardized_image_popularity"
STANDARDIZED_AUDIO_POPULARITY_FUNCTION = "standardized_audio_popularity"

IMAGE_POP_CONSTANTS_IDX = "image_popularity_constants_provider_metric_idx"
AUDIO_POP_CONSTANTS_IDX = "audio_popularity_constants_provider_metric_idx"
IMAGE_VIEW_ID_IDX = "image_view_identifier_idx"
AUDIO_VIEW_ID_IDX = "audio_view_identifier_idx"
IMAGE_VIEW_PROVIDER_FID_IDX = "image_view_provider_fid_idx"
AUDIO_VIEW_PROVIDER_FID_IDX = "audio_view_provider_fid_idx"

# Column name constants
CONSTANT = "constant"
FID = col.FOREIGN_ID.db_name
IDENTIFIER = col.IDENTIFIER.db_name
METADATA_COLUMN = col.META_DATA.db_name
METRIC = "metric"
PARTITION = col.PROVIDER.db_name
PERCENTILE = "percentile"
PROVIDER = col.PROVIDER.db_name

Column = namedtuple("Column", ["name", "definition"])

IMAGE_POPULARITY_METRICS_TABLE_NAME = "image_popularity_metrics"
AUDIO_POPULARITY_METRICS_TABLE_NAME = "audio_popularity_metrics"

IMAGE_POPULARITY_METRICS = {
    "flickr": {"metric": "views"},
    "wikimedia": {"metric": "global_usage_count"},
    "stocksnap": {"metric": "downloads_raw"},
}

AUDIO_POPULARITY_METRICS = {
    "jamendo": {"metric": "listens"},
    "wikimedia_audio": {"metric": "global_usage_count"},
    "freesound": {"metric": "num_downloads"},
}

POPULARITY_METRICS_TABLE_COLUMNS = [
    Column(name=PARTITION, definition="character varying(80) PRIMARY KEY"),
    Column(name=METRIC, definition="character varying(80)"),
    Column(name=PERCENTILE, definition="float"),
]


def drop_media_popularity_relations(
    postgres_conn_id,
    media_type=IMAGE,
    db_view=IMAGE_VIEW_NAME,
    constants=IMAGE_POPULARITY_CONSTANTS_VIEW,
    metrics=IMAGE_POPULARITY_METRICS_TABLE_NAME,
):

    if media_type == AUDIO:
        db_view = AUDIO_VIEW_NAME
        constants = AUDIO_POPULARITY_CONSTANTS_VIEW
        metrics = AUDIO_POPULARITY_METRICS_TABLE_NAME

    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    drop_media_view = f"DROP MATERIALIZED VIEW IF EXISTS public.{db_view} CASCADE;"
    drop_popularity_constants = (
        f"DROP MATERIALIZED VIEW IF EXISTS public.{constants} CASCADE;"
    )
    drop_popularity_metrics = f"DROP TABLE IF EXISTS public.{metrics} CASCADE;"
    postgres.run(drop_media_view)
    postgres.run(drop_popularity_constants)
    postgres.run(drop_popularity_metrics)


def drop_media_popularity_functions(
    postgres_conn_id,
    media_type=IMAGE,
    standardized_popularity=STANDARDIZED_IMAGE_POPULARITY_FUNCTION,
    popularity_percentile=IMAGE_POPULARITY_PERCENTILE_FUNCTION,
):
    if media_type == AUDIO:
        popularity_percentile = AUDIO_POPULARITY_PERCENTILE_FUNCTION
        standardized_popularity = STANDARDIZED_AUDIO_POPULARITY_FUNCTION
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    drop_standardized_popularity = (
        f"DROP FUNCTION IF EXISTS public.{standardized_popularity} CASCADE;"
    )
    drop_popularity_percentile = (
        f"DROP FUNCTION IF EXISTS public.{popularity_percentile} CASCADE;"
    )
    postgres.run(drop_standardized_popularity)
    postgres.run(drop_popularity_percentile)


def create_media_popularity_metrics(
    postgres_conn_id,
    media_type=IMAGE,
    popularity_metrics_table=IMAGE_POPULARITY_METRICS_TABLE_NAME,
):
    if media_type == AUDIO:
        popularity_metrics_table = AUDIO_POPULARITY_METRICS_TABLE_NAME
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    popularity_metrics_columns_string = ",\n            ".join(
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


def update_media_popularity_metrics(
    postgres_conn_id,
    media_type=IMAGE,
    popularity_metrics=None,
    popularity_metrics_table=IMAGE_POPULARITY_METRICS_TABLE_NAME,
):
    if popularity_metrics is None:
        if media_type == AUDIO:
            popularity_metrics = AUDIO_POPULARITY_METRICS
        else:
            popularity_metrics = IMAGE_POPULARITY_METRICS
    if media_type == AUDIO:
        popularity_metrics_table = AUDIO_POPULARITY_METRICS_TABLE_NAME
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    column_names = [c.name for c in POPULARITY_METRICS_TABLE_COLUMNS]
    updates_string = ",\n          ".join(
        f"{c}=EXCLUDED.{c}" for c in column_names if c != PARTITION
    )
    popularity_metric_inserts = _get_popularity_metric_insert_values_string(
        popularity_metrics
    )

    query = dedent(
        f"""
        INSERT INTO public.{popularity_metrics_table} (
          {', '.join(column_names)}
        ) VALUES
          {popularity_metric_inserts}
        ON CONFLICT ({PARTITION})
        DO UPDATE SET
          {updates_string}
        ;
        """
    )
    postgres.run(query)


def _get_popularity_metric_insert_values_string(
    popularity_metrics,
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
    provider,
    metric,
    percentile,
):
    return f"('{provider}', '{metric}', {percentile})"


def create_media_popularity_percentile_function(
    postgres_conn_id,
    media_type=IMAGE,
    popularity_percentile=IMAGE_POPULARITY_PERCENTILE_FUNCTION,
    media_table=TABLE_NAMES[IMAGE],
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    if media_type == AUDIO:
        popularity_percentile = AUDIO_POPULARITY_PERCENTILE_FUNCTION
        media_table = TABLE_NAMES[AUDIO]
    query = dedent(
        f"""
        CREATE OR REPLACE FUNCTION public.{popularity_percentile}(
            provider text, pop_field text, percentile float
        ) RETURNS FLOAT AS $$
          SELECT percentile_disc($3) WITHIN GROUP (
            ORDER BY ({METADATA_COLUMN}->>$2)::float
          )
          FROM {media_table} WHERE {PARTITION}=$1;
        $$
        LANGUAGE SQL
        STABLE
        RETURNS NULL ON NULL INPUT;
        """
    )
    postgres.run(query)


def create_media_popularity_constants_view(
    postgres_conn_id,
    media_type=IMAGE,
    popularity_constants=IMAGE_POPULARITY_CONSTANTS_VIEW,
    popularity_constants_idx=IMAGE_POP_CONSTANTS_IDX,
    popularity_metrics=IMAGE_POPULARITY_METRICS_TABLE_NAME,
    popularity_percentile=IMAGE_POPULARITY_PERCENTILE_FUNCTION,
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    if media_type == AUDIO:
        popularity_constants = AUDIO_POPULARITY_CONSTANTS_VIEW
        popularity_constants_idx = AUDIO_POP_CONSTANTS_IDX
        popularity_metrics = AUDIO_POPULARITY_METRICS_TABLE_NAME
        popularity_percentile = AUDIO_POPULARITY_PERCENTILE_FUNCTION
    create_view_query = dedent(
        f"""
        CREATE MATERIALIZED VIEW public.{popularity_constants} AS
          WITH
            popularity_metric_raw_values AS (
              SELECT
                *,
                {popularity_percentile}({PARTITION}, {METRIC}, {PERCENTILE})
                  AS raw_value
              FROM {popularity_metrics}
            ),
            popularity_metric_values AS(
              SELECT
                *,
                CASE
                  WHEN raw_value=0 THEN
                    1
                  ELSE
                    raw_value
                END AS value
              FROM popularity_metric_raw_values
            )
          SELECT *, ((1 - {PERCENTILE}) / {PERCENTILE}) * value AS {CONSTANT}
          FROM popularity_metric_values;
        """
    )
    add_idx_query = dedent(
        f"""
        CREATE UNIQUE INDEX {popularity_constants_idx}
          ON public.{popularity_constants}
          USING btree({PARTITION}, {METRIC});
        """
    )
    postgres.run(create_view_query)
    postgres.run(add_idx_query)


def update_media_popularity_constants(
    postgres_conn_id,
    media_type=IMAGE,
    popularity_constants_view=IMAGE_POPULARITY_CONSTANTS_VIEW,
):
    if media_type == AUDIO:
        popularity_constants_view = AUDIO_POPULARITY_CONSTANTS_VIEW
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.run(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {popularity_constants_view};")


def create_standardized_media_popularity_function(
    postgres_conn_id,
    media_type=IMAGE,
    function_name=STANDARDIZED_IMAGE_POPULARITY_FUNCTION,
    popularity_constants=IMAGE_POPULARITY_CONSTANTS_VIEW,
):
    if media_type == AUDIO:
        popularity_constants = AUDIO_POPULARITY_CONSTANTS_VIEW
        function_name = STANDARDIZED_AUDIO_POPULARITY_FUNCTION
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    query = dedent(
        f"""
        CREATE OR REPLACE FUNCTION public.{function_name}(
          provider text, meta_data jsonb
        ) RETURNS FLOAT AS $$
          SELECT ($2->>{METRIC})::float / (($2->>{METRIC})::float + {CONSTANT})
          FROM {popularity_constants} WHERE provider=$1;
        $$
        LANGUAGE SQL
        STABLE
        RETURNS NULL ON NULL INPUT;
        """
    )
    postgres.run(query)


def create_media_view(
    postgres_conn_id,
    media_type=IMAGE,
    standardized_popularity_func=STANDARDIZED_IMAGE_POPULARITY_FUNCTION,
    table_name=TABLE_NAMES[IMAGE],
    db_view_name=IMAGE_VIEW_NAME,
    db_view_id_idx=IMAGE_VIEW_ID_IDX,
    db_view_provider_fid_idx=IMAGE_VIEW_PROVIDER_FID_IDX,
):
    if media_type == AUDIO:
        table_name = TABLE_NAMES[AUDIO]
        db_view_name = AUDIO_VIEW_NAME
        db_view_id_idx = AUDIO_VIEW_ID_IDX
        db_view_provider_fid_idx = AUDIO_VIEW_PROVIDER_FID_IDX
        standardized_popularity_func = STANDARDIZED_AUDIO_POPULARITY_FUNCTION
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    create_view_query = dedent(
        f"""
        CREATE MATERIALIZED VIEW public.{db_view_name} AS
          SELECT
            *,
            {standardized_popularity_func}(
              {table_name}.{PARTITION},
              {table_name}.{METADATA_COLUMN}
            ) AS standardized_popularity
          FROM {table_name};
        """
    )
    add_idx_query = dedent(
        f"""
        CREATE UNIQUE INDEX {db_view_id_idx}
          ON public.{db_view_name} ({IDENTIFIER});
        CREATE UNIQUE INDEX {db_view_provider_fid_idx}
          ON public.{db_view_name}
          USING btree({PROVIDER}, md5({FID}));
        """
    )
    postgres.run(create_view_query)
    postgres.run(add_idx_query)


def update_db_view(
    postgres_conn_id,
    media_type=IMAGE,
    db_view_name=IMAGE_VIEW_NAME,
):
    if media_type == AUDIO:
        db_view_name = AUDIO_VIEW_NAME
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.run(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {db_view_name};")
