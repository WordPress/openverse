/*
-------------------------------------------------------------------------------
PHOTOS
-------------------------------------------------------------------------------
--  despite the 2022-05-30 data set having complete observer IDs, we do not use an FK
    constraint on observer_id in order to save load time
--  photo_id is not unique. There are ~130,000 duplicate photo_ids (~0.1% of photos).
    Both records are saved to the TSV and only one is loaded back into to postgres.

Taking DDL from
https://github.com/inaturalist/inaturalist-open-data/blob/main/Metadata/structure.sql
*/

DROP TABLE IF EXISTS inaturalist.photos CASCADE;
COMMIT;

CREATE TABLE inaturalist.photos (
    photo_uuid uuid NOT NULL,
    photo_id integer NOT NULL,
    observation_uuid uuid NOT NULL,
    observer_id integer,
    extension character varying(5),
    license character varying(255),
    width smallint,
    height smallint,
    position smallint
);
COMMIT;

SELECT aws_s3.table_import_from_s3('inaturalist.photos',
    '',
    '(FORMAT ''csv'', DELIMITER E''\t'', HEADER, QUOTE E''\b'')',
    'inaturalist-open-data',
    'photos.csv.gz',
    'us-east-1');

-- Not unique, because photo id isn't unique, and it will take too long to check.
-- btree because that is the only one that will support limit/offset without sorting.
-- more here: https://www.postgresql.org/docs/current/indexes-ordering.html
CREATE INDEX ON INATURALIST.PHOTOS USING btree (PHOTO_ID);

DROP TABLE IF EXISTS inaturalist.photo_dupes;
CREATE TABLE inaturalist.photo_dupes as (
    SELECT PHOTO_ID, count(*) PHOTO_RECORDS
    FROM INATURALIST.PHOTOS
    GROUP BY PHOTO_ID
    HAVING COUNT(*)>1
);
ALTER TABLE inaturalist.photo_dupes ADD PRIMARY KEY (PHOTO_ID);
COMMIT;

SELECT count(*) FROM inaturalist.photos;
