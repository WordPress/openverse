CREATE TABLE image_insert_order AS
SELECT row_number() OVER (
  PARTITION BY provider, foreign_identifier
  ORDER BY updated_on
) rn, id
FROM image;
