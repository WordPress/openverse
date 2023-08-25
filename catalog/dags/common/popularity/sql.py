from collections import namedtuple
from datetime import timedelta
from textwrap import dedent

from airflow.decorators import task, task_group
from airflow.models.abstractoperator import AbstractOperator

from common.constants import AUDIO, DAG_DEFAULT_ARGS, IMAGE
from common.loader.sql import TABLE_NAMES
from common.popularity.constants import (
    AUDIO_POPULARITY_PERCENTILE_FUNCTION,
    AUDIO_VIEW_NAME,
    IMAGE_POPULARITY_PERCENTILE_FUNCTION,
    IMAGE_VIEW_NAME,
    STANDARDIZED_AUDIO_POPULARITY_FUNCTION,
    STANDARDIZED_IMAGE_POPULARITY_FUNCTION,
)
from common.sql import PostgresHook, _single_value
from common.storage import columns as col
from common.storage.db_columns import AUDIO_TABLE_COLUMNS, IMAGE_TABLE_COLUMNS


DEFAULT_PERCENTILE = 0.85

IMAGE_VIEW_ID_IDX = "image_view_identifier_idx"
AUDIO_VIEW_ID_IDX = "audio_view_identifier_idx"
IMAGE_VIEW_PROVIDER_FID_IDX = "image_view_provider_fid_idx"
AUDIO_VIEW_PROVIDER_FID_IDX = "audio_view_provider_fid_idx"

# Column name constants
VALUE = "val"
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
    "nappy": {"metric": "downloads"},
    "rawpixel": {"metric": "download_count"},
    "stocksnap": {"metric": "downloads_raw"},
    "wikimedia": {"metric": "global_usage_count"},
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
    Column(name=VALUE, definition="float"),
    Column(name=CONSTANT, definition="float"),
]

# Further refactoring of this nature will be done in
# https://github.com/WordPress/openverse/issues/2678.
POPULARITY_METRICS_BY_MEDIA_TYPE = {
    AUDIO: AUDIO_POPULARITY_METRICS,
    IMAGE: IMAGE_POPULARITY_METRICS,
}


def drop_media_matview(
    postgres_conn_id: str,
    media_type: str = IMAGE,
    db_view: str = IMAGE_VIEW_NAME,
    pg_timeout: float = timedelta(minutes=10).total_seconds(),
):
    if media_type == AUDIO:
        db_view = AUDIO_VIEW_NAME

    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id, default_statement_timeout=pg_timeout
    )
    postgres.run(f"DROP MATERIALIZED VIEW IF EXISTS public.{db_view} CASCADE;")


def drop_media_popularity_relations(
    postgres_conn_id,
    media_type=IMAGE,
    db_view=IMAGE_VIEW_NAME,
    metrics=IMAGE_POPULARITY_METRICS_TABLE_NAME,
    pg_timeout: float = timedelta(minutes=10).total_seconds(),
):
    if media_type == AUDIO:
        db_view = AUDIO_VIEW_NAME
        metrics = AUDIO_POPULARITY_METRICS_TABLE_NAME

    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id, default_statement_timeout=pg_timeout
    )
    drop_media_view = f"DROP MATERIALIZED VIEW IF EXISTS public.{db_view} CASCADE;"
    drop_popularity_metrics = f"DROP TABLE IF EXISTS public.{metrics} CASCADE;"
    postgres.run(drop_media_view)
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
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id, default_statement_timeout=10.0
    )
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
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id, default_statement_timeout=10.0
    )
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


