CREATE TABLE public.audio_popularity_metrics (
  provider character varying(80) PRIMARY KEY,
  metric character varying(80),
  percentile float
);

INSERT INTO public.audio_popularity_metrics (
  provider, metric, percentile
) VALUES
  ('jamendo', 'listens', 0.85);
