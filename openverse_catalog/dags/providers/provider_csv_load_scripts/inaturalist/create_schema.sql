CREATE SCHEMA IF NOT EXISTS inaturalist;
COMMIT;
SELECT schema_name
FROM information_schema.schemata WHERE schema_name = 'inaturalist';

/*
LICENSE LOOKUP
Everything on iNaturalist is holding at version 4, except CC0 which is version 1.0.
License versions below are hard-coded from inaturalist
https://github.com/inaturalist/inaturalist/blob/d338ba76d82af83d8ad0107563015364a101568c/app/models/shared/license_module.rb#L5
*/

DROP TABLE IF EXISTS inaturalist.license_codes;
COMMIT;

/*
_enrich_metadata calls for both license_url and raw_license_url, but there is no
raw license_url here, it's all calculated
https://github.com/WordPress/openverse-catalog/blob/337ea7aede228609cbd5031e3a501f22b6ccc482/openverse_catalog/dags/common/storage/media.py#L247
*/
CREATE TABLE inaturalist.license_codes (
    inaturalist_code varchar(50),
    license_name varchar(255),
    license_url_metadata jsonb,
    openverse_code varchar(50),
    license_version varchar(25)
);
COMMIT;

INSERT INTO inaturalist.license_codes
    (inaturalist_code, license_name, license_url_metadata, openverse_code, license_version)
    VALUES
    ('CC-BY-NC-SA', 'Creative Commons Attribution-NonCommercial-ShareAlike License', jsonb_build_object('license_url', 'http://creativecommons.org/licenses/by-nc-sa/4.0/'), 'by-nc-sa', '4.0'),
    ('CC-BY-NC', 'Creative Commons Attribution-NonCommercial License', jsonb_build_object('license_url', 'http://creativecommons.org/licenses/by-nc/4.0/'), 'by-nc', '4.0'),
    ('CC-BY-NC-ND', 'Creative Commons Attribution-NonCommercial-NoDerivs License', jsonb_build_object('license_url', 'http://creativecommons.org/licenses/by-nc-nd/4.0/'), 'by-nc-nd', '4.0'),
    ('CC-BY', 'Creative Commons Attribution License', jsonb_build_object('license_url', 'http://creativecommons.org/licenses/by/4.0/'), 'by', '4.0'),
    ('CC-BY-SA', 'Creative Commons Attribution-ShareAlike License', jsonb_build_object('license_url', 'http://creativecommons.org/licenses/by-sa/4.0/'), 'by-sa', '4.0'),
    ('CC-BY-ND', 'Creative Commons Attribution-NoDerivs License', jsonb_build_object('license_url', 'http://creativecommons.org/licenses/by-nd/4.0/'), 'by-nd', '4.0'),
    ('PD', 'Public domain', jsonb_build_object('license_url', 'http://en.wikipedia.org/wiki/Public_domain'), 'pdm', ''),
    ('GFDL', 'GNU Free Documentation License', jsonb_build_object('license_url', 'http://www.gnu.org/copyleft/fdl.html'), 'gfdl', ''),
    ('CC0', 'Creative Commons CC0 Universal Public Domain Dedication', jsonb_build_object('license_url', 'http://creativecommons.org/publicdomain/zero/1.0/'), 'cc0', '1.0');
COMMIT;

/*
SPECIES NAMES
The Catalog of Life (COL) has data on vernacular names which we use to optimize titles
and tags based on iNaturalist taxon information. But there a few very common taxon_ids
that do not have matches in the COL so I am adding them hard coded here.

Another option would be the Integrated Taxonomic Information System
https://www.itis.gov/dwca_format.html which also has vernacular names / synonyms.
*/

DROP TABLE IF EXISTS inaturalist.col_vernacular;
COMMIT;

CREATE TABLE inaturalist.col_vernacular (
    taxonID varchar(5),
    sourceID decimal,
    taxon_name varchar(2000),
    transliteration text,
    name_language varchar(3),
    country varchar(3),
    area varchar(2000),
    sex decimal,
    referenceID decimal
);
COMMIT;

DROP TABLE IF EXISTS inaturalist.col_name_usage;
COMMIT;

CREATE TABLE inaturalist.col_name_usage (
    ID varchar(50),
    alternativeID decimal,
    nameAlternativeID decimal,
    sourceID decimal,
    parentID varchar(5),
    basionymID varchar(5),
    status varchar(22),
    scientificName varchar(76),
    authorship varchar(255),
    rank varchar(21),
    notho varchar(13),
    uninomial varchar(50),
    genericName varchar(50),
    infragenericEpithet varchar(25),
    specificEpithet varchar(50),
    infraspecificEpithet varchar(50),
    cultivarEpithet varchar(50),
    namePhrase varchar(80),
    nameReferenceID varchar(36),
    publishedInYear decimal,
    publishedInPage varchar(255),
    publishedInPageLink varchar(255),
    code varchar(10),
    nameStatus varchar(15),
    accordingToID varchar(36),
    accordingToPage decimal,
    accordingToPageLink decimal,
    referenceID text,
    scrutinizer varchar(149),
    scrutinizerID decimal,
    scrutinizerDate varchar(10),
    extinct boolean,
    temporalRangeStart varchar(15),
    temporalRangeEnd varchar(15),
    environment varchar(38),
    species decimal,
    section decimal,
    subgenus decimal,
    genus decimal,
    subtribe decimal,
    tribe decimal,
    subfamily decimal,
    taxon_family decimal,
    superfamily decimal,
    suborder decimal,
    taxon_order decimal,
    subclass decimal,
    taxon_class decimal,
    subphylum decimal,
    phylum decimal,
    kingdom decimal,
    sequenceIndex decimal,
    branchLength decimal,
    link varchar(240),
    nameRemarks decimal,
    remarks text
);
COMMIT;

DROP TABLE IF EXISTS inaturalist.manual_name_additions;
COMMIT;

CREATE TABLE inaturalist.manual_name_additions (
    md5_scientificname uuid,
    vernacular_name varchar(100)
);
with records as
    (
        select cast(md5('Animalia') as uuid) as md5_scientificname, 'Animals' as vernacular_name
        union all
        select cast(md5('Araneae') as uuid) as md5_scientificname, 'Spider' as vernacular_name
        union all
        select cast(md5('Magnoliopsida') as uuid) as md5_scientificname, 'Flowers' as vernacular_name
        union all
        select cast(md5('Plantae') as uuid) as md5_scientificname, 'Plants' as vernacular_name
        union all
        select cast(md5('Lepidoptera') as uuid) as md5_scientificname, 'Butterflies and Moths' as vernacular_name
        union all
        select cast(md5('Insecta') as uuid) as md5_scientificname, 'Insect' as vernacular_name
        union all
        select cast(md5('Agaricales') as uuid) as md5_scientificname, 'Mushroom' as vernacular_name
        union all
        select cast(md5('Poaceae') as uuid) as md5_scientificname, 'Grass' as vernacular_name
        union all
        select cast(md5('Asteraceae') as uuid) as md5_scientificname, 'Daisy' as vernacular_name
        union all
        select cast(md5('Danaus plexippus') as uuid) as md5_scientificname, 'Monarch Butterfly' as vernacular_name
        union all
        select cast(md5('Felinae') as uuid) as md5_scientificname, 'Cats' as vernacular_name
        union all
        select cast(md5('Canis') as uuid) as md5_scientificname, 'Dogs' as vernacular_name
    )
INSERT INTO inaturalist.manual_name_additions
(select * from records);
COMMIT;

select distinct table_schema
from information_schema.tables
where table_schema='inaturalist';
