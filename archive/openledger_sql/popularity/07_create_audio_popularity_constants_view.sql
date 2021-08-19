CREATE MATERIALIZED VIEW public.audio_popularity_constants AS
  WITH popularity_metric_values AS (
    SELECT
    *,
    audio_popularity_percentile(provider, metric, percentile) AS val
    FROM audio_popularity_metrics
  )
  SELECT *, ((1 - percentile) / percentile) * val AS constant
  FROM popularity_metric_values;
