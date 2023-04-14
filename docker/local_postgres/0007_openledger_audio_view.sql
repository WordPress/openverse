CREATE TABLE public.audio_popularity_metrics (
  provider character varying(80) PRIMARY KEY,
  metric character varying(80),
  percentile float
);


INSERT INTO public.audio_popularity_metrics (
  provider, metric, percentile
) VALUES
  ('wikimedia_audio', 'global_usage_count', 0.85),
  ('jamendo', 'listens', 0.85),
  ('freesound', 'num_downloads', 0.85);


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

CREATE UNIQUE INDEX ON audio_popularity_constants (provider);


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
    filetype,
    duration,
    bit_rate,
    sample_rate,
    category,
    genres,
    audio_set,
    alt_files,
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
    audio_set ->> 'foreign_identifier' AS audio_set_foreign_identifier,
    standardized_audio_popularity(
      audio.provider, audio.meta_data
    ) AS standardized_popularity
  FROM audio;

CREATE UNIQUE INDEX ON audio_view (identifier);



CREATE VIEW audioset_view AS
  -- DISTINCT clause exists to ensure that only one record is present for a given
  -- foreign identifier/provider pair. This exists as a hard constraint in the API table
  -- downstream, so we must enforce it here. The audio_set data is chosen by which audio
  -- record was most recently updated (see the final section of the ORDER BY clause
  -- below). More info here:
  -- https://github.com/WordPress/openverse-catalog/issues/658
  SELECT DISTINCT ON (audio_view.audio_set ->> 'foreign_identifier', audio_view.provider)
    (audio_view.audio_set ->> 'foreign_identifier'::text)   ::character varying(1000) AS foreign_identifier,
    (audio_view.audio_set ->> 'title'::text)                ::character varying(2000) AS title,
    (audio_view.audio_set ->> 'foreign_landing_url'::text)  ::character varying(1000) AS foreign_landing_url,
    (audio_view.audio_set ->> 'creator'::text)              ::character varying(2000) AS creator,
    (audio_view.audio_set ->> 'creator_url'::text)          ::character varying(2000) AS creator_url,
    (audio_view.audio_set ->> 'url'::text)                  ::character varying(1000) AS url,
    (audio_view.audio_set ->> 'filesize'::text)             ::integer AS filesize,
    (audio_view.audio_set ->> 'filetype'::text)             ::character varying(80) AS filetype,
    (audio_view.audio_set ->> 'thumbnail'::text)            ::character varying(1000) AS thumbnail,
    audio_view.provider
FROM audio_view
WHERE (audio_view.audio_set IS NOT NULL)
ORDER BY
    audio_view.audio_set ->> 'foreign_identifier',
    audio_view.provider,
    audio_view.updated_on DESC;
