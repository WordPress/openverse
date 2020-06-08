ALTER TABLE image ADD COLUMN new_image_insert_order INTEGER;

UPDATE image SET new_image_insert_order=rn
FROM image_insert_order
WHERE image.id=image_insert_order.id;
