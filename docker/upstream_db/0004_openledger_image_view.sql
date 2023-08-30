CREATE TABLE public.image_popularity_metrics (
  provider character varying(80) PRIMARY KEY,
  metric character varying(80),
  percentile float,
  val float,
  constant float
);


-- For more information on these values see:
-- https://github.com/cc-archive/cccatalog/issues/405#issuecomment-629233047
-- https://github.com/cc-archive/cccatalog/pull/477
INSERT INTO public.image_popularity_metrics (
  provider, metric, percentile
) VALUES
  ('flickr', 'views', 0.85),
  ('nappy', 'downloads', 0.85),
  ('rawpixel', 'download_count', 0.85),
  ('stocksnap', 'downloads_raw', 0.85),
  ('wikimedia', 'global_usage_count', 0.85)
;


CREATE FUNCTION image_popularity_percentile(
  provider text, pop_field text, percentile float
) RETURNS FLOAT AS $$
  SELECT percentile_disc($3) WITHIN GROUP (
    ORDER BY (meta_data->>$2)::float
  )
  FROM image WHERE provider=$1;
$$
LANGUAGE SQL
STABLE
RETURNS NULL ON NULL INPUT;


CREATE FUNCTION standardized_image_popularity(provider text, meta_data jsonb)
RETURNS FLOAT AS $$
  SELECT ($2->>metric)::FLOAT / (($2->>metric)::FLOAT + constant)
  FROM image_popularity_metrics WHERE provider=$1;
$$
LANGUAGE SQL
STABLE
RETURNS NULL ON NULL INPUT;
