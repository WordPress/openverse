/*
-------------------------------------------------------------------------------
TAXA
-------------------------------------------------------------------------------

Taking DDL from
https://github.com/inaturalist/inaturalist-open-data/blob/main/Metadata/structure.sql
Plus adding a field for ancestry tags.
*/

DROP TABLE IF EXISTS inaturalist.taxa;
COMMIT;

CREATE TABLE inaturalist.taxa (
    taxon_id integer,
    ancestry character varying(255),
    rank_level double precision,
    rank character varying(255),
    name character varying(255),
    active boolean,
    ancestor_names varchar[]
);
COMMIT;

SELECT aws_s3.table_import_from_s3('inaturalist.taxa',
    'taxon_id, ancestry, rank_level, rank, name, active',
    '(FORMAT ''csv'', DELIMITER E''\t'', HEADER, QUOTE E''\b'')',
    'inaturalist-open-data',
    'taxa.csv.gz',
    'us-east-1');

ALTER TABLE inaturalist.taxa ADD PRIMARY KEY (taxon_id);
COMMIT;

WITH aggregated AS
(
    select
        child.taxon_id,
        array_agg(ancestors.name) as ancestor_names
    from
        inaturalist.taxa ancestors,
        inaturalist.taxa child
    where ancestors.taxon_id = ANY (string_to_array(child.ancestry, '/')::int[])
        and ancestors.rank not in ('stateofmatter','epifamily','zoosection')
    group by child.taxon_id
)
UPDATE inaturalist.taxa
SET ancestor_names = aggregated.ancestor_names
from aggregated
where taxa.taxon_id = aggregated.taxon_id;
COMMIT;

SELECT count(*) FROM inaturalist.taxa;
