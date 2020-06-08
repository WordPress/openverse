INSERT INTO new_image AS new (
  created_on, updated_on, identifier, ingestion_type, provider, source,
  foreign_identifier, foreign_landing_url, url, thumbnail, width, height,
  filesize, license, license_version, creator, creator_url, title,
  last_synced_with_source, removed_from_source, meta_data, tags, watermarked
)
SELECT
  created_on, updated_on, identifier, source, provider, provider,
  foreign_identifier, foreign_landing_url, url, thumbnail, width, height,
  filesize, license, license_version, creator, creator_url, title,
  last_synced_with_source, removed_from_source, meta_data, tags, watermarked
FROM image
WHERE new_image_insert_order=1
ON CONFLICT (provider, md5(foreign_identifier))
DO UPDATE SET
   created_on = EXCLUDED.created_on,
   updated_on = EXCLUDED.updated_on,
   identifier = EXCLUDED.identifier,
   ingestion_type = EXCLUDED.ingestion_type,
   source = EXCLUDED.source,
   foreign_landing_url = EXCLUDED.foreign_landing_url,
   url = EXCLUDED.url,
   thumbnail = EXCLUDED.thumbnail,
   width = EXCLUDED.width,
   height = EXCLUDED.height,
   filesize = EXCLUDED.filesize,
   license = EXCLUDED.license,
   license_version = EXCLUDED.license_version,
   creator = EXCLUDED.creator,
   creator_url = EXCLUDED.creator_url,
   title = EXCLUDED.title,
   last_synced_with_source = EXCLUDED.last_synced_with_source,
   removed_from_source = EXCLUDED.removed_from_source,
   meta_data = COALESCE(
       jsonb_strip_nulls(new.meta_data) || jsonb_strip_nulls(EXCLUDED.meta_data),
       EXCLUDED.meta_data,
       new.meta_data
     ),
   tags = COALESCE(
       (
         SELECT jsonb_agg(DISTINCT x)
         FROM jsonb_array_elements(new.tags || EXCLUDED.tags) t(x)
       ),
       EXCLUDED.tags,
       new.tags
     ),
   watermarked = EXCLUDED.watermarked;
