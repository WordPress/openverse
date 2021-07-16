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
    standardized_image_popularity(
      image.provider, image.meta_data
    ) AS standardized_image_popularity
  FROM image;
