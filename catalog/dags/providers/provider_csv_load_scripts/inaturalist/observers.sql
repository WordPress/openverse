/*
-------------------------------------------------------------------------------
OBSERVERS
-------------------------------------------------------------------------------

Taking DDL from
https://github.com/inaturalist/inaturalist-open-data/blob/main/Metadata/structure.sql
*/

DROP TABLE IF EXISTS inaturalist.observers;
COMMIT;

CREATE TABLE inaturalist.observers (
    observer_id integer,
    login character varying(255),
    name character varying(255)
);
COMMIT;

SELECT aws_s3.table_import_from_s3('inaturalist.observers',
    '',
    '(FORMAT ''csv'', DELIMITER E''\t'', HEADER, QUOTE E''\b'')',
    'inaturalist-open-data',
    'observers.csv.gz',
    'us-east-1');

ALTER TABLE inaturalist.observers ADD PRIMARY KEY (observer_id);

/*
We prefer to use name, but many iNaturalist users only have a login id, not a name in
the observers table.
As of data from January 2023, out of 589,290 records, only 107,840 (18%) had name data.
Presumably, those with more photos/observations are more likely to have their name in
the table. Still, we will use the login if the name is unavailable.
*/
ALTER TABLE inaturalist.observers ADD COLUMN creator varchar(255) ;
UPDATE inaturalist.observers SET creator = coalesce(name, login) ;
COMMIT;

SELECT count(*) FROM inaturalist.observers;
