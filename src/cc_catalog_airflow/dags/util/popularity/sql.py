from textwrap import dedent
from airflow.hooks.postgres_hook import PostgresHook

POPULARITY_METRICS_TABLE_NAME = "image_popularity_metrics"
POPULARITY_CONSTANTS_VIEW_NAME = "image_popularity_constants"
DEFAULT_PERCENTILE = 0.85
POPULARITY_METRICS = {
    "flickr": {"metric": "views"},
    "wikimedia": {"metric": "global_usage_count"},
}


def update_image_popularity_metrics(
    postgres_conn_id, popularity_metrics_table=POPULARITY_METRICS_TABLE_NAME,
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    query = dedent(
        f"""
        INSERT INTO public.{popularity_metrics_table} (
          provider, metric, percentile
        ) VALUES
          {_get_popularity_metric_insert_values_string()}
        ON CONFLICT (provider)
        DO UPDATE SET
          metric=EXCLUDED.metric,
          percentile=EXCLUDED.percentile
        ;
        """
    )
    postgres.run(query)


def update_image_popularity_constants(
        postgres_conn_id,
        popularity_constants_view=POPULARITY_CONSTANTS_VIEW_NAME,
):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.run(
        f"REFRESH MATERIALIZED VIEW {popularity_constants_view};"
    )


def _get_popularity_metric_insert_values_string(
    popularity_metrics=POPULARITY_METRICS,
    default_percentile=DEFAULT_PERCENTILE,
):
    return ",\n  ".join(
        [
            _format_popularity_metric_insert_tuple_string(
                provider,
                provider_info["metric"],
                provider_info.get("percentile", default_percentile),
            )
            for provider, provider_info in popularity_metrics.items()
        ]
    )


def _format_popularity_metric_insert_tuple_string(
    provider, metric, percentile, popularity_metrics=POPULARITY_METRICS,
):
    return f"('{provider}', '{metric}', {percentile})"
