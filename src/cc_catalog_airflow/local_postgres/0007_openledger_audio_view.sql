CREATE TABLE public.audio_popularity_metrics (
  provider character varying(80) PRIMARY KEY,
  metric character varying(80),
  percentile float
);


INSERT INTO public.audio_popularity_metrics (
  provider, metric, percentile
) VALUES
  ('jamendo', 'listens', 0.85);


CREATE FUNCTION audio_popularity_percentile(
  provider text, pop_field text, percentile float
) RETURNS FLOAT AS $$
  SELECT percentile_disc($3) WITHIN GROUP (
    ORDER BY (meta_data->>$2)::float
  )
  FROM audio WHERE provider=$1;
$$
LANGUAGE SQL
STABLE
RETURNS NULL ON NULL INPUT;


CREATE MATERIALIZED VIEW public.audio_popularity_constants AS
  WITH popularity_metric_values AS (
    SELECT
    *,
    audio_popularity_percentile(provider, metric, percentile) AS val
    FROM audio_popularity_metrics
  )
  SELECT *, ((1 - percentile) / percentile) * val AS constant
  FROM popularity_metric_values;



CREATE FUNCTION standardized_audio_popularity(provider text, meta_data jsonb)
RETURNS FLOAT AS $$
  SELECT ($2->>metric)::FLOAT / (($2->>metric)::FLOAT + constant)
  FROM audio_popularity_constants WHERE provider=$1;
$$
LANGUAGE SQL
STABLE
RETURNS NULL ON NULL INPUT;


CREATE MATERIALIZED VIEW audio_view AS
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
    duration,
    bit_rate,
    sample_rate,
    category,
    genre,
    audio_set,
    alt_audio_files,
    filesize,
    license,
    license_version,
    creator,
    creator_url,
    title,
    meta_data,
    tags,
    last_synced_with_source,
    removed_from_source,
    standardized_audio_popularity(
      audio.provider, audio.meta_data
    ) AS standardized_audio_popularity
  FROM audio;
