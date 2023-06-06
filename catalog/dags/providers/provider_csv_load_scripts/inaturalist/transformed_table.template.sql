/*
-------------------------------------------------------------------------------
Load Intermediate Table
-------------------------------------------------------------------------------

    ** Please note: This SQL will not run as is! You must replace offset_num and
    batch_limit with integers representing the records you want to retrieve.

Joining two very large normalized tables is difficult, in any data manipulation system.
PHOTOS has on the order of 120 million records, and OBSERVATIONS has on the order of
70 million records. We have to join them to get at the taxa (species) information for
any given photo. Taxa are the only descriptive text we have for inaturalist photos.

Using image columns version 001 from common.storage.tsv_columns.
*/

INSERT INTO {intermediate_table}
(
    SELECT
        /*
        The same photo_id can have multiple records, for example if there are multiple
        observations for separate species. But it only actually happens in about 0.1% of
        the photos. For now, we're skipping them.
        TO DO #685: Figure out aggregating tags and titles or formatting alternate
        foreign ids for photos with multiple taxa and process them separately.
        (If we go the alternate foreign id way, we'd want to drop photos loaded in the
        first inaturalist load.)
        */
        INATURALIST.PHOTOS.PHOTO_ID as FOREIGN_IDENTIFIER,
        'https://www.inaturalist.org/photos/' || INATURALIST.PHOTOS.PHOTO_ID
            as LANDING_URL,
        'https://inaturalist-open-data.s3.amazonaws.com/photos/'
        || INATURALIST.PHOTOS.PHOTO_ID || '/original.' || INATURALIST.PHOTOS.EXTENSION
            as DIRECT_URL,
        -- TO DO #810: Add the thumbnail url here.
        null::varchar(10) as THUMBNAIL,
        -- TO DO #966: jpg, jpeg, png & gif in 6/2022 data
        lower(INATURALIST.PHOTOS.EXTENSION) as FILETYPE,
        null::int as FILESIZE,
        INATURALIST.LICENSE_CODES.OPENVERSE_CODE as LICENSE,
        INATURALIST.LICENSE_CODES.LICENSE_VERSION,
        INATURALIST.OBSERVERS.CREATOR,
        'https://www.inaturalist.org/users/' || INATURALIST.PHOTOS.OBSERVER_ID
            as CREATOR_URL,
        taxa_enriched.title,
        LICENSE_CODES.license_url_metadata as META_DATA,
        taxa_enriched.tags,
        'photograph' as CATEGORY,
        null::boolean as WATERMARKED,
        'inaturalist' as PROVIDER,
        'inaturalist' as SOURCE,
        'sql_bulk_load' as INGESTION_TYPE,
        INATURALIST.PHOTOS.WIDTH,
        INATURALIST.PHOTOS.HEIGHT
    FROM INATURALIST.PHOTOS
    INNER JOIN
        INATURALIST.OBSERVATIONS ON
            INATURALIST.PHOTOS.OBSERVATION_UUID = INATURALIST.OBSERVATIONS.OBSERVATION_UUID
    INNER JOIN
        INATURALIST.OBSERVERS ON
            INATURALIST.PHOTOS.OBSERVER_ID = INATURALIST.OBSERVERS.OBSERVER_ID
    INNER JOIN
        INATURALIST.TAXA_ENRICHED ON
            INATURALIST.OBSERVATIONS.TAXON_ID = INATURALIST.TAXA_ENRICHED.TAXON_ID
    INNER JOIN
        INATURALIST.LICENSE_CODES ON
            INATURALIST.PHOTOS.LICENSE = INATURALIST.LICENSE_CODES.INATURALIST_CODE
    WHERE INATURALIST.PHOTOS.PHOTO_ID BETWEEN {batch_start} AND {batch_end}
        AND NOT(EXISTS(SELECT 1 FROM INATURALIST.PHOTO_DUPES
                WHERE PHOTO_DUPES.PHOTO_ID BETWEEN {batch_start} AND {batch_end}
                AND PHOTO_DUPES.PHOTO_ID = PHOTOS.PHOTO_ID))
)
;
COMMIT;

SELECT count(*) transformed_records, max(FOREIGN_IDENTIFIER) max_id_loaded
FROM {intermediate_table} ;
