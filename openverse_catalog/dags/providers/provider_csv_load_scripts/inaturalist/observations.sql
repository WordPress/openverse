/*
-------------------------------------------------------------------------------
OBSERVATIONS
-------------------------------------------------------------------------------
--  ~400,000 observations do not have a taxon_id that is in the taxa table.
--  Their photos are not included in the final transformed view on the
    assumption that photos are not useful to us without a title or tags

Taking DDL from
https://github.com/inaturalist/inaturalist-open-data/blob/main/Metadata/structure.sql
*/

DROP TABLE IF EXISTS inaturalist.observations;
COMMIT;

CREATE TABLE inaturalist.observations (
    observation_uuid uuid,
    observer_id integer,
    latitude numeric(15, 10),
    longitude numeric(15, 10),
    positional_accuracy integer,
    taxon_id integer,
    quality_grade character varying(255),
    observed_on date
);
COMMIT;

SELECT aws_s3.table_import_from_s3('inaturalist.observations',
    '',
    '(FORMAT ''csv'', DELIMITER E''\t'', HEADER, QUOTE E''\b'')',
    'inaturalist-open-data',
    'observations.csv.gz',
    'us-east-1');

ALTER TABLE inaturalist.observations ADD PRIMARY KEY (observation_uuid);
COMMIT;

SELECT count(*) FROM inaturalist.observations;
