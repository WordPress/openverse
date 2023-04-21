# DAGs

_Note: this document is auto-generated and should not be manually edited_

This document describes the DAGs available along with pertinent DAG information
and the DAG's documentation.

The DAGs are shown in two forms:

- [DAGs by Type](#dags-by-type)
- [Individual DAG documentation](#dag-documentation)

# DAGs by Type

The following are DAGs grouped by their primary tag:

1.  [Data Normalization](#data_normalization)
1.  [Data Refresh](#data_refresh)
1.  [Database](#database)
1.  [Maintenance](#maintenance)
1.  [Oauth](#oauth)
1.  [Provider](#provider)
1.  [Provider Reingestion](#provider-reingestion)

## Data Normalization

| DAG ID                                | Schedule Interval |
| ------------------------------------- | ----------------- |
| [`add_license_url`](#add_license_url) | `None`            |

## Data Refresh

| DAG ID                                                        | Schedule Interval |
| ------------------------------------------------------------- | ----------------- |
| [`audio_data_refresh`](#audio_data_refresh)                   | `@weekly`         |
| [`create_filtered_audio_index`](#create_filtered_audio_index) | `None`            |
| [`create_filtered_image_index`](#create_filtered_image_index) | `None`            |
| [`image_data_refresh`](#image_data_refresh)                   | `None`            |

## Database

| DAG ID                                                                            | Schedule Interval |
| --------------------------------------------------------------------------------- | ----------------- |
| [`recreate_audio_popularity_calculation`](#recreate_audio_popularity_calculation) | `None`            |
| [`recreate_image_popularity_calculation`](#recreate_image_popularity_calculation) | `None`            |
| [`report_pending_reported_media`](#report_pending_reported_media)                 | `@weekly`         |

## Maintenance

| DAG ID                                                                      | Schedule Interval |
| --------------------------------------------------------------------------- | ----------------- |
| [`airflow_log_cleanup`](#airflow_log_cleanup)                               | `@weekly`         |
| [`check_silenced_dags`](#check_silenced_dags)                               | `@weekly`         |
| [`flickr_audit_sub_provider_workflow`](#flickr_audit_sub_provider_workflow) | `@monthly`        |
| [`pr_review_reminders`](#pr_review_reminders)                               | `0 0 * * 1-5`     |
| [`rotate_db_snapshots`](#rotate_db_snapshots)                               | `0 0 * * 6`       |

## Oauth

| DAG ID                                          | Schedule Interval |
| ----------------------------------------------- | ----------------- |
| [`oauth2_authorization`](#oauth2_authorization) | `None`            |
| [`oauth2_token_refresh`](#oauth2_token_refresh) | `0 */12 * * *`    |

## Provider

| DAG ID                                                          | Schedule Interval | Dated   | Media Type(s) |
| --------------------------------------------------------------- | ----------------- | ------- | ------------- |
| `brooklyn_museum_workflow`                                      | `@monthly`        | `False` | image         |
| `cleveland_museum_workflow`                                     | `@monthly`        | `False` | image         |
| [`europeana_workflow`](#europeana_workflow)                     | `@daily`          | `True`  | image         |
| [`finnish_museums_workflow`](#finnish_museums_workflow)         | `@daily`          | `True`  | image         |
| [`flickr_workflow`](#flickr_workflow)                           | `@daily`          | `True`  | image         |
| [`freesound_workflow`](#freesound_workflow)                     | `@quarterly`      | `False` | audio         |
| [`inaturalist_workflow`](#inaturalist_workflow)                 | `0 0 2 * *`       | `False` | image         |
| [`jamendo_workflow`](#jamendo_workflow)                         | `@monthly`        | `False` | audio         |
| [`metropolitan_museum_workflow`](#metropolitan_museum_workflow) | `@daily`          | `True`  | image         |
| `museum_victoria_workflow`                                      | `@monthly`        | `False` | image         |
| [`nappy_workflow`](#nappy_workflow)                             | `@monthly`        | `False` | image         |
| `nypl_workflow`                                                 | `@monthly`        | `False` | image         |
| [`phylopic_workflow`](#phylopic_workflow)                       | `@weekly`         | `False` | image         |
| [`rawpixel_workflow`](#rawpixel_workflow)                       | `@monthly`        | `False` | image         |
| [`science_museum_workflow`](#science_museum_workflow)           | `@monthly`        | `False` | image         |
| [`smithsonian_workflow`](#smithsonian_workflow)                 | `@weekly`         | `False` | image         |
| [`smk_workflow`](#smk_workflow)                                 | `@monthly`        | `False` | image         |
| [`stocksnap_workflow`](#stocksnap_workflow)                     | `@monthly`        | `False` | image         |
| [`wikimedia_commons_workflow`](#wikimedia_commons_workflow)     | `@daily`          | `True`  | image, audio  |
| [`wordpress_workflow`](#wordpress_workflow)                     | `@monthly`        | `False` | image         |

## Provider Reingestion

| DAG ID                                                                                  | Schedule Interval |
| --------------------------------------------------------------------------------------- | ----------------- |
| [`europeana_reingestion_workflow`](#europeana_reingestion_workflow)                     | `@weekly`         |
| [`flickr_reingestion_workflow`](#flickr_reingestion_workflow)                           | `@weekly`         |
| [`metropolitan_museum_reingestion_workflow`](#metropolitan_museum_reingestion_workflow) | `@weekly`         |
| [`phylopic_reingestion_workflow`](#phylopic_reingestion_workflow)                       | `@weekly`         |
| [`wikimedia_reingestion_workflow`](#wikimedia_reingestion_workflow)                     | `@weekly`         |

# DAG documentation

The following is documentation associated with each DAG (where available):

1.  [`add_license_url`](#add_license_url)
1.  [`airflow_log_cleanup`](#airflow_log_cleanup)
1.  [`audio_data_refresh`](#audio_data_refresh)
1.  [`check_silenced_dags`](#check_silenced_dags)
1.  [`create_filtered_audio_index`](#create_filtered_audio_index)
1.  [`create_filtered_image_index`](#create_filtered_image_index)
1.  [`europeana_reingestion_workflow`](#europeana_reingestion_workflow)
1.  [`europeana_workflow`](#europeana_workflow)
1.  [`finnish_museums_workflow`](#finnish_museums_workflow)
1.  [`flickr_audit_sub_provider_workflow`](#flickr_audit_sub_provider_workflow)
1.  [`flickr_reingestion_workflow`](#flickr_reingestion_workflow)
1.  [`flickr_workflow`](#flickr_workflow)
1.  [`freesound_workflow`](#freesound_workflow)
1.  [`image_data_refresh`](#image_data_refresh)
1.  [`inaturalist_workflow`](#inaturalist_workflow)
1.  [`jamendo_workflow`](#jamendo_workflow)
1.  [`metropolitan_museum_reingestion_workflow`](#metropolitan_museum_reingestion_workflow)
1.  [`metropolitan_museum_workflow`](#metropolitan_museum_workflow)
1.  [`nappy_workflow`](#nappy_workflow)
1.  [`oauth2_authorization`](#oauth2_authorization)
1.  [`oauth2_token_refresh`](#oauth2_token_refresh)
1.  [`phylopic_reingestion_workflow`](#phylopic_reingestion_workflow)
1.  [`phylopic_workflow`](#phylopic_workflow)
1.  [`pr_review_reminders`](#pr_review_reminders)
1.  [`rawpixel_workflow`](#rawpixel_workflow)
1.  [`recreate_audio_popularity_calculation`](#recreate_audio_popularity_calculation)
1.  [`recreate_image_popularity_calculation`](#recreate_image_popularity_calculation)
1.  [`report_pending_reported_media`](#report_pending_reported_media)
1.  [`rotate_db_snapshots`](#rotate_db_snapshots)
1.  [`science_museum_workflow`](#science_museum_workflow)
1.  [`smithsonian_workflow`](#smithsonian_workflow)
1.  [`smk_workflow`](#smk_workflow)
1.  [`stocksnap_workflow`](#stocksnap_workflow)
1.  [`wikimedia_commons_workflow`](#wikimedia_commons_workflow)
1.  [`wikimedia_reingestion_workflow`](#wikimedia_reingestion_workflow)
1.  [`wordpress_workflow`](#wordpress_workflow)

## `add_license_url`

### Add license URL

Add `license_url` to all rows that have `NULL` in their `meta_data` fields. This
PR sets the meta_data value to "{license_url: https://... }", where the url is
constructed from the `license` and `license_version` columns.

This is a maintenance DAG that should be run once. If all the null values in the
`meta_data` column are updated, the DAG will only run the first and the last
step, logging the statistics.

## `airflow_log_cleanup`

### Clean up airflow logs

A maintenance workflow that you can deploy into Airflow to periodically clean
out the task logs to avoid those getting too big. By default, this will also
clean child process logs from the 'scheduler' directory.

Can remove all log files by setting "maxLogAgeInDays" to -1. If you want to test
the DAG in the Airflow Web UI, you can also set enableDelete to `false`, and
then you will see a list of log folders that can be deleted, but will not
actually delete them.

This should all go on one line:

```
airflow dags trigger --conf
'{"maxLogAgeInDays":-1, "enableDelete": "false"}' airflow_log_cleanup
```

`--conf` options:

- maxLogAgeInDays:<INT> - Optional
- enableDelete:<BOOLEAN> - Optional

## `audio_data_refresh`

### Data Refresh DAG Factory

This file generates our data refresh DAGs using a factory function. For the
given media type these DAGs will first refresh the popularity data, then
initiate a data refresh on the data refresh server and await the success or
failure of that task.

Popularity data for each media type is collated in a materialized view. Before
initiating a data refresh, the DAG will first refresh the view in order to
update popularity data for records that have been ingested since the last
refresh. On the first run of the month, the DAG will also refresh the underlying
tables, including the percentile values and any new popularity metrics. The DAG
can also be run with the `force_refresh_metrics` option to run this refresh
after the first of the month.

Once this step is complete, the data refresh can be initiated. A data refresh
occurs on the data refresh server in the openverse-api project. This is a task
which imports data from the upstream Catalog database into the API, copies
contents to a new Elasticsearch index, and finally makes the index "live". This
process is necessary to make new content added to the Catalog by our provider
DAGs available to the API. You can read more in the
[README](https://github.com/WordPress/openverse-api/blob/main/ingestion_server/README.md)
Importantly, the data refresh TaskGroup is also configured to handle concurrency
requirements of the data refresh server. Finally, once the origin indexes have
been refreshed, the corresponding filtered index creation DAG is triggered.

You can find more background information on this process in the following issues
and related PRs:

- [[Feature] Data refresh orchestration DAG](https://github.com/WordPress/openverse-catalog/issues/353)
- [[Feature] Merge popularity calculations and data refresh into a single DAG](https://github.com/WordPress/openverse-catalog/issues/453)

## `check_silenced_dags`

### Silenced DAGs check

Check for DAGs that have silenced Slack alerts or skipped errors which may need
to be turned back on.

When a DAG has known failures, it can be ommitted from Slack error reporting by
adding an entry to the `SILENCED_SLACK_NOTIFICATIONS` Airflow variable.
Similarly, errors that occur during the `pull_data` step may be configured to
skip and allow ingestion to continue, using the `SKIPPED_INGESTION_ERRORS`
Airflow variable. These variables are dictionaries where the key is the `dag_id`
of the affected DAG, and the value is a list of configuration dictionaries
mapping an error `predicate` to be skipped/silenced to an open GitHub issue.

The `check_silenced_dags` DAG iterates over the entries in the
`SILENCED_SLACK_NOTIFICATIONS` and `SKIPPED_INGESTION_ERRORS` configurations and
verifies that the associated GitHub issues are still open. If an issue has been
closed, it is assumed that the entry should be removed, and an alert is sent to
prompt manual update of the configuration. This prevents developers from
forgetting to reenable Slack reporting or turnoff error skipping after the issue
has been resolved.

The DAG runs weekly.

## `create_filtered_audio_index`

### Create filtered index DAG factory

This module creates the filtered index creation DAGs for each media type using a
factory function.

Filtered index creation is handled by the ingestion server. The DAGs generated
by the `build_create_filtered_index_dag` function in this module are responsible
for triggering the ingestion server action to create and populate the filtered
index for a given media type. The DAG awaits the completion of the filtered
index creation and then points the filtered index alias for the media type to
the newly created index.

## When this DAG runs

The DAGs generated in this module are triggered by the data refresh DAGs.
Maintaining this process separate from the data refresh DAGs, while still
triggering it there, allows us to run filtered index creation independently of
the full data refresh. This is primarily useful in two cases: for testing
changes to the filtered index creation; and for re-running filtered index
creation if an urgent change to the sensitive terms calls for an immediate
recreation of the filtered indexes.

## Race conditions

Because filtered index creation employs the `reindex` Elasticsearch API to
derive the filtered index from an existing index, we need to be mindful of the
race condition that potentially exists between the data refresh DAG and this
DAG. The race condition is caused by the fact that the data refresh DAG always
deletes the previous index once the new index for the media type is finished
being created. Consider the situation where filtered index creation is triggered
to run during a data refresh. The filtered index is being derived from the
previous index for the media type. Once the data refresh is finished, it will
delete that index, causing the reindex to halt because suddenly it has no data
source from which to pull documents.

There are two mechanisms that prevent this from happening:

1. The filtered index creation DAGs are not allowed to run if a data refresh for
   the media type is already running.
2. The data refresh DAGs will wait for any pre-existing filtered index creation
   DAG runs for the media type to finish before continuing.

This ensures that neither are depending on or modifying the origin indexes
critical for the creation of the filtered indexes.

Because the data refresh DAG triggers the filtered index creation DAG, we do
allow a `force` param to be passed to the DAGs generated by this module. This
parameter is only for use by the data refresh DAG and should not be used when
manually triggering the DAG unless you are absolutely certain of what you are
doing.

## `create_filtered_image_index`

### Create filtered index DAG factory

This module creates the filtered index creation DAGs for each media type using a
factory function.

Filtered index creation is handled by the ingestion server. The DAGs generated
by the `build_create_filtered_index_dag` function in this module are responsible
for triggering the ingestion server action to create and populate the filtered
index for a given media type. The DAG awaits the completion of the filtered
index creation and then points the filtered index alias for the media type to
the newly created index.

## When this DAG runs

The DAGs generated in this module are triggered by the data refresh DAGs.
Maintaining this process separate from the data refresh DAGs, while still
triggering it there, allows us to run filtered index creation independently of
the full data refresh. This is primarily useful in two cases: for testing
changes to the filtered index creation; and for re-running filtered index
creation if an urgent change to the sensitive terms calls for an immediate
recreation of the filtered indexes.

## Race conditions

Because filtered index creation employs the `reindex` Elasticsearch API to
derive the filtered index from an existing index, we need to be mindful of the
race condition that potentially exists between the data refresh DAG and this
DAG. The race condition is caused by the fact that the data refresh DAG always
deletes the previous index once the new index for the media type is finished
being created. Consider the situation where filtered index creation is triggered
to run during a data refresh. The filtered index is being derived from the
previous index for the media type. Once the data refresh is finished, it will
delete that index, causing the reindex to halt because suddenly it has no data
source from which to pull documents.

There are two mechanisms that prevent this from happening:

1. The filtered index creation DAGs are not allowed to run if a data refresh for
   the media type is already running.
2. The data refresh DAGs will wait for any pre-existing filtered index creation
   DAG runs for the media type to finish before continuing.

This ensures that neither are depending on or modifying the origin indexes
critical for the creation of the filtered indexes.

Because the data refresh DAG triggers the filtered index creation DAG, we do
allow a `force` param to be passed to the DAGs generated by this module. This
parameter is only for use by the data refresh DAG and should not be used when
manually triggering the DAG unless you are absolutely certain of what you are
doing.

## `europeana_reingestion_workflow`

Content Provider: Europeana

ETL Process: Use the API to identify all CC licensed images.

Output: TSV file containing the images and the respective meta-data.

Notes: https://pro.europeana.eu/page/search

## `europeana_workflow`

Content Provider: Europeana

ETL Process: Use the API to identify all CC licensed images.

Output: TSV file containing the images and the respective meta-data.

Notes: https://pro.europeana.eu/page/search

## `finnish_museums_workflow`

Content Provider: Finnish Museums

ETL Process: Use the API to identify all CC licensed images.

Output: TSV file containing the images and the respective meta-data.

Notes: https://api.finna.fi/swagger-ui/
https://www.finna.fi/Content/help-syntax?lng=en-gb The Finnish Museums provider
script is a dated DAG that ingests all records that were last updated in the
previous day. Because of this, it is not necessary to run a separate reingestion
DAG, as updated data will be processed during regular ingestion.

## `flickr_audit_sub_provider_workflow`

### Flickr Sub Provider Audit

Check the list of member institutions of the Flickr Commons for institutions
that have cc-licensed images and are not already configured as sub-providers for
the Flickr DAG. Report suggestions for new sub-providers to Slack.

## `flickr_reingestion_workflow`

Content Provider: Flickr

ETL Process: Use the API to identify all CC licensed images.

Output: TSV file containing the images and the respective meta-data.

Notes: https://www.flickr.com/help/terms/api Rate limit: 3600 requests per hour.

## `flickr_workflow`

Content Provider: Flickr

ETL Process: Use the API to identify all CC licensed images.

Output: TSV file containing the images and the respective meta-data.

Notes: https://www.flickr.com/help/terms/api Rate limit: 3600 requests per hour.

## `freesound_workflow`

Content Provider: Freesound

ETL Process: Use the API to identify all CC-licensed images.

Output: TSV file containing the image, the respective meta-data.

Notes: https://freesound.org/docs/api/ Rate limit: No limit for our API key.
This script can be run either to ingest the full dataset or as a dated DAG.

## `image_data_refresh`

### Data Refresh DAG Factory

This file generates our data refresh DAGs using a factory function. For the
given media type these DAGs will first refresh the popularity data, then
initiate a data refresh on the data refresh server and await the success or
failure of that task.

Popularity data for each media type is collated in a materialized view. Before
initiating a data refresh, the DAG will first refresh the view in order to
update popularity data for records that have been ingested since the last
refresh. On the first run of the month, the DAG will also refresh the underlying
tables, including the percentile values and any new popularity metrics. The DAG
can also be run with the `force_refresh_metrics` option to run this refresh
after the first of the month.

Once this step is complete, the data refresh can be initiated. A data refresh
occurs on the data refresh server in the openverse-api project. This is a task
which imports data from the upstream Catalog database into the API, copies
contents to a new Elasticsearch index, and finally makes the index "live". This
process is necessary to make new content added to the Catalog by our provider
DAGs available to the API. You can read more in the
[README](https://github.com/WordPress/openverse-api/blob/main/ingestion_server/README.md)
Importantly, the data refresh TaskGroup is also configured to handle concurrency
requirements of the data refresh server. Finally, once the origin indexes have
been refreshed, the corresponding filtered index creation DAG is triggered.

You can find more background information on this process in the following issues
and related PRs:

- [[Feature] Data refresh orchestration DAG](https://github.com/WordPress/openverse-catalog/issues/353)
- [[Feature] Merge popularity calculations and data refresh into a single DAG](https://github.com/WordPress/openverse-catalog/issues/453)

## `inaturalist_workflow`

Provider: iNaturalist

Output: Records loaded to the image catalog table.

Notes: The iNaturalist API is not intended for data scraping.
https://api.inaturalist.org/v1/docs/ But there is a full dump intended for
sharing on S3.
https://github.com/inaturalist/inaturalist-open-data/tree/documentation/Metadata
Because these are very large normalized tables, as opposed to more document
oriented API responses, we found that bringing the data into postgres first was
the most effective approach. More detail in slack here:
https://wordpress.slack.com/archives/C02012JB00N/p1653145643080479?thread_ts=1653082292.714469&cid=C02012JB00N
We use the table structure defined here,
https://github.com/inaturalist/inaturalist-open-data/blob/main/Metadata/structure.sql
except for adding ancestry tags to the taxa table.

## `jamendo_workflow`

Content Provider: Jamendo

ETL Process: Use the API to identify all CC-licensed audio.

Output: TSV file containing the audio meta-data.

Notes: https://api.jamendo.com/v3.0/tracks/ 35,000 requests per month for
non-commercial apps Jamendo Music has more than 500,000 tracks shared by 40,000
artists from over 150 countries all over the world. Audio quality: uploaded as
WAV/ FLAC/ AIFF bit depth: 16/24 sample rate: 44.1 or 48 kHz channels: 1/2

## `metropolitan_museum_reingestion_workflow`

Content Provider: Metropolitan Museum of Art

ETL Process: Use the API to identify all CC0 artworks.

Output: TSV file containing the image, their respective meta-data.

Notes: https://metmuseum.github.io/#search "Please limit requests to 80 requests
per second." May need to bump up the delay (e.g. to 3 seconds), to avoid of
blocking during local development testing.

                        Some analysis to improve data quality was conducted using a
                        separate csv file here: https://github.com/metmuseum/openaccess

                        Get a list of object IDs:
                        https://collectionapi.metmuseum.org/public/collection/v1/objects?metadataDate=2022-08-10
                        Get a specific object:
                        https://collectionapi.metmuseum.org/public/collection/v1/objects/1027
                        The search functionality requires a specific query (term search)
                        in addition to date and public domain. It seems like it won't
                        connect with just date and license.
                        https://collectionapi.metmuseum.org/public/collection/v1/search?isPublicDomain=true&metadataDate=2022-08-07

## `metropolitan_museum_workflow`

Content Provider: Metropolitan Museum of Art

ETL Process: Use the API to identify all CC0 artworks.

Output: TSV file containing the image, their respective meta-data.

Notes: https://metmuseum.github.io/#search "Please limit requests to 80 requests
per second." May need to bump up the delay (e.g. to 3 seconds), to avoid of
blocking during local development testing.

                        Some analysis to improve data quality was conducted using a
                        separate csv file here: https://github.com/metmuseum/openaccess

                        Get a list of object IDs:
                        https://collectionapi.metmuseum.org/public/collection/v1/objects?metadataDate=2022-08-10
                        Get a specific object:
                        https://collectionapi.metmuseum.org/public/collection/v1/objects/1027
                        The search functionality requires a specific query (term search)
                        in addition to date and public domain. It seems like it won't
                        connect with just date and license.
                        https://collectionapi.metmuseum.org/public/collection/v1/search?isPublicDomain=true&metadataDate=2022-08-07

## `nappy_workflow`

Content Provider: Nappy

ETL Process: Use the API to identify all CC0-licensed images.

Output: TSV file containing the image meta-data.

Notes: This api was written specially for Openverse. There are no known limits
or restrictions. https://nappy.co/

## `oauth2_authorization`

### OAuth Provider Authorization

Iterates through all the OAuth2 providers and attempts to authorize them using
tokens found in the in the `OAUTH2_AUTH_KEYS` Variable. Once authorization has
been completed successfully, the auth token is removed from that Variable. The
authorization will create an access/refresh token pair in the
`OAUTH2_ACCESS_TOKENS` Variable.

**Current Providers**:

- Freesound

## `oauth2_token_refresh`

### OAuth Provider Token Refresh

Iterates through all OAuth2 providers and attempts to refresh the access token
using the refresh token stored in the `OAUTH2_ACCESS_TOKENS` Variable. This DAG
will update the tokens stored in the Variable upon successful refresh.

**Current Providers**:

- Freesound

## `phylopic_reingestion_workflow`

Content Provider: PhyloPic

ETL Process: Use the API to identify all CC licensed images.

Output: TSV file containing the image, their respective meta-data.

Notes: http://api-docs.phylopic.org/v2/ No rate limit specified.

## `phylopic_workflow`

Content Provider: PhyloPic

ETL Process: Use the API to identify all CC licensed images.

Output: TSV file containing the image, their respective meta-data.

Notes: http://api-docs.phylopic.org/v2/ No rate limit specified.

## `pr_review_reminders`

### PR Review Reminders

Iterates through open PRs in our repositories and pings assigned reviewers who
have not yet approved the PR or explicitly requested changes.

This DAG runs daily and pings on the following schedule based on priority label:

| priority | days    |
| -------- | ------- |
| critical | 1 day   |
| high     | >2 days |
| medium   | >4 days |
| low      | >7 days |

The DAG does not ping on Saturday and Sunday and accounts for weekend days when
determining how much time has passed since the review.

Unfortunately the DAG does not know when someone is on vacation. It is up to the
author of the PR to re-assign review if one of the randomly selected reviewers
is unavailable for the time period during which the PR should be reviewed.

## `rawpixel_workflow`

Content Provider: Rawpixel

ETL Process: Use the API to identify all CC-licensed images.

Output: TSV file containing the image meta-data.

Notes: Rawpixel has given Openverse beta access to their API. This API is
undocumented, and we will need to contact Rawpixel directly if we run into any
issues. The public API max results range is limited to 100,000 results, although
the API key we've been given can circumvent this limit.
https://www.rawpixel.com/api/v1/search?tags=$publicdomain&page=1&pagesize=100

## `recreate_audio_popularity_calculation`

This file generates Apache Airflow DAGs that, for the given media type,
completely wipe out the PostgreSQL relations and functions involved in
calculating our standardized popularity metric. It then recreates relations and
functions to make the calculation, and performs an initial calculation. The
results are available in the materialized view for that media type.

These DAGs are not on a schedule, and should only be run manually when new SQL
code is deployed for the calculation.

## `recreate_image_popularity_calculation`

This file generates Apache Airflow DAGs that, for the given media type,
completely wipe out the PostgreSQL relations and functions involved in
calculating our standardized popularity metric. It then recreates relations and
functions to make the calculation, and performs an initial calculation. The
results are available in the materialized view for that media type.

These DAGs are not on a schedule, and should only be run manually when new SQL
code is deployed for the calculation.

## `report_pending_reported_media`

### Report Pending Reported Media DAG

This DAG checks for any user-reported media pending manual review, and alerts
via Slack.

Media may be reported for mature content or copyright infringement, for example.
Once reported, these require manual review through the Django Admin to determine
whether further action (such as deindexing the record) needs to be taken. If a
record has been reported multiple times, it only needs to be reviewed once and
so is only counted once in the reporting by this DAG.

## `rotate_db_snapshots`

Manages weekly database snapshots.

RDS does not support weekly snapshots schedules on its own, so we need a DAG to
manage this for us.

It runs on Saturdays at 00:00 UTC in order to happen before the data refresh.

The DAG will automatically delete the oldest snapshots when more snaphots exist
than it is configured to retain.

Requires two variables:

`AIRFLOW_RDS_ARN`: The ARN of the RDS DB instance that needs snapshots.
`AIRFLOW_RDS_SNAPSHOTS_TO_RETAIN`: How many historical snapshots to retain.

## `science_museum_workflow`

Content Provider: Science Museum

ETL Process: Use the API to identify all CC-licensed images.

Output: TSV file containing the image, the respective meta-data.

Notes:
https://github.com/TheScienceMuseum/collectionsonline/wiki/Collections-Online-API
Rate limited, no specific rate given.

## `smithsonian_workflow`

Content Provider: Smithsonian

ETL Process: Use the API to identify all CC licensed images.

Output: TSV file containing the images and the respective meta-data.

Notes: https://api.si.edu/openaccess/api/v1.0/search

## `smk_workflow`

Content Provider: Statens Museum for Kunst (National Gallery of Denmark)

ETL Process: Use the API to identify all openly licensed media.

Output: TSV file containing the media metadata.

Notes: https://www.smk.dk/en/article/smk-api/

## `stocksnap_workflow`

Content Provider: StockSnap

ETL Process: Use the API to identify all CC-licensed images.

Output: TSV file containing the image, the respective meta-data.

Notes: https://stocksnap.io/api/load-photos/date/desc/1 https://stocksnap.io/faq
All images are licensed under CC0. No rate limits or authorization required. API
is undocumented.

## `wikimedia_commons_workflow`

**Content Provider:** Wikimedia Commons

**ETL Process:** Use the API to identify all CC-licensed images.

**Output:** TSV file containing the image, the respective meta-data.

### Notes

Rate limit of no more than 200 requests/second, and we are required to set a
unique User-Agent field
([docs](https://www.mediawiki.org/wiki/Wikimedia_REST_API#Terms_and_conditions)).

Wikimedia Commons uses an implementation of the
[MediaWiki API](https://www.mediawiki.org/wiki/API:Main_page). This API is
incredibly complex in the level of configuration you can provide when querying,
and as such it can also be quite abstruse. The most straightforward docs can be
found on the
[Wikimedia website directly](https://commons.wikimedia.org/w/api.php?action=help&modules=query),
as these show all the parameters available. Specifications on queries can also
be found on the [query page](https://www.mediawiki.org/wiki/API:Query).

Different kinds of queries can be made against the API using "modules", we use
the [allimages module](https://www.mediawiki.org/wiki/API:Allimages), which lets
us search for images in a given time range (see `"generator": "allimages"` in
the query params).

Many queries will return results in batches, with the API supplying a "continue"
token. This token is used on subsequent calls to tell the API where to start the
next set of results from; it functions as a page offset
([docs](https://www.mediawiki.org/wiki/API:Query#Continuing_queries)).

We can also specify what kinds of information we want for the query. Wikimedia
has a massive amount of data on it, so it only returns what we ask for. The
fields that are returned are defined by the
[properties](https://www.mediawiki.org/wiki/API:Properties) or "props"
parameter. Sub-properties can also be defined, with the parameter name of the
sub-property determined by an abbreviation of the higher-level property. For
instance, if our property is "imageinfo" and we want to set sub-property values,
we would define those in "iiprops".

The data within a property is paginated as well, Wikimedia will handle iteration
through the property sub-pages using the "continue" token
([see here for more details](https://www.mediawiki.org/wiki/API:Properties#Additional_notes)).

Depending on the kind of property data that's being returned, it's possible for
the API to iterate extensively on a specific media item. What Wikimedia is
iterating over in these cases can be gleaned from the "continue" token. Those
tokens take the form of, as I understand it,
"<primary-iterator>||<next-iteration-prop>", paired with an "<XX>continue" value
for the property being iterated over. For example, if we're were iterating over
a set of image properties, the token might look like:

```
{
    "iicontinue": "The_Railway_Chronicle_1844.pdf|20221209222801",
    "gaicontinue": "20221209222614|NTUL-0527100_英國產業革命史略.pdf",
    "continue": "gaicontinue||globalusage",
}
```

In this case, we're iterating over the "global all images" generator
(gaicontinue) as our primary iterator, with the "image properties" (iicontinue)
as the secondary continue iterator. The "globalusage" property would be the next
property to iterate over. It's also possible for multiple sub-properties to be
iterated over simultaneously, in which case the "continue" token would not have
a secondary value (e.g. `gaicontinue||`).

In most runs, the "continue" key will be `gaicontinue||` after the first
request, which means that we have more than one batch to iterate over for the
primary iterator. Some days will have fewer images than the batch limit but
still have multiple batches of content on the secondary iterator, which means
the "continue" key may not have a primary iteration component (e.g.
`||globalusage`). This token can also be seen when the first request has more
data in the secondary iterator, before we've processed any data on the primary
iterator.

Occasionally, the ingester will come across a piece of media that has many
results for the property it's iterating over. An example of this can include an
item being on many pages, this it would have many "global usage" results. In
order to process the entire batch, we have to iterate over _all_ of the returned
results; Wikimedia does not provide a mechanism to "skip to the end" of a batch.
On numerous occasions, this iteration has been so extensive that the pull media
task has hit the task's timeout. To avoid this, we limit the number of
iterations we make for parsing through a sub-property's data. If we hit the
limit, we re-issue the original query _without_ requesting properties that
returned large amounts of data. Unfortunately, this means that we will **not**
have that property's data for these items the second time around (e.g.
popularity data if we needed to skip global usage). In the case of popularity,
especially since the problem with these images is that they're so popular, we
want to preserve that information where possible! So we cache the popularity
data from previous iterations and use it in subsequent ones if we come across
the same item again.

Below are some specific references to various properties, with examples for
cases where they might exceed the limit. Technically, it's feasible for almost
any property to exceed the limit, but these are the ones that we've seen in
practice.

#### `imageinfo`

[Docs](https://commons.wikimedia.org/w/api.php?action=help&modules=query%2Bimageinfo)

[Example where metadata has hundreds of data points](https://commons.wikimedia.org/wiki/File:The_Railway_Chronicle_1844.pdf#metadata)
(see "Metadata" table, which may need to be expanded).

For these requests, we can remove the `metadata` property from the `iiprops`
parameter to avoid this issue on subsequent iterations.

#### `globalusage`

[Docs](https://commons.wikimedia.org/w/api.php?action=help&modules=query%2Bglobalusage)

[Example where an image is used on almost every wiki](https://commons.wikimedia.org/w/index.php?curid=4298234).

For these requests, we can remove the `globalusage` property from the `prop`
parameter entirely and eschew the popularity data for these items.

## `wikimedia_reingestion_workflow`

**Content Provider:** Wikimedia Commons

**ETL Process:** Use the API to identify all CC-licensed images.

**Output:** TSV file containing the image, the respective meta-data.

### Notes

Rate limit of no more than 200 requests/second, and we are required to set a
unique User-Agent field
([docs](https://www.mediawiki.org/wiki/Wikimedia_REST_API#Terms_and_conditions)).

Wikimedia Commons uses an implementation of the
[MediaWiki API](https://www.mediawiki.org/wiki/API:Main_page). This API is
incredibly complex in the level of configuration you can provide when querying,
and as such it can also be quite abstruse. The most straightforward docs can be
found on the
[Wikimedia website directly](https://commons.wikimedia.org/w/api.php?action=help&modules=query),
as these show all the parameters available. Specifications on queries can also
be found on the [query page](https://www.mediawiki.org/wiki/API:Query).

Different kinds of queries can be made against the API using "modules", we use
the [allimages module](https://www.mediawiki.org/wiki/API:Allimages), which lets
us search for images in a given time range (see `"generator": "allimages"` in
the query params).

Many queries will return results in batches, with the API supplying a "continue"
token. This token is used on subsequent calls to tell the API where to start the
next set of results from; it functions as a page offset
([docs](https://www.mediawiki.org/wiki/API:Query#Continuing_queries)).

We can also specify what kinds of information we want for the query. Wikimedia
has a massive amount of data on it, so it only returns what we ask for. The
fields that are returned are defined by the
[properties](https://www.mediawiki.org/wiki/API:Properties) or "props"
parameter. Sub-properties can also be defined, with the parameter name of the
sub-property determined by an abbreviation of the higher-level property. For
instance, if our property is "imageinfo" and we want to set sub-property values,
we would define those in "iiprops".

The data within a property is paginated as well, Wikimedia will handle iteration
through the property sub-pages using the "continue" token
([see here for more details](https://www.mediawiki.org/wiki/API:Properties#Additional_notes)).

Depending on the kind of property data that's being returned, it's possible for
the API to iterate extensively on a specific media item. What Wikimedia is
iterating over in these cases can be gleaned from the "continue" token. Those
tokens take the form of, as I understand it,
"<primary-iterator>||<next-iteration-prop>", paired with an "<XX>continue" value
for the property being iterated over. For example, if we're were iterating over
a set of image properties, the token might look like:

```
{
    "iicontinue": "The_Railway_Chronicle_1844.pdf|20221209222801",
    "gaicontinue": "20221209222614|NTUL-0527100_英國產業革命史略.pdf",
    "continue": "gaicontinue||globalusage",
}
```

In this case, we're iterating over the "global all images" generator
(gaicontinue) as our primary iterator, with the "image properties" (iicontinue)
as the secondary continue iterator. The "globalusage" property would be the next
property to iterate over. It's also possible for multiple sub-properties to be
iterated over simultaneously, in which case the "continue" token would not have
a secondary value (e.g. `gaicontinue||`).

In most runs, the "continue" key will be `gaicontinue||` after the first
request, which means that we have more than one batch to iterate over for the
primary iterator. Some days will have fewer images than the batch limit but
still have multiple batches of content on the secondary iterator, which means
the "continue" key may not have a primary iteration component (e.g.
`||globalusage`). This token can also be seen when the first request has more
data in the secondary iterator, before we've processed any data on the primary
iterator.

Occasionally, the ingester will come across a piece of media that has many
results for the property it's iterating over. An example of this can include an
item being on many pages, this it would have many "global usage" results. In
order to process the entire batch, we have to iterate over _all_ of the returned
results; Wikimedia does not provide a mechanism to "skip to the end" of a batch.
On numerous occasions, this iteration has been so extensive that the pull media
task has hit the task's timeout. To avoid this, we limit the number of
iterations we make for parsing through a sub-property's data. If we hit the
limit, we re-issue the original query _without_ requesting properties that
returned large amounts of data. Unfortunately, this means that we will **not**
have that property's data for these items the second time around (e.g.
popularity data if we needed to skip global usage). In the case of popularity,
especially since the problem with these images is that they're so popular, we
want to preserve that information where possible! So we cache the popularity
data from previous iterations and use it in subsequent ones if we come across
the same item again.

Below are some specific references to various properties, with examples for
cases where they might exceed the limit. Technically, it's feasible for almost
any property to exceed the limit, but these are the ones that we've seen in
practice.

#### `imageinfo`

[Docs](https://commons.wikimedia.org/w/api.php?action=help&modules=query%2Bimageinfo)

[Example where metadata has hundreds of data points](https://commons.wikimedia.org/wiki/File:The_Railway_Chronicle_1844.pdf#metadata)
(see "Metadata" table, which may need to be expanded).

For these requests, we can remove the `metadata` property from the `iiprops`
parameter to avoid this issue on subsequent iterations.

#### `globalusage`

[Docs](https://commons.wikimedia.org/w/api.php?action=help&modules=query%2Bglobalusage)

[Example where an image is used on almost every wiki](https://commons.wikimedia.org/w/index.php?curid=4298234).

For these requests, we can remove the `globalusage` property from the `prop`
parameter entirely and eschew the popularity data for these items.

## `wordpress_workflow`

Content Provider: WordPress Photo Directory

ETL Process: Use the API to identify all openly licensed media.

Output: TSV file containing the media metadata.

Notes: https://wordpress.org/photos/wp-json/wp/v2 Provide photos, media, users
and more related resources. No rate limit specified.