@task
def update_media_popularity_metrics(
    postgres_conn_id,
    media_type=IMAGE,
    popularity_metrics=None,
    popularity_metrics_table=IMAGE_POPULARITY_METRICS_TABLE_NAME,
    popularity_percentile=IMAGE_POPULARITY_PERCENTILE_FUNCTION,
    task: AbstractOperator = None,
):
    if popularity_metrics is None:
        popularity_metrics = POPULARITY_METRICS_BY_MEDIA_TYPE[media_type]
    if media_type == AUDIO:
        popularity_metrics_table = AUDIO_POPULARITY_METRICS_TABLE_NAME
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
    )

    column_names = [c.name for c in POPULARITY_METRICS_TABLE_COLUMNS]

    # Note that we do not update the val and constant. That is only done during the
    # calculation tasks. In other words, we never want to clear out the current value of
    # the popularity constant unless we're already done calculating the new one, since
    # that can be a time consuming process.
    updates_string = ",\n          ".join(
        f"{c}=EXCLUDED.{c}"
        for c in column_names
        if c not in [PARTITION, CONSTANT, VALUE]
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
    return postgres.run(query)


@task
def calculate_media_popularity_percentile_value(
    postgres_conn_id,
    provider,
    media_type=IMAGE,
    popularity_metrics_table=IMAGE_POPULARITY_METRICS_TABLE_NAME,
    popularity_percentile=IMAGE_POPULARITY_PERCENTILE_FUNCTION,
    task: AbstractOperator = None,
):
    if media_type == AUDIO:
        popularity_metrics_table = AUDIO_POPULARITY_METRICS_TABLE_NAME
        popularity_percentile = AUDIO_POPULARITY_PERCENTILE_FUNCTION

    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
    )

    # Calculate the percentile value. E.g. if `percentile` = 0.80, then we'll
    # calculate the _value_ of the 80th percentile for this provider's
    # popularity metric.
    calculate_new_percentile_value_query = dedent(
        f"""
        SELECT {popularity_percentile}({PARTITION}, {METRIC}, {PERCENTILE})
        FROM {popularity_metrics_table}
        WHERE {col.PROVIDER.db_name}='{provider}';
        """
    )

    raw_percentile_value = postgres.run(
        calculate_new_percentile_value_query, handler=_single_value
    )

    return raw_percentile_value


@task
def update_percentile_and_constants_values_for_provider(
    postgres_conn_id,
    provider,
    raw_percentile_value,
    media_type=IMAGE,
    popularity_metrics=None,
    popularity_metrics_table=IMAGE_POPULARITY_METRICS_TABLE_NAME,
    task: AbstractOperator = None,
):
    if popularity_metrics is None:
        popularity_metrics = POPULARITY_METRICS_BY_MEDIA_TYPE.get(media_type, {})
    if media_type == AUDIO:
        popularity_metrics_table = AUDIO_POPULARITY_METRICS_TABLE_NAME

    if raw_percentile_value is None:
        # Occurs when a provider has a metric configured, but there are no records
        # with any data for that metric.
        return

    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
    )

    provider_info = popularity_metrics.get(provider)
    percentile = provider_info.get("percentile", DEFAULT_PERCENTILE)

    # Calculate the popularity constant using the percentile value
    percentile_value = raw_percentile_value or 1
    new_constant = ((1 - percentile) / (percentile)) * percentile_value

    # Update the percentile value and constant in the metrics table
    update_constant_query = dedent(
        f"""
        UPDATE public.{popularity_metrics_table}
        SET {VALUE} = {percentile_value}, {CONSTANT} = {new_constant}
        WHERE {col.PROVIDER.db_name} = '{provider}';
        """
    )
    return postgres.run(update_constant_query)


@task_group
def update_percentile_and_constants_for_provider(
    postgres_conn_id, provider, media_type=IMAGE, execution_timeout=None
):
    calculate_percentile_val = calculate_media_popularity_percentile_value.override(
        task_id="calculate_percentile_value",
        execution_timeout=execution_timeout
        or DAG_DEFAULT_ARGS.get("execution_timeout"),
    )(
        postgres_conn_id=postgres_conn_id,
        provider=provider,
        media_type=media_type,
    )
    calculate_percentile_val.doc = (
        "Calculate the percentile popularity value for this provider. For"
        " example, if this provider has `percentile`=0.80 and `metric`='views',"
        " calculate the 80th percentile value of views for all records for this"
        " provider."
    )

    update_metrics_table = update_percentile_and_constants_values_for_provider.override(
        task_id="update_percentile_values_and_constant",
    )(
        postgres_conn_id=postgres_conn_id,
        provider=provider,
        raw_percentile_value=calculate_percentile_val,
        media_type=media_type,
    )
    update_metrics_table.doc = (
        "Given the newly calculated percentile value, calculate the"
        " popularity constant and update the metrics table with the newly"
        " calculated values."
    )


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
    # Default null val and constant
    return f"('{provider}', '{metric}', {percentile}, null, null)"


def create_media_popularity_percentile_function(
    postgres_conn_id,
    media_type=IMAGE,
    popularity_percentile=IMAGE_POPULARITY_PERCENTILE_FUNCTION,
    media_table=TABLE_NAMES[IMAGE],
):
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id, default_statement_timeout=10.0
    )
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


