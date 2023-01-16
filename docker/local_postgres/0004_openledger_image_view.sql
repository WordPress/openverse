CREATE TABLE public.image_popularity_metrics (
  provider character varying(80) PRIMARY KEY,
  metric character varying(80),
  percentile float
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


CREATE MATERIALIZED VIEW public.image_popularity_constants AS
  WITH popularity_metric_values AS (
    SELECT
    *,
    image_popularity_percentile(provider, metric, percentile) AS val
    FROM image_popularity_metrics
  )
  SELECT *, ((1 - percentile) / percentile) * val AS constant
  FROM popularity_metric_values;

CREATE UNIQUE INDEX ON image_popularity_constants (provider);


CREATE FUNCTION standardized_image_popularity(provider text, meta_data jsonb)
RETURNS FLOAT AS $$
  SELECT ($2->>metric)::FLOAT / (($2->>metric)::FLOAT + constant)
  FROM image_popularity_constants WHERE provider=$1;
$$
LANGUAGE SQL
STABLE
RETURNS NULL ON NULL INPUT;


CREATE MATERIALIZED VIEW image_view AS
  SELECT
    identifier,
    created_on,
    updated_on,
    ingestion_type,
    provider,
    source,
    foreign_identifier,
    foreign_landing_url,
    url,
    thumbnail,
    width,
    height,
    filesize,
    license,
    license_version,
    creator,
    creator_url,
    title,
    meta_data,
    tags,
    watermarked,
    last_synced_with_source,
    removed_from_source,
    filetype,
    category,
    standardized_image_popularity(
      image.provider, image.meta_data
    ) AS standardized_popularity
  FROM image;

CREATE UNIQUE INDEX ON image_view (identifier);
