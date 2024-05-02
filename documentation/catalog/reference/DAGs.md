# DAGs

_Note: this document is auto-generated and should not be manually edited_

This document describes the DAGs available along with pertinent DAG information
and the DAG's documentation.

The DAGs are shown in two forms:

- [DAGs by Type](#dags-by-type)
- [Individual DAG documentation](#dag-documentation)

## DAGs by Type

The following are DAGs grouped by their primary tag:

1.  [Data Normalization](#data-normalization)
1.  [Data Refresh](#data-refresh)
1.  [Database](#database)
1.  [Elasticsearch](#elasticsearch)
1.  [Maintenance](#maintenance)
1.  [Oauth](#oauth)
1.  [Popularity Refresh](#popularity-refresh)
1.  [Provider](#provider)
1.  [Provider Reingestion](#provider-reingestion)

### Data Normalization

| DAG ID                                | Schedule Interval |
| ------------------------------------- | ----------------- |
| [`add_license_url`](#add_license_url) | `None`            |

### Data Refresh

| DAG ID                                                                  | Schedule Interval |
| ----------------------------------------------------------------------- | ----------------- |
| [`create_filtered_audio_index`](#create_filtered_media_type_index)      | `None`            |
| [`create_filtered_image_index`](#create_filtered_media_type_index)      | `None`            |
| [`production_audio_data_refresh`](#environment_media_type_data_refresh) | `0 0 * * 1`       |
| [`production_image_data_refresh`](#environment_media_type_data_refresh) | `0 0 * * 1`       |
| [`staging_audio_data_refresh`](#environment_media_type_data_refresh)    | `0 0 * * 1`       |
| [`staging_image_data_refresh`](#environment_media_type_data_refresh)    | `0 0 * * 1`       |
| [`audio_data_refresh`](#media_type_data_refresh)                        | `0 0 * * 1`       |
| [`image_data_refresh`](#media_type_data_refresh)                        | `0 0 * * 1`       |

### Database

| DAG ID                                                                                 | Schedule Interval |
| -------------------------------------------------------------------------------------- | ----------------- |
| [`batched_update`](#batched_update)                                                    | `None`            |
| [`delete_records`](#delete_records)                                                    | `None`            |
| [`recreate_full_staging_index`](#recreate_full_staging_index)                          | `None`            |
| [`recreate_audio_popularity_calculation`](#recreate_media_type_popularity_calculation) | `None`            |
| [`recreate_image_popularity_calculation`](#recreate_media_type_popularity_calculation) | `None`            |
| [`report_pending_reported_media`](#report_pending_reported_media)                      | `@weekly`         |
| [`staging_database_restore`](#staging_database_restore)                                | `@monthly`        |

### Elasticsearch

| DAG ID                                                                                           | Schedule Interval |
| ------------------------------------------------------------------------------------------------ | ----------------- |
| [`create_new_production_es_index`](#create_new_environment_es_index)                             | `None`            |
| [`create_new_staging_es_index`](#create_new_environment_es_index)                                | `None`            |
| [`create_proportional_by_source_staging_index`](#create_proportional_by_source_staging_index)    | `None`            |
| [`point_production_es_alias`](#point_environment_es_alias)                                       | `None`            |
| [`point_staging_es_alias`](#point_environment_es_alias)                                          | `None`            |
| [`production_elasticsearch_cluster_healthcheck`](#environment_elasticsearch_cluster_healthcheck) | `*/15 * * * *`    |
| [`staging_elasticsearch_cluster_healthcheck`](#environment_elasticsearch_cluster_healthcheck)    | `*/15 * * * *`    |

### Maintenance

| DAG ID                                                                      | Schedule Interval |
| --------------------------------------------------------------------------- | ----------------- |
| [`airflow_log_cleanup`](#airflow_log_cleanup)                               | `@weekly`         |
| [`check_silenced_dags`](#check_silenced_dags)                               | `@weekly`         |
| [`flickr_audit_sub_provider_workflow`](#flickr_audit_sub_provider_workflow) | `@monthly`        |
| [`pr_review_reminders`](#pr_review_reminders)                               | `0 0 * * 1-5`     |
| [`rotate_db_snapshots`](#rotate_db_snapshots)                               | `0 0 * * 6`       |

### Oauth

| DAG ID                                          | Schedule Interval |
| ----------------------------------------------- | ----------------- |
| [`oauth2_authorization`](#oauth2_authorization) | `None`            |
| [`oauth2_token_refresh`](#oauth2_token_refresh) | `0 */12 * * *`    |

### Popularity Refresh

| DAG ID                                                       | Schedule Interval |
| ------------------------------------------------------------ | ----------------- |
| [`audio_popularity_refresh`](#media_type_popularity_refresh) | `@monthly`        |
| [`image_popularity_refresh`](#media_type_popularity_refresh) | `@monthly`        |

### Provider

| DAG ID                                                          | Schedule Interval | Dated   | Media Type(s) |
| --------------------------------------------------------------- | ----------------- | ------- | ------------- |
| [`auckland_museum_workflow`](#auckland_museum_workflow)         | `@daily`          | `True`  | image         |
| `brooklyn_museum_workflow`                                      | `@monthly`        | `False` | image         |
| [`cc_mixter_workflow`](#cc_mixter_workflow)                     | `@monthly`        | `False` | audio         |
| `cleveland_museum_workflow`                                     | `@monthly`        | `False` | image         |
| [`europeana_workflow`](#europeana_workflow)                     | `@daily`          | `True`  | image         |
| [`finnish_museums_workflow`](#finnish_museums_workflow)         | `@daily`          | `True`  | image         |
| [`flickr_workflow`](#flickr_workflow)                           | `@daily`          | `True`  | image         |
| [`freesound_workflow`](#freesound_workflow)                     | `@quarterly`      | `False` | audio         |
| [`inaturalist_workflow`](#inaturalist_workflow)                 | `0 0 2 * *`       | `False` | image         |
| [`jamendo_workflow`](#jamendo_workflow)                         | `@monthly`        | `False` | audio         |
| [`justtakeitfree_workflow`](#justtakeitfree_workflow)           | `@monthly`        | `False` | image         |
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
| [`wordpress_workflow`](#wordpress_workflow)                     | `@weekly`         | `False` | image         |

### Provider Reingestion

| DAG ID                                                                      | Schedule Interval |
| --------------------------------------------------------------------------- | ----------------- |
| [`flickr_reingestion_workflow`](#flickr_workflow)                           | `@weekly`         |
| [`metropolitan_museum_reingestion_workflow`](#metropolitan_museum_workflow) | `@weekly`         |
| [`phylopic_reingestion_workflow`](#phylopic_workflow)                       | `@weekly`         |
| [`wikimedia_reingestion_workflow`](#wikimedia_commons_workflow)             | `@weekly`         |

## DAG documentation

The following is documentation associated with each DAG (where available):

1.  [`add_license_url`](#add_license_url)
1.  [`airflow_log_cleanup`](#airflow_log_cleanup)
1.  [`auckland_museum_workflow`](#auckland_museum_workflow)
1.  [`batched_update`](#batched_update)
1.  [`cc_mixter_workflow`](#cc_mixter_workflow)
1.  [`check_silenced_dags`](#check_silenced_dags)
1.  [`create_filtered_audio_index`](#create_filtered_media_type_index)
1.  [`create_filtered_image_index`](#create_filtered_media_type_index)
1.  [`create_new_production_es_index`](#create_new_environment_es_index)
1.  [`create_new_staging_es_index`](#create_new_environment_es_index)
1.  [`create_proportional_by_source_staging_index`](#create_proportional_by_source_staging_index)
1.  [`delete_records`](#delete_records)
1.  [`europeana_workflow`](#europeana_workflow)
1.  [`finnish_museums_workflow`](#finnish_museums_workflow)
1.  [`flickr_audit_sub_provider_workflow`](#flickr_audit_sub_provider_workflow)
1.  [`flickr_reingestion_workflow`](#flickr_workflow)
1.  [`flickr_workflow`](#flickr_workflow)
1.  [`freesound_workflow`](#freesound_workflow)
1.  [`inaturalist_workflow`](#inaturalist_workflow)
1.  [`jamendo_workflow`](#jamendo_workflow)
1.  [`justtakeitfree_workflow`](#justtakeitfree_workflow)
1.  [`metropolitan_museum_reingestion_workflow`](#metropolitan_museum_workflow)
1.  [`metropolitan_museum_workflow`](#metropolitan_museum_workflow)
1.  [`nappy_workflow`](#nappy_workflow)
1.  [`oauth2_authorization`](#oauth2_authorization)
1.  [`oauth2_token_refresh`](#oauth2_token_refresh)
1.  [`phylopic_reingestion_workflow`](#phylopic_workflow)
1.  [`phylopic_workflow`](#phylopic_workflow)
1.  [`point_production_es_alias`](#point_environment_es_alias)
1.  [`point_staging_es_alias`](#point_environment_es_alias)
1.  [`pr_review_reminders`](#pr_review_reminders)
1.  [`rawpixel_workflow`](#rawpixel_workflow)
1.  [`recreate_full_staging_index`](#recreate_full_staging_index)
1.  [`recreate_audio_popularity_calculation`](#recreate_media_type_popularity_calculation)
1.  [`recreate_image_popularity_calculation`](#recreate_media_type_popularity_calculation)
1.  [`report_pending_reported_media`](#report_pending_reported_media)
1.  [`rotate_db_snapshots`](#rotate_db_snapshots)
1.  [`science_museum_workflow`](#science_museum_workflow)
1.  [`smithsonian_workflow`](#smithsonian_workflow)
1.  [`smk_workflow`](#smk_workflow)
1.  [`staging_database_restore`](#staging_database_restore)
1.  [`stocksnap_workflow`](#stocksnap_workflow)
1.  [`wikimedia_commons_workflow`](#wikimedia_commons_workflow)
1.  [`wikimedia_reingestion_workflow`](#wikimedia_commons_workflow)
1.  [`wordpress_workflow`](#wordpress_workflow)
1.  [`production_elasticsearch_cluster_healthcheck`](#environment_elasticsearch_cluster_healthcheck)
1.  [`staging_elasticsearch_cluster_healthcheck`](#environment_elasticsearch_cluster_healthcheck)
1.  [`production_audio_data_refresh`](#environment_media_type_data_refresh)
1.  [`production_image_data_refresh`](#environment_media_type_data_refresh)
1.  [`staging_audio_data_refresh`](#environment_media_type_data_refresh)
1.  [`staging_image_data_refresh`](#environment_media_type_data_refresh)
1.  [`audio_data_refresh`](#media_type_data_refresh)
1.  [`image_data_refresh`](#media_type_data_refresh)
1.  [`audio_popularity_refresh`](#media_type_popularity_refresh)
1.  [`image_popularity_refresh`](#media_type_popularity_refresh)

### `add_license_url`

#### Add license URL

Add `license_url` to rows without one in their `meta_data` fields. This PR
merges the `meta_data` value with "{license_url: https://... }", where the url
is constructed from the `license` and `license_version` columns.

This is a maintenance DAG that should be run once.

----

### `airflow_log_cleanup`

#### Clean up airflow logs

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

----

### `auckland_museum_workflow`

Content Provider: Auckland War Memorial Museum Tāmaki Paenga Hira

ETL Process: Use the API to identify all CC licensed media.

Output: TSV file containing the media and the respective meta-data.

Notes: <https://api.aucklandmuseum.com/>

Resource: <https://api.aucklandmuseum.com/>
<https://github.com/AucklandMuseum/API/wiki/Tutorial>

| Resource     | Requests per second | Requests per day |
| ------------ | ------------------- | ---------------- |
| /search, /id | 10                  | 1000             |
| /id/media    | 10                  | 1000             |

----

### `batched_update`

#### Batched Update DAG

This DAG is used to run a batched SQL update on a media table in the Catalog
database. It is automatically triggered by the `popularity_refresh` DAGs to
refresh popularity data using newly calculated constants, but can also be
triggered manually with custom SQL operations.

The DAG must be run with a valid dag_run configuration specifying the SQL
commands to be run. The DAG will then split the rows to be updated into batches,
and report to Slack when all batches have been updated. It handles all
deadlocking and timeout concerns, ensuring that the provided SQL is run without
interfering with ingestion. For more information, see the implementation plan:
<https://docs.openverse.org/projects/proposals/popularity_optimizations/20230420-implementation_plan_popularity_optimizations.html#special-considerations-avoiding-deadlocks-and-timeouts>

By default the DAG will run as a dry_run, logging the generated SQL but not
actually running it. To actually perform the update, the `dry_run` parameter
must be explicitly set to `false` in the configuration.

Required Dagrun Configuration parameters:

- query_id: a string identifier which will be appended to temporary table used
  in the update
- table_name: the name of the table to update. Must be a valid media table
- select_query: a SQL `WHERE` clause used to select the rows that will be
  updated
- update_query: the SQL `UPDATE` expression to be run on all selected rows

Optional params:

- dry_run: bool, whether to actually run the generated SQL. True by default.
- batch_size: int number of records to process in each batch. By default, 10_000
- update_timeout: int number of seconds to run an individual batch update before
  timing out. By default, 3600 (or one hour)
- resume_update: boolean indicating whether to attempt to resume an update using
  an existing temp table matching the `query_id`. When True, a new temp table is
  not created.

An example dag_run configuration used to set the thumbnails of all Flickr images
to null would look like this:

```
{
    "query_id": "my_flickr_query",
    "table_name": "image",
    "select_query": "WHERE provider='flickr'",
    "update_query": "SET thumbnail=null",
    "batch_size": 10,
    "dry_run": false
}
```

##### Automatic Failure Recovery

The `update_batches` task automatically keeps track of its progress in an
Airflow variable suffixed with the `query_id`. If the task fails, when it
retries it will pick up from where it left off. The DAG can still fail if the
configured number of retries are exceeded.

##### Manual Recovery

If the DAG does fail, the update can be manually resumed by triggering a new
DagRun with the same `query_id` and `update_query`, and enabling the
`resume_update` param. The DAG will skip temp table creation and resume progress
using the Airflow variable created on the previous run. **Manually managing this
Airflow variable should not be necessary.**

It is also possible to start an entirely new update using an existing temp
table, by setting the `resume_update` param to True but providing a new
`update_query`. The DAG will begin running the new update on records selected
from the existing temp table matching the `query_id`. This option should only be
used when the DagRun configuration needs to be changed after the table was
already created: for example, if there was a problem with the `update_query`
which caused DAG failures during the `update_batches` step. In this case, verify
that the `BATCH_START` var is set appropriately for your needs.

----

### `cc_mixter_workflow`

Content Provider: ccMixter

ETL Process: Use the API to identify all CC licensed media.

Output: TSV file containing the media and the respective meta-data.

Notes: Documentation: <https://ccmixter.org/query-api> ccMixter sends bad JSON
and extremely huge headers, both of which need workarounds that are handled by
this DAG.

----

### `check_silenced_dags`

#### Silenced DAGs check

Check for DAGs that have silenced Slack alerts or skipped errors which may need
to be turned back on.

When a DAG has known failures, it can be omitted from Slack error reporting by
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
forgetting to re-enable Slack reporting or turnoff error skipping after the
issue has been resolved.

The DAG runs weekly.

----

### `create_filtered_{media_type}_index`

#### Create filtered index DAG factory

This module creates the filtered index creation DAGs for each media type using a
factory function.

Filtered index creation is handled by the ingestion server. The DAGs generated
by the `create_filtered_index_creation_dag` function in this module are
responsible for triggering the ingestion server action to create and populate
the filtered index for a given media type. The DAG awaits the completion of the
filtered index creation and then points the filtered index alias for the media
type to the newly created index. They make use of the
`create_filtered_index_creation_task_groups` factory, which is also used by the
data refreshes to perform the same functions. The purpose of these DAGs is to
allow the filtered index creation steps to be run in isolation from the data
refresh.

##### When this DAG runs

The DAGs generated by the `create_filtered_index_creation_dag` can be used to
manually run the filtered index creation and promotion steps described above in
isolation from the rest of the data refresh. These DAGs also include checks to
ensure that race conditions with the data refresh DAGs are not encountered (see
`Race conditions` section below).

The DAGs generated in this module are on a `None` schedule and are only
triggered manually. This is primarily useful in two cases: for testing changes
to the filtered index creation; and for re-running filtered index creation if an
urgent change to the sensitive terms calls for an immediate recreation of the
filtered indexes.

##### Race conditions

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

1. The filtered index creation DAGs fail immediately if any of the DAGs that are
   tagged as part of the `production-es-concurrency` group (including the data
   refreshes) are currently running.
2. The data refresh DAGs will wait for any pre-existing filtered index creation
   DAG runs for the media type to finish before continuing.

This ensures that neither are depending on or modifying the origin indexes
critical for the creation of the filtered indexes.

----

### `create_new_{environment}_es_index`

#### Create New ES Index DAG

This file generates our Create New ES Index DAGs using a factory function. A
separate DAG is generated for the staging and production environments.

Each DAG can be used to create new Elasticsearch indices in their respective
environment, based on an existing index. The following configuration options are
available:

- `media_type` : media type for which to create the new index
- `index_suffix` : optional suffix to be added to the new index name. If not
  supplied, a creation timestamp is used.
- `source_index` : the existing index on which to base the new index, and from
  which to copy records
- `index_config` : a JSON object containing the configuration for the new index.
  By default, this will be merged into the configuration of the source index
  according to the merging policy documented below.
- `query` : an optional Elasticsearch query, used to filter the documents copied
  from the source index into the new index. If not supplied, all records are
  copied.
- `override_config`: boolean override; when True, the `index_config` will be
  used for the new index configuration _without_ merging any values from the
  source index config.
- `target_alias` : optional alias to be applied to the new index after
  reindexing. If the alias already applies to an existing index, it will be
  removed first.
- `should_delete_old_index`: whether to remove the index previously pointed to
  by the target_alias, if it exists. Defaults to False.

##### Merging policy

The configuration will be merged such that a leaf key in the `index_config`
overwrites the entire value present in the source configuration at that key. The
leaf values are merged naively, so a list for instance is replaced entirely
(rather than appending values). For example, if the base configuration is:

```
{
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "analysis": {
            "filter": {
                "stem_overrides": {
                    "type": "stemmer_override",
                    "rules": [
                        "animals => animal",
                        "animal => animal",
                        "anime => anime",
                        "animate => animate",
                        "animated => animate",
                        "universe => universe"
                    ]
                }
            }
        }
    }
}
```

And the `index_config` passed in is:

```
{
    "settings": {
        "index": {
            "number_of_shards": 2,
        },
        "analysis": {
            "filter": {
                "stem_overrides": {
                    "rules": ["crim => cribble"]
                }
            }
        }
    }
}
```

The resulting, merged configuration will be:

```
{
    "settings": {
        "index": {
            "number_of_shards": 2,
            "number_of_replicas": 1
        },
        "analysis": {
            "filter": {
                "stem_overrides": {
                    "type": "stemmer_override",
                    "rules": ["crim => cribble"]
                }
            }
        }
    }
}
```

##### Race conditions

Each DAG will fail immediately if any of the DAGs tagged as part of the
es-concurrency group for the DAG's environment is running. (E.g., the
`create_new_staging_es_index` DAG fails immediately if any DAGs tagged with
`staging-es-concurrency` are running.)

----

### `create_proportional_by_source_staging_index`

#### Create Proportional By Source Staging Index DAG

This DAG is used to create a new staging Elasticsearch index that is a subset of
a staging source index, such that the proportions of records by source in the
new index is equal to the proportions of records by source in the source index.

Required Dagrun Configuration parameters:

- media_type: The media type for which to create a new index.
- percentage_of_prod: A float indicating the proportion of items to take from
  each source from the total amount existing in the staging source index

Optional params:

- source_index: An existing staging Elasticsearch index to use as the basis for
  the new index. If not provided, the index aliased to `<media_type>-filtered`
  will be used.
- should_delete_old_index: If True, the index previously pointed to by the
  target alias (if one exists) will be deleted.

##### When this DAG runs

This DAG is on a `None` schedule and is run manually.

##### Race conditions

Because this DAG runs on the staging elasticsearch cluster, it does _not_
interfere with the production `data_refresh` or `create_filtered_index` DAGs.
However, it will fail immediately if any of the DAGs tagged as part of the
`staging-es-concurrency` group are running.

----

### `delete_records`

#### Delete Records DAG

This DAG is used to delete records from the Catalog media tables, after creating
a corresponding record in the associated `deleted_<media_type>` table for each
record to be deleted. It is important to note that records deleted by this DAG
will still be available in the API until the next data refresh runs.

Required Dagrun Configuration parameters:

- table_name: the name of the table to delete from. Must be a valid media table
- select_query: a SQL `WHERE` clause used to select the rows that will be
  deleted
- reason: a string explaining the reason for deleting the records. Ex
  ('deadlink')

An example dag_run configuration used to delete all records for the "foo" image
provider due to deadlinks would look like this:

```
{
    "table_name": "image",
    "select_query": "WHERE provider='foo'",
    "reason": "deadlink"
}
```

##### Multiple deletions

When a record is deleted, it is added to the corresponding Deleted Media table.
If the record is reingested back into the media table, the delete*records DAG
may be run additional times to delete the same record. When this occurs, only
one row will be kept in the Deleted Media table for the record (as uniquely
identified by the provider and foreign identifier pair). This row is not
updated, so the `deleted_on` time will reflect the \_first* time the record was
deleted.

When restoring records from the Deleted Media table, it is important to note
that these records have not been updated through reingestion, so fields such as
popularity data may be out of date.

##### Warnings

Presently, there is no logic to prevent records that have an entry in a Deleted
Media table from simply being reingested during provider ingestion. Therefore in
its current state, the DAG should _only_ be used to delete records that we can
guarantee will not be reingested (for example, because the provider is
archived).

This DAG does not have automated handling for deadlocks, so you must be certain
that records selected for deletion in this DAG are not also being written to by
a provider DAG, for instance. The simplest way to do this is to ensure that any
affected provider DAGs are not currently running.

----

### `europeana_workflow`

Content Provider: Europeana

ETL Process: Use the API to identify all CC licensed images.

Output: TSV file containing the images and the respective meta-data.

Notes: <https://pro.europeana.eu/page/search>

----

### `finnish_museums_workflow`

Content Provider: Finnish Museums

ETL Process: Use the API to identify all CC licensed images.

Output: TSV file containing the images and the respective meta-data.

Notes: <https://api.finna.fi/swagger-ui/>
<https://www.finna.fi/Content/help-syntax?lng=en-gb> The Finnish Museums
provider script is a dated DAG that ingests all records that were last updated
in the previous day. Because of this, it is not necessary to run a separate
reingestion DAG, as updated data will be processed during regular ingestion.

----

### `flickr_audit_sub_provider_workflow`

#### Flickr Sub Provider Audit

Check the list of member institutions of the Flickr Commons for institutions
that have cc-licensed images and are not already configured as sub-providers for
the Flickr DAG. Report suggestions for new sub-providers to Slack.

----

### `flickr_workflow`

Content Provider: Flickr

ETL Process: Use the API to identify all CC licensed images.

Output: TSV file containing the images and the respective meta-data.

Notes: <https://www.flickr.com/help/terms/api>

Rate limit: 3600 requests per hour.

----

### `freesound_workflow`

Content Provider: Freesound

ETL Process: Use the API to identify all CC-licensed images.

Output: TSV file containing the image, the respective meta-data.

Notes: <https://freesound.org/docs/api/>

Rate limit: No limit for our API key. This script can be run either to ingest
the full dataset or as a dated DAG.

----

### `inaturalist_workflow`

Provider: iNaturalist

Output: Records loaded to the image catalog table.

Notes: The iNaturalist API is not intended for data scraping.
<https://api.inaturalist.org/v1/docs/> But there is a full dump intended for
sharing on S3.
<https://github.com/inaturalist/inaturalist-open-data/tree/documentation/Metadata>
Because these are exceptionally large normalized tables, as opposed to more
document oriented API responses, we found that bringing the data into postgres
first was the most effective approach. More detail in slack here:
<https://wordpress.slack.com/archives/C02012JB00N/p1653145643080479?thread_ts=1653082292.714469&cid=C02012JB00N>
We use the table structure defined here,
<https://github.com/inaturalist/inaturalist-open-data/blob/main/Metadata/structure.sql>
except for adding ancestry tags to the taxa table.

----

### `jamendo_workflow`

Content Provider: Jamendo

ETL Process: Use the API to identify all CC-licensed audio.

Output: TSV file containing the audio meta-data.

Notes: <https://api.jamendo.com/v3.0/tracks/> 35,000 requests per month for
non-commercial apps Jamendo Music has more than 500,000 tracks shared by 40,000
artists from over 150 countries all over the world. Audio quality: uploaded as
WAV/ FLAC/ AIFF bit depth: 16/24 sample rate: 44.1 or 48 kHz channels: 1/2

----

### `justtakeitfree_workflow`

Content Provider: Justtakeitfree

ETL Process: Use the API to identify all CC licensed media.

Output: TSV file containing the media and the respective meta-data.

Notes: <https://justtakeitfree.com/api/api.php> This API requires an API key.
For more details, see <https://github.com/WordPress/openverse/pull/2793>

----

### `metropolitan_museum_workflow`

Content Provider: Metropolitan Museum of Art

ETL Process: Use the API to identify all CC0 artworks.

Output: TSV file containing the image, their respective meta-data.

Notes: <https://metmuseum.github.io/#search> "Please limit requests to 80
requests per second." May need to bump up the delay (e.g. to 3 seconds), to
avoid of blocking during local development testing.

                        Some analysis to improve data quality was conducted using a
                        separate csv file here: <https://github.com/metmuseum/openaccess>

                        Get a list of object IDs:
                        <https://collectionapi.metmuseum.org/public/collection/v1/objects?metadataDate=2022-08-10>
                        Get a specific object:
                        <https://collectionapi.metmuseum.org/public/collection/v1/objects/1027>
                        The search functionality requires a specific query (term search)
                        in addition to date and public domain. It seems like it won't
                        connect with just date and license.
                        <https://collectionapi.metmuseum.org/public/collection/v1/search?isPublicDomain=true&metadataDate=2022-08-07>

----

### `nappy_workflow`

Content Provider: Nappy

ETL Process: Use the API to identify all CC0-licensed images.

Output: TSV file containing the image meta-data.

Notes: This api was written specially for Openverse. There are no known limits
or restrictions. <https://nappy.co/>

----

### `oauth2_authorization`

#### OAuth Provider Authorization

Iterates through all the OAuth2 providers and attempts to authorize them using
tokens found in the in the `OAUTH2_AUTH_KEYS` Variable. Once authorization has
been completed successfully, the auth token is removed from that Variable. The
authorization will create an access/refresh token pair in the
`OAUTH2_ACCESS_TOKENS` Variable.

**Current Providers**:

- Freesound

----

### `oauth2_token_refresh`

#### OAuth Provider Token Refresh

Iterates through all OAuth2 providers and attempts to refresh the access token
using the refresh token stored in the `OAUTH2_ACCESS_TOKENS` Variable. This DAG
will update the tokens stored in the Variable upon successful refresh.

**Current Providers**:

- Freesound

----

### `phylopic_workflow`

Content Provider: PhyloPic

ETL Process: Use the API to identify all CC licensed images.

Output: TSV file containing the image, their respective meta-data.

Notes: <http://api-docs.phylopic.org/v2/> No rate limit specified.

----

### `point_{environment}_es_alias`

#### Point ES Alias DAG

This file generates our Point ES Alias DAGs using a factory function. A separate
DAG is generated for the staging and production environments.

The DAGs are used to point a `target_alias` to a `target_index` in the given
environment's elasticsearch cluster. When the alias is applied, it is first
removed from any existing index to which it already applies; optionally, it can
also delete that index afterward.

##### When this DAG runs

This DAG is on a `None` schedule and is run manually.

##### Race conditions

Each DAG will fail immediately if any of the DAGs tagged as part of the
es-concurrency group for the DAG's environment is running. (E.g., the
`point_staging_alias` DAG fails immediately if any DAGs tagged with
`staging-es-concurrency` are running.)

----

### `pr_review_reminders`

#### PR Review Reminders

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

----

### `rawpixel_workflow`

Content Provider: Rawpixel

ETL Process: Use the API to identify all CC-licensed images.

Output: TSV file containing the image meta-data.

Notes: Rawpixel has given Openverse beta access to their API. This API is
undocumented, and we will need to contact Rawpixel directly if we run into any
issues. The public API max results range is limited to 100,000 results, although
the API key we've been given can circumvent this limit.
<https://www.rawpixel.com/api/v1/search?tags=$publicdomain&page=1&pagesize=100>

----

### `recreate_full_staging_index`

#### Recreate Full Staging Index DAG

This DAG is used to fully recreate a new staging Elasticsearch index for a given
`media_type`, using records pulled from the staging API database rather than
from a source index (like the `create_new_staging_es_index` DAG does). It is
used to decouple the steps of creating a new index from the rest of the data
refresh process.

Staging index creation is handled by the _staging_ ingestion server. The DAG
triggers the ingestion server `REINDEX` action to create a new index in the
staging elasticsearch cluster for the given media type, suffixed by the current
timestamp. The DAG awaits the completion of the index creation and then points
the `<media_type>-full` alias to the newly created index.

Required Dagrun Configuration parameters:

- media_type: the media type for which to create a new index.

Optional params:

- target_alias_override: Override the alias that is pointed to the new index. By
  default this is `<media_type>-full`.
- delete_old_index: Whether to delete the index previously pointed to by the
  target alias, if applicable. Defaults to False.

##### When this DAG runs

This DAG is on a `None` schedule and is run manually.

##### Race conditions

Because this DAG runs on the staging ingestion server and staging elasticsearch
cluster, it does _not_ interfere with the `data_refresh` or
`create_filtered_index` DAGs.

However, as the DAG operates on the staging API database and ES cluster it will
exit immediately if any of the DAGs tagged as part of the
`staging_es_concurrency` group are already running.

----

### `recreate_{media_type}_popularity_calculation`

This file generates Apache Airflow DAGs that, for the given media type,
completely wipes out and recreates the PostgreSQL functions involved in
calculating our standardized popularity metric.

Note that they do not drop any tables or views related to popularity, and they
do not perform any popularity calculations. Once this DAG has been run, the
associated popularity refresh DAG must be run in order to actually recalculate
popularity constants and standardized popularity scores using the new functions.

These DAGs are not on a schedule, and should only be run manually when new SQL
code is deployed for the calculation.

----

### `report_pending_reported_media`

#### Report Pending Reported Media DAG

This DAG checks for any user-reported media pending manual review, and alerts
via Slack.

Media may be reported for mature content or copyright infringement, for example.
Once reported, these require manual review through the Django Admin to determine
whether further action (such as deindexing the record) needs to be taken. If a
record has been reported multiple times, it only needs to be reviewed once and
so is only counted once in the reporting by this DAG.

----

### `rotate_db_snapshots`

Manages weekly database snapshots.

RDS does not support weekly snapshots schedules on its own, so we need a DAG to
manage this for us.

It runs on Saturdays at 00:00 UTC in order to happen before the data refresh.

The DAG will automatically delete the oldest snapshots when more snapshots exist
than it is configured to retain.

Requires two variables:

`CATALOG_RDS_DB_IDENTIFIER`: The "DBIdentifier" of the RDS DB instance.
`CATALOG_RDS_SNAPSHOTS_TO_RETAIN`: How many historical snapshots to retain.

----

### `science_museum_workflow`

Content Provider: Science Museum

ETL Process: Use the API to identify all CC-licensed images.

Output: TSV file containing the image, the respective meta-data.

Notes:
<https://github.com/TheScienceMuseum/collectionsonline/wiki/Collections-Online-API>
Rate limited, no specific rate given.

----

### `smithsonian_workflow`

Content Provider: Smithsonian

ETL Process: Use the API to identify all CC licensed images.

Output: TSV file containing the images and the respective meta-data.

Notes: <https://api.si.edu/openaccess/api/v1.0/search>

----

### `smk_workflow`

Content Provider: Statens Museum for Kunst (National Gallery of Denmark)

ETL Process: Use the API to identify all openly licensed media.

Output: TSV file containing the media metadata.

Notes: <https://www.smk.dk/en/article/smk-api/>

----

### `staging_database_restore`

#### Staging Database Restore DAG

This DAG is responsible for updating the staging database using the most recent
snapshot of the production database.

For a full explanation of the DAG, see the implementation plan description:
<https://docs.openverse.org/projects/proposals/search_relevancy_sandbox/20230406-implementation_plan_update_staging_database.html#dag>

This DAG can be skipped by setting the `SKIP_STAGING_DATABASE_RESTORE` Airflow
Variable to `true`. To change this variable, navigate to Admin > Variables in
the Airflow UI, then click the "edit" button next to the variable and set the
value to either `true` or `false`.

This DAG will default to using the standard AWS connection ID for the RDS
operations. For local testing, you can set up two environment variables to have
the RDS operations run using a different hook:

- `AWS_RDS_CONN_ID`: The Airflow connection ID to use for RDS operations (e.g.
  `aws_rds`)
- `AIRFLOW_CONN_<ID>`: The connection string to use for RDS operations (per the
  above example, it might be `AIRFLOW_CONN_AWS_RDS`)

----

### `stocksnap_workflow`

Content Provider: StockSnap

ETL Process: Use the API to identify all CC-licensed images.

Output: TSV file containing the image, the respective meta-data.

Notes: <https://stocksnap.io/api/load-photos/date/desc/1>
<https://stocksnap.io/faq> All images are licensed under CC0. No rate limits or
authorization required. API is undocumented.

----

### `wikimedia_commons_workflow`

**Content Provider:** Wikimedia Commons

**ETL Process:** Use the API to identify all CC-licensed images.

**Output:** TSV file containing the image, the respective meta-data.

#### Notes

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

##### `imageinfo`

[Docs](https://commons.wikimedia.org/w/api.php?action=help&modules=query%2Bimageinfo)

[Example where metadata has hundreds of data points](https://commons.wikimedia.org/wiki/File:The_Railway_Chronicle_1844.pdf#metadata)
(see "Metadata" table, which may need to be expanded).

For these requests, we can remove the `metadata` property from the `iiprops`
parameter to avoid this issue on subsequent iterations.

##### `globalusage`

[Docs](https://commons.wikimedia.org/w/api.php?action=help&modules=query%2Bglobalusage)

[Example where an image is used on almost every wiki](https://commons.wikimedia.org/w/index.php?curid=4298234).

For these requests, we can remove the `globalusage` property from the `prop`
parameter entirely and eschew the popularity data for these items.

----

### `wordpress_workflow`

Content Provider: WordPress Photo Directory

ETL Process: Use the API to identify all openly licensed media.

Output: TSV file containing the media metadata.

Notes: <https://wordpress.org/photos/wp-json/wp/v2> Provide photos, media, users
and more related resources. No rate limit specified.

----

### `{environment}_elasticsearch_cluster_healthcheck`

Monitor staging and production Elasticsearch cluster health endpoint.

Requests the cluster health and alerts under the following conditions:

- Red cluster health
- Unexpected number of nodes
- Unresponsive cluster

Additionally, the DAG will notify (rather than alert) when the cluster health is
yellow. Yellow cluster health may or may not be an issue, depending on whether
it is expected, and occurs whenever shards and replicas are being relocated
(e.g., during reindexes). It is worthwhile to notify in these cases, as an
assurance, but we could choose to add logic that ignores yellow cluster health
during data refresh or other similar operations.

----

### `{environment}_{media_type}_data_refresh`

#### Data Refresh DAG Factory

This file generates our data refresh DAGs for each media type and environment
using a factory function. The data refresh is a process which makes new content
added to the Catalog by our provider DAGs available to the API.

The data refresh has the following high level steps:

- Copy Data: An FDW extension is used to connect the API database to the
  upstream (catalog) database. The entire contents of the upstream media table
  are copied into a new temp table in the API database. This temp table will
  later replace the main media table in the API.
- Create Index: Create a new Elasticsearch index, matching the configuration of
  the existing media index.
- Distributed Reindex: Convert each record from the new temp table to the format
  required by an Elasticsearch document, and then reindex them into the newly
  created index.
- Create and Populate Filtered Index: Create a new Elasticsearch index matching
  the configuration of the existing filtered index, and then reindex documents
  into it from the new media index, applying appropriate filtering for sensitive
  terms.
- Reapply Constraints: Recreate indices and constraints from the original API
  tables on the new temp tables.
- Promote Table: Drop the old media table in the API and rename the temp table
  and its indices, which has the effect of promoting them/replacing the old
  table.
- Promote Index: Promote the new Elasticsearch index by unlinking the given
  alias from the existing index and moving it to the new one. (Used for both the
  main and filtered indices.)
- Delete Index: Delete the old Elasticsearch index. (Used for both the main and
  filtered indices.)

Importantly, the data refresh DAGs are also configured to handle concurrency
requirements of the reindexing steps.

You can find more background information on this process in the following issues
and related PRs:

- [[Implementation Plan] Ingestion Server Removal](https://docs.openverse.org/projects/proposals/ingestion_server_removal/20240328-implementation_plan_ingestion_server_removal.html)
- [[Feature] Merge popularity calculations and data refresh into a single DAG](https://github.com/WordPress/openverse-catalog/issues/453)

----

### `{media_type}_data_refresh`

#### Data Refresh DAG Factory

This file generates our data refresh DAGs using a factory function. For the
given media type these DAGs will initiate a data refresh on the ingestion server
and await the success or failure of that task.

A data refresh occurs on the Ingestion server in the Openverse project. This is
a task which imports data from the upstream Catalog database into the API,
copies contents to a new Elasticsearch index, and finally makes the index
"live". This process is necessary to make new content added to the Catalog by
our provider DAGs available to the API. You can read more in the
[README](https://github.com/WordPress/openverse/blob/main/ingestion_server/README.md)
Importantly, the data refresh TaskGroup is also configured to handle concurrency
requirements of the Ingestion server. Finally, once the origin indexes have been
refreshed, the corresponding filtered index creation DAG is triggered.

You can find more background information on this process in the following issues
and related PRs:

- [[Feature] Data refresh orchestration DAG](https://github.com/WordPress/openverse-catalog/issues/353)
- [[Feature] Merge popularity calculations and data refresh into a single DAG](https://github.com/WordPress/openverse-catalog/issues/453)

----

### `{media_type}_popularity_refresh`

#### Popularity Refresh DAG Factory

This file generates our popularity refresh DAGs using a factory function.

For the given media type these DAGs will first update the popularity metrics
table, adding any new metrics and updating the percentile that is used in
calculating the popularity constants. It then refreshes the popularity constants
view, which recalculates the popularity constant for each provider.

Once the constants have been updated, the DAG will trigger a `batched_update`
DagRun for each provider of this media_type that is configured to support
popularity data. The batched update recalculates standardized popularity scores
for all records, using the new constant. When the updates are complete, all
records have up-to-date popularity data. This DAG can be run concurrently with
data refreshes and regular ingestion.

You can find more background information on this process in the following
implementation plan:

- [[Implementation Plan] Decoupling Popularity Calculations from the Data Refresh](https://docs.openverse.org/projects/proposals/popularity_optimizations/20230420-implementation_plan_popularity_optimizations.html)
