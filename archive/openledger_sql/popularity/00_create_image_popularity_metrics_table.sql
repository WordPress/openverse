CREATE TABLE public.image_popularity_metrics (
  provider character varying(80) PRIMARY KEY,
  metric character varying(80),
  percentile float
);

INSERT INTO public.image_popularity_metrics (
  provider, metric, percentile
) VALUES
  ('flickr', 'views', 0.85),
  ('wikimedia', 'global_usage_count', 0.85);
