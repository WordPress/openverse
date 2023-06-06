CREATE FUNCTION audio_popularity_percentile(
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