def create_standardized_media_popularity_function(
    postgres_conn_id,
    media_type=IMAGE,
    function_name=STANDARDIZED_IMAGE_POPULARITY_FUNCTION,
    popularity_metrics=IMAGE_POPULARITY_METRICS_TABLE_NAME,
):
    if media_type == AUDIO:
        popularity_metrics = AUDIO_POPULARITY_METRICS_TABLE_NAME
        function_name = STANDARDIZED_AUDIO_POPULARITY_FUNCTION
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id, default_statement_timeout=10.0
    )
    query = dedent(
        f"""
        CREATE OR REPLACE FUNCTION public.{function_name}(
          provider text, meta_data jsonb
        ) RETURNS FLOAT AS $$
          SELECT ($2->>{METRIC})::float / (($2->>{METRIC})::float + {CONSTANT})
          FROM {popularity_metrics} WHERE provider=$1;
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
    db_columns=IMAGE_TABLE_COLUMNS,
    db_view_name=IMAGE_VIEW_NAME,
    db_view_id_idx=IMAGE_VIEW_ID_IDX,
    db_view_provider_fid_idx=IMAGE_VIEW_PROVIDER_FID_IDX,
    task: AbstractOperator = None,
):
    if media_type == AUDIO:
        table_name = TABLE_NAMES[AUDIO]
        db_columns = AUDIO_TABLE_COLUMNS
        db_view_name = AUDIO_VIEW_NAME
        db_view_id_idx = AUDIO_VIEW_ID_IDX
        db_view_provider_fid_idx = AUDIO_VIEW_PROVIDER_FID_IDX
        standardized_popularity_func = STANDARDIZED_AUDIO_POPULARITY_FUNCTION
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
    )
    # We want to copy all columns except standardized popularity, which is calculated
    columns_to_select = (", ").join(
        [
            column.db_name
            for column in db_columns
            if column.db_name != col.STANDARDIZED_POPULARITY.db_name
        ]
    )
    create_view_query = dedent(
        f"""
        CREATE MATERIALIZED VIEW public.{db_view_name} AS
          SELECT
            {columns_to_select},
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


def get_providers_with_popularity_data_for_media_type(
    postgres_conn_id: str,
    media_type: str = IMAGE,
    popularity_metrics: str = IMAGE_POPULARITY_METRICS_TABLE_NAME,
    pg_timeout: float = timedelta(minutes=10).total_seconds(),
):
    """
    Return a list of distinct `provider`s that support popularity data,
    for the given media type.
    """
    if media_type == AUDIO:
        popularity_metrics = AUDIO_POPULARITY_METRICS_TABLE_NAME

    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id, default_statement_timeout=pg_timeout
    )
    providers = postgres.get_records(
        f"SELECT DISTINCT provider FROM public.{popularity_metrics};"
    )

    return [x[0] for x in providers]


def format_update_standardized_popularity_query(
    media_type=IMAGE,
    standardized_popularity_func=STANDARDIZED_IMAGE_POPULARITY_FUNCTION,
    table_name=TABLE_NAMES[IMAGE],
    db_columns=IMAGE_TABLE_COLUMNS,
    db_view_name=IMAGE_VIEW_NAME,
    db_view_id_idx=IMAGE_VIEW_ID_IDX,
    db_view_provider_fid_idx=IMAGE_VIEW_PROVIDER_FID_IDX,
    task: AbstractOperator = None,
):
    """
    Create a SQL query for updating the standardized popularity for the given
    media type. Only the `SET ...` portion of the query is returned, to be used
    by a `batched_update` DagRun.
    """
    if media_type == AUDIO:
        table_name = TABLE_NAMES[AUDIO]
        standardized_popularity_func = STANDARDIZED_AUDIO_POPULARITY_FUNCTION

    return (
        f"SET {col.STANDARDIZED_POPULARITY.db_name} = {standardized_popularity_func}"
        f"({table_name}.{PARTITION}, {table_name}.{METADATA_COLUMN})"
    )


def update_db_view(
    postgres_conn_id, media_type=IMAGE, db_view_name=IMAGE_VIEW_NAME, task=None
):
    if media_type == AUDIO:
        db_view_name = AUDIO_VIEW_NAME
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
    )
    postgres.run(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {db_view_name};")
