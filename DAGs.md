# DAGs

_Note: this document is auto-generated and should not be manually edited_

This document describes the DAGs available along with pertinent DAG information and
the DAG's documentation.

The DAGs are shown in two forms:

 - [DAGs by Type](#dags-by-type)
 - [Individual DAG documentation](#dag-documentation)

# DAGs by Type

The following are DAGs grouped by their primary tag:

 1. [Commoncrawl](#commoncrawl)
 1. [Data Refresh](#data_refresh)
 1. [Database](#database)
 1. [Maintenance](#maintenance)
 1. [Oauth](#oauth)
 1. [Provider](#provider)
 1. [Provider Reingestion](#provider-reingestion)

## Commoncrawl

| DAG ID | Schedule Interval |
| --- | --- |
| `commoncrawl_etl_workflow` | `0 0 * * 1` |
| `sync_commoncrawl_workflow` | `0 16 15 * *` |



## Data Refresh

| DAG ID | Schedule Interval |
| --- | --- |
| [`audio_data_refresh`](#audio_data_refresh) | `@weekly` |
| [`image_data_refresh`](#image_data_refresh) | `@weekly` |



## Database

| DAG ID | Schedule Interval |
| --- | --- |
| `image_expiration_workflow` | `None` |
| [`recreate_audio_popularity_calculation`](#recreate_audio_popularity_calculation) | `None` |
| [`recreate_image_popularity_calculation`](#recreate_image_popularity_calculation) | `None` |
| [`report_pending_reported_media`](#report_pending_reported_media) | `@weekly` |



## Maintenance

| DAG ID | Schedule Interval |
| --- | --- |
| [`airflow_log_cleanup`](#airflow_log_cleanup) | `@weekly` |
| [`check_silenced_dags`](#check_silenced_dags) | `@weekly` |
| [`pr_review_reminders`](#pr_review_reminders) | `0 0 * * 1-5` |



## Oauth

| DAG ID | Schedule Interval |
| --- | --- |
| [`oauth2_authorization`](#oauth2_authorization) | `None` |
| [`oauth2_token_refresh`](#oauth2_token_refresh) | `0 */12 * * *` |



## Provider

| DAG ID | Schedule Interval | Dated | Media Type(s) |
| --- | --- | --- | --- |
| `brooklyn_museum_workflow` | `@monthly` | `False` | image |
| `cleveland_museum_workflow` | `@monthly` | `False` | image |
| [`europeana_workflow`](#europeana_workflow) | `@daily` | `True` | image |
| `finnish_museums_workflow` | `@monthly` | `False` | image |
| [`flickr_workflow`](#flickr_workflow) | `@daily` | `True` | image |
| [`freesound_workflow`](#freesound_workflow) | `@monthly` | `False` | audio |
| [`inaturalist_workflow`](#inaturalist_workflow) | `@monthly` | `False` | image |
| [`jamendo_workflow`](#jamendo_workflow) | `@monthly` | `False` | audio |
| [`metropolitan_museum_workflow`](#metropolitan_museum_workflow) | `@daily` | `True` | image |
| `museum_victoria_workflow` | `@monthly` | `False` | image |
| `nypl_workflow` | `@monthly` | `False` | image |
| [`phylopic_workflow`](#phylopic_workflow) | `@daily` | `True` | image |
| [`rawpixel_workflow`](#rawpixel_workflow) | `@monthly` | `False` | image |
| `science_museum_workflow` | `@monthly` | `False` | image |
| [`smithsonian_workflow`](#smithsonian_workflow) | `@weekly` | `False` | image |
| `smk_workflow` | `@monthly` | `False` | image |
| [`stocksnap_workflow`](#stocksnap_workflow) | `@monthly` | `False` | image |
| [`wikimedia_commons_workflow`](#wikimedia_commons_workflow) | `@daily` | `True` | image, audio |
| [`wordpress_workflow`](#wordpress_workflow) | `@monthly` | `False` | image |



## Provider Reingestion

| DAG ID | Schedule Interval |
| --- | --- |
| `europeana_reingestion_workflow` | `@weekly` |
| `flickr_reingestion_workflow` | `@weekly` |
| `metropolitan_museum_reingestion_workflow` | `@weekly` |
| `phylopic_reingestion_workflow` | `@weekly` |
| `wikimedia_reingestion_workflow` | `@weekly` |


# DAG documentation

The following is documentation associated with each DAG (where available):

 1. [`airflow_log_cleanup`](#airflow_log_cleanup)
 1. [`audio_data_refresh`](#audio_data_refresh)
 1. [`check_silenced_dags`](#check_silenced_dags)
 1. [`europeana_workflow`](#europeana_workflow)
 1. [`flickr_workflow`](#flickr_workflow)
 1. [`freesound_workflow`](#freesound_workflow)
 1. [`image_data_refresh`](#image_data_refresh)
 1. [`inaturalist_workflow`](#inaturalist_workflow)
 1. [`jamendo_workflow`](#jamendo_workflow)
 1. [`metropolitan_museum_workflow`](#metropolitan_museum_workflow)
 1. [`oauth2_authorization`](#oauth2_authorization)
 1. [`oauth2_token_refresh`](#oauth2_token_refresh)
 1. [`phylopic_workflow`](#phylopic_workflow)
 1. [`pr_review_reminders`](#pr_review_reminders)
 1. [`rawpixel_workflow`](#rawpixel_workflow)
 1. [`recreate_audio_popularity_calculation`](#recreate_audio_popularity_calculation)
 1. [`recreate_image_popularity_calculation`](#recreate_image_popularity_calculation)
 1. [`report_pending_reported_media`](#report_pending_reported_media)
 1. [`smithsonian_workflow`](#smithsonian_workflow)
 1. [`stocksnap_workflow`](#stocksnap_workflow)
 1. [`wikimedia_commons_workflow`](#wikimedia_commons_workflow)
 1. [`wordpress_workflow`](#wordpress_workflow)


## `airflow_log_cleanup`


A maintenance workflow that you can deploy into Airflow to periodically clean
out the task logs to avoid those getting too big. By default, this will also
clean child process logs from the 'scheduler' directory.

Can remove all log files by setting "maxLogAgeInDays" to -1.
If you want to test the DAG in the Airflow Web UI, you can also set
enableDelete to `false`, and then you will see a list of log folders
that can be deleted, but will not actually delete them.

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
This file generates our data refresh DAGs using a factory function.
For the given media type these DAGs will first refresh the popularity data,
then initiate a data refresh on the data refresh server and await the
success or failure of that task.

Popularity data for each media type is collated in a materialized view. Before
initiating a data refresh, the DAG will first refresh the view in order to
update popularity data for records that have been ingested since the last refresh.
On the first run of the month, the DAG will also refresh the underlying tables,
including the percentile values and any new popularity metrics. The DAG can also
be run with the `force_refresh_metrics` option to run this refresh after the first
of the month.

Once this step is complete, the data refresh can be initiated. A data refresh
occurs on the data refresh server in the openverse-api project. This is a task
which imports data from the upstream Catalog database into the API, copies contents
to a new Elasticsearch index, and finally makes the index "live". This process is
necessary to make new content added to the Catalog by our provider DAGs available
to the API. You can read more in the [README](
https://github.com/WordPress/openverse-api/blob/main/ingestion_server/README.md
) Importantly, the data refresh TaskGroup is also configured to handle concurrency
requirements of the data refresh server.

You can find more background information on this process in the following
issues and related PRs:

- [[Feature] Data refresh orchestration DAG](
https://github.com/WordPress/openverse-catalog/issues/353)
- [[Feature] Merge popularity calculations and data refresh into a single DAG](
https://github.com/WordPress/openverse-catalog/issues/453)


## `check_silenced_dags`


Checks for DAGs that have silenced Slack alerts which may need to be turned back
on.

When a DAG has known failures, it can be ommitted from Slack error reporting by adding
an entry to the `SILENCED_SLACK_NOTIFICATIONS` Airflow variable. This is a dictionary
where thekey is the `dag_id` of the affected DAG, and the value is a list of
SilencedSlackNotifications (which map silenced notifications to GitHub URLs) for that
DAG.

The `check_silenced_dags` DAG iterates over the entries in the
`SILENCED_SLACK_NOTIFICATIONS` configuration and verifies that the associated GitHub
issues are still open. If an issue has been closed, it is assumed that the DAG should
have Slack reporting reenabled, and an alert is sent to prompt manual update of the
configuration. This prevents developers from forgetting to reenable Slack reporting
after the issue has been resolved.

The DAG runs weekly.


## `europeana_workflow`


Content Provider:       Europeana

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the images and the
                        respective meta-data.

Notes:                  https://www.europeana.eu/api/v2/search.json


## `flickr_workflow`


Content Provider:       Flickr

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the images and the
                        respective meta-data.

Notes:                  https://www.flickr.com/help/terms/api
                        Rate limit: 3600 requests per hour.


## `freesound_workflow`


Content Provider:       Freesound

ETL Process:            Use the API to identify all CC-licensed images.

Output:                 TSV file containing the image, the respective
                        meta-data.

Notes:                  https://freesound.org/apiv2/search/text'
                        No rate limit specified.
                        This script can be run either to ingest the full dataset or
                        as a dated DAG.


## `image_data_refresh`

### Data Refresh DAG Factory
This file generates our data refresh DAGs using a factory function.
For the given media type these DAGs will first refresh the popularity data,
then initiate a data refresh on the data refresh server and await the
success or failure of that task.

Popularity data for each media type is collated in a materialized view. Before
initiating a data refresh, the DAG will first refresh the view in order to
update popularity data for records that have been ingested since the last refresh.
On the first run of the month, the DAG will also refresh the underlying tables,
including the percentile values and any new popularity metrics. The DAG can also
be run with the `force_refresh_metrics` option to run this refresh after the first
of the month.

Once this step is complete, the data refresh can be initiated. A data refresh
occurs on the data refresh server in the openverse-api project. This is a task
which imports data from the upstream Catalog database into the API, copies contents
to a new Elasticsearch index, and finally makes the index "live". This process is
necessary to make new content added to the Catalog by our provider DAGs available
to the API. You can read more in the [README](
https://github.com/WordPress/openverse-api/blob/main/ingestion_server/README.md
) Importantly, the data refresh TaskGroup is also configured to handle concurrency
requirements of the data refresh server.

You can find more background information on this process in the following
issues and related PRs:

- [[Feature] Data refresh orchestration DAG](
https://github.com/WordPress/openverse-catalog/issues/353)
- [[Feature] Merge popularity calculations and data refresh into a single DAG](
https://github.com/WordPress/openverse-catalog/issues/453)


## `inaturalist_workflow`


Provider:   iNaturalist

Output:     TSV file containing the media metadata.

Notes:      [The iNaturalist API is not intended for data scraping.]
            (https://api.inaturalist.org/v1/docs/)

            [But there is a full dump intended for sharing on S3.]
            (https://github.com/inaturalist/inaturalist-open-data/tree/documentation/Metadata)

            Because these are very large normalized tables, as opposed to more document
            oriented API responses, we found that bringing the data into postgres first
            was the most effective approach. [More detail in slack here.]
            (https://wordpress.slack.com/archives/C02012JB00N/p1653145643080479?thread_ts=1653082292.714469&cid=C02012JB00N)

            We use the table structure defined [here,]
            (https://github.com/inaturalist/inaturalist-open-data/blob/main/Metadata/structure.sql)
            except for adding ancestry tags to the taxa table.


## `jamendo_workflow`


Content Provider:       Jamendo

ETL Process:            Use the API to identify all CC-licensed audio.

Output:                 TSV file containing the audio meta-data.

Notes:                  https://api.jamendo.com/v3.0/tracks/
                        35,000 requests per month for non-commercial apps
                        Jamendo Music has more than 500,000 tracks shared by
                        40,000 artists from over 150 countries all over
                        the world.
                        Audio quality: uploaded as WAV/ FLAC/ AIFF
                        bit depth: 16/24
                        sample rate: 44.1 or 48 kHz
                        channels: 1/2


## `metropolitan_museum_workflow`


Content Provider:       Metropolitan Museum of Art

ETL Process:            Use the API to identify all CC0 artworks.

Output:                 TSV file containing the image, their respective
                        meta-data.

Notes:                  https://metmuseum.github.io/#search
                        "Please limit requests to 80 requests per second." May need to
                        bump up the delay (e.g. to 3 seconds), to avoid of blocking
                        during local development testing.

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



## `oauth2_authorization`

### OAuth Provider Authorization

**Author**: Madison Swain-Bowden

**Created**: 2021-10-13



Iterates through all the OAuth2 providers and attempts to authorize them using tokens
found in the in the `OAUTH2_AUTH_KEYS` Variable. Once authorization has been
completed successfully, the auth token is removed from that Variable. The authorization
will create an access/refresh token pair in the `OAUTH2_ACCESS_TOKENS` Variable.

**Current Providers**:

- Freesound


## `oauth2_token_refresh`

### OAuth Provider Token Refresh

**Author**: Madison Swain-Bowden

**Created**: 2021-10-13


Iterates through all OAuth2 providers and attempts to refresh the access token using
the refresh token stored in the `OAUTH2_ACCESS_TOKENS` Variable. This DAG will
update the tokens stored in the Variable upon successful refresh.

**Current Providers**:

- Freesound


## `phylopic_workflow`


Content Provider:       PhyloPic

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the image,
                        their respective meta-data.

Notes:                  http://phylopic.org/api/
                        No rate limit specified.


## `pr_review_reminders`


Iterates through open PRs in our repositories and pings assigned reviewers
who have not yet approved the PR or explicitly requested changes.

This DAG runs daily and pings on the following schedule based on priority label:

| priority | days |
| --- | --- |
| critical | 1 day |
| high | >2 days |
| medium | >4 days |
| low | >7 days |

The DAG does not ping on Saturday and Sunday and accounts for weekend days
when determining how much time has passed since the review.

Unfortunately the DAG does not know when someone is on vacation. It is up to the
author of the PR to re-assign review if one of the randomly selected reviewers
is unavailable for the time period during which the PR should be reviewed.


## `rawpixel_workflow`


Content Provider:       Rawpixel

ETL Process:            Use the API to identify all CC-licensed images.

Output:                 TSV file containing the image meta-data.

Notes:                  Rawpixel has given Openverse beta access to their API.
                        This API is undocumented, and we will need to contact Rawpixel
                        directly if we run into any issues.
                        The public API max results range is limited to 100,000 results,
                        although the API key we've been given can circumvent this limit.
                        https://www.rawpixel.com/api/v1/search?tags=$publicdomain&page=1&pagesize=100


## `recreate_audio_popularity_calculation`


This file generates Apache Airflow DAGs that, for the given media type,
completely wipe out the PostgreSQL relations and functions involved in
calculating our standardized popularity metric. It then recreates relations
and functions to make the calculation, and performs an initial calculation.
The results are available in the materialized view for that media type.

These DAGs are not on a schedule, and should only be run manually when new
SQL code is deployed for the calculation.


## `recreate_image_popularity_calculation`


This file generates Apache Airflow DAGs that, for the given media type,
completely wipe out the PostgreSQL relations and functions involved in
calculating our standardized popularity metric. It then recreates relations
and functions to make the calculation, and performs an initial calculation.
The results are available in the materialized view for that media type.

These DAGs are not on a schedule, and should only be run manually when new
SQL code is deployed for the calculation.


## `report_pending_reported_media`

### Report Pending Reported Media DAG
This DAG checks for any user-reported media pending manual review, and alerts
via Slack.

Media may be reported for mature content or copyright infringement, for
example. Once reported, these require manual review through the Django Admin to
determine whether further action (such as deindexing the record) needs to be
taken. If a record has been reported multiple times, it only needs to be
reviewed once and so is only counted once in the reporting by this DAG.


## `smithsonian_workflow`


Content Provider:   Smithsonian

ETL Process:        Use the API to identify all CC licensed images.

Output:             TSV file containing the images and the respective meta-data.

Notes:              https://api.si.edu/openaccess/api/v1.0/search


## `stocksnap_workflow`


Content Provider:       StockSnap

ETL Process:            Use the API to identify all CC-licensed images.

Output:                 TSV file containing the image, the respective meta-data.

Notes:                  https://stocksnap.io/api/load-photos/date/desc/1
                        https://stocksnap.io/faq
                        All images are licensed under CC0.
                        No rate limits or authorization required.
                        API is undocumented.


## `wikimedia_commons_workflow`


Content Provider:       Wikimedia Commons

ETL Process:            Use the API to identify all CC-licensed images.

Output:                 TSV file containing the image, the respective
                        meta-data.

Notes:                  https://commons.wikimedia.org/wiki/API:Main_page
                        No rate limit specified.


## `wordpress_workflow`


Content Provider:       WordPress Photo Directory

ETL Process:            Use the API to identify all openly licensed media.

Output:                 TSV file containing the media metadata.

Notes:                  https://wordpress.org/photos/wp-json/wp/v2
                        Provide photos, media, users and more related resources.
                        No rate limit specified.
