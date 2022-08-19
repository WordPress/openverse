/*
-------------------------------------------------------------------------------
EXPORT TO JSON
-------------------------------------------------------------------------------

    ** Please note: This SQL will not run as is! You must replace offset_num and
    batch_limit with integers representing the records you want to retrieve.

Joining two very large normalized tables is difficult, in any data manipulation system.
PHOTOS has on the order of 120 million records, and OBSERVATIONS has on the order of
70 million records. We have to join them to get at the taxa (species) information for
any given photo. Taxa are the only descriptive text we have for inaturalist photos.

The postgres query optimizer is smart enough to use limit and offset to make this like
joining multiple small-ish tables to a single large one which is not so difficult. The
ORDER BY requires a sort on each call, but the index on INATURALIST.PHOTOS.PHOTO_ID
makes that manageable. (More info on limit / offset and query optimization at
https://www.postgresql.org/docs/current/queries-limit.html)

This query calls for 100 records at a time to match the pace of the python ingester.

Alternative approaches considered:
- Let python do the pagination using a cursor: Joining the two full tables in one step
  requires working through 120 million * 70 million possible combinations, and when
  tested with the full dataset after 13 minutes the local machine was physically hot and
  had not yet returned a single record.
- Use database pagination instead of limit/offset: This would have avoided the need to
  sort / index, but might have introduced data quality risks (if postgres moved
  things around while the job was running) and some pages appeared empty which required
  more complicated python logic for retries. More on this approach at:
  https://www.citusdata.com/blog/2016/03/30/five-ways-to-paginate/

Everything on iNaturalist is holding at version 4, except CC0 which is version 1.0.
License versions below are hard-coded from inaturalist
https://github.com/inaturalist/inaturalist/blob/d338ba76d82af83d8ad0107563015364a101568c/app/models/shared/license_module.rb#L5
*/

select json_agg(records)
from (
        SELECT
            INATURALIST.PHOTOS.PHOTO_ID as foreign_identifier,
            INATURALIST.PHOTOS.WIDTH,
            INATURALIST.PHOTOS.HEIGHT,
            INATURALIST.TAXA.NAME as title,
            array_to_json(INATURALIST.TAXA.ancestor_names) as raw_tags,
            LOWER(INATURALIST.PHOTOS.EXTENSION) as filetype,
            (CASE
                WHEN INATURALIST.PHOTOS.LICENSE = 'CC-BY-NC-SA'
                    THEN 'http://creativecommons.org/licenses/by-nc-sa/4.0/'
                WHEN INATURALIST.PHOTOS.LICENSE = 'CC-BY-NC'
                    THEN 'http://creativecommons.org/licenses/by-nc/4.0/'
                WHEN INATURALIST.PHOTOS.LICENSE = 'CC-BY-NC-ND'
                    THEN 'http://creativecommons.org/licenses/by-nc-nd/4.0/'
                WHEN INATURALIST.PHOTOS.LICENSE = 'CC-BY'
                    THEN 'http://creativecommons.org/licenses/by/4.0/'
                WHEN INATURALIST.PHOTOS.LICENSE = 'CC-BY-SA'
                    THEN 'http://creativecommons.org/licenses/by-sa/4.0/'
                WHEN INATURALIST.PHOTOS.LICENSE = 'CC-BY-ND'
                    THEN 'http://creativecommons.org/licenses/by-nd/4.0/'
                WHEN INATURALIST.PHOTOS.LICENSE = 'PD'
                    THEN 'http://en.wikipedia.org/wiki/Public_domain'
                WHEN INATURALIST.PHOTOS.LICENSE = 'CC0'
                    THEN 'http://creativecommons.org/publicdomain/zero/1.0/'
                END) as license_url,
            'https://www.inaturalist.org/photos/' || INATURALIST.PHOTOS.PHOTO_ID
                as foreign_landing_url,
            'https://inaturalist-open-data.s3.amazonaws.com/photos/'
            || INATURALIST.PHOTOS.PHOTO_ID || '/medium.' || INATURALIST.PHOTOS.EXTENSION
                as image_url,
            COALESCE(INATURALIST.OBSERVERS.LOGIN, INATURALIST.PHOTOS.OBSERVER_ID::text)
                as creator,
            'https://www.inaturalist.org/users/' || INATURALIST.PHOTOS.OBSERVER_ID
                as creator_url
    FROM INATURALIST.PHOTOS
    INNER JOIN
        INATURALIST.OBSERVATIONS ON
            INATURALIST.PHOTOS.OBSERVATION_UUID = INATURALIST.OBSERVATIONS.OBSERVATION_UUID
    INNER JOIN
        INATURALIST.OBSERVERS ON
            INATURALIST.PHOTOS.OBSERVER_ID = INATURALIST.OBSERVERS.OBSERVER_ID
    INNER JOIN
        INATURALIST.TAXA ON
            INATURALIST.OBSERVATIONS.TAXON_ID = INATURALIST.TAXA.TAXON_ID
    ORDER BY PHOTO_ID
    LIMIT {batch_limit}
    OFFSET {offset_num}
) as records;
