CREATE TABLE image_insert_order AS
SELECT row_number() OVER (
  PARTITION BY provider, foreign_identifier
  ORDER BY updated_on
) rn, id
FROM image;

ALTER TABLE public.image_insert_order ADD CONSTRAINT image_insert_order_pkey (id);
CREATE INDEX image_insert_order_rn_idx on image_insert_order USING btree (rn);
