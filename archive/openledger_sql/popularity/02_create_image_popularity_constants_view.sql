CREATE MATERIALIZED VIEW public.image_popularity_constants AS
  WITH popularity_metric_values AS (
    SELECT
    *,
    image_popularity_percentile(provider, metric, percentile) AS val
    FROM image_popularity_metrics
  )
  SELECT *, ((1 - percentile) / percentile) * val AS constant
  FROM popularity_metric_values;
