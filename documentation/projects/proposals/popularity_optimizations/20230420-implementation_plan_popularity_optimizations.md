# Implementation Plan: Decoupling Popularity Calculations from the Data Refresh

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @AetherUnbound
- [x] @obulat

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/433)
- [Project Proposal](https://docs.openverse.org/projects/proposals/popularity_optimizations/20230406-project_proposal_popularity_optimizations.md)

## Overview

<!-- A brief one or two sentence overview of the implementation being described. -->

This document describes a method for separating the popularity calculation steps
from the data refresh process, allowing the data refresh to be re-enabled
independently of popularity calculations.

## Background

To improve search relevancy, we use a
[rank feature query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-rank-feature-query.html)
to calculate relevance scores based (in part) on a `standardized_popularity`
score. Because the process of calculating these scores and pushing them into the
API DB (referred to as "data refresh") is complex, it may be beneficial to
briefly outline the tables and views currently used in the catalog database.

For simplicity, I will use `image` as an example, but note that equivalent
structures exist for `audio` and will exist for any media types added in the
future. Descriptions are not exhaustive; some details that are not relevant have
been omitted for brevity.

### `image`

The 'main' image table. Rows in this table may contain **raw** popularity data
from the provider in the `meta_data` column, such as the number of times this
image has been viewed or downloaded at the source provider.

This table is updated by **ingestion**, which may:

- insert newly ingested images
- update previously ingested images (for example, by updating raw popularity
  data)

### `image_popularity_metrics`

A table which contains known 'metrics': that is, the name of the metadata field
which contains raw popularity data for each provider. _Not all providers have a
configured popularity metric._

This table only needs to be updated when a metric is added or modified.

### `image_popularity_constants`

A materialized view which calculates, for each provider that supports popularity
data, a popularity constant that can be used to normalize raw popularity scores.
This constant is calculated using the 85th percentile of the given metric (total
views, etc). Because of this, the constant needs to be periodically updated for
accuracy as more data is consumed.

Refreshing this view results in the constants being recalculated. We currently
do this once a month. It must also be done whenever a new metric is added.

### `image_view`

A materialized view sourced from the `image` table, which adds the calculated
`standardized_popularity` column. This normalized popularity score is calculated
by a simple operation using the raw score and the popularity constant.

The effect of refreshing the view is to:

- Add all images which were ingested since the last time the view was refreshed,
  and calculate their popularity
- Update existing records which may have been modified on the `image` table
  since the last refresh
- Update the `standardized_popularity` for all records to use _the current
  popularity constant_

In a data refresh, the data from this view is copied into a new table in the API
DB, which is used to build new Elasticsearch indices and eventually swapped with
the live tables. As a result, the view **must** be refreshed before the data
refresh can run, or newly ingested data would not make it to the API.

## Outlined Steps

<!-- Describe the implementation step necessary for completion. -->

The basic strategy proposed here for decoupling popularity calculations from the
data refresh is:

1. Add `standardized_popularity` as a `nullable` column on the `image` and
   `audio` tables. ([link](#add-standardized-popularity-to-the-media-tables))
1. Update the `provider_dag_factory` and `ProviderDataIngester` to calculate
   `standardized_popularity` **at ingestion**.
   ([link](#update-provider-dags-to-calculate-standardized-popularity))
1. Create a new `popularity_refresh` DAG
   ([link](#create-a-popularity_refresh-dag)) which:
   1. Recalculates the popularity constants
   1. Updates the `standardized_popularity` score for existing records, using
      the new constants.
1. Remove the popularity calculation steps from the data refresh DAGs.
   ([link](#remove-popularity-steps-from-the-data_refresh-dags))
1. Begin running the data refresh directly from the media tables, and drop the
   materialized views. ([link](#run-the-data-refresh-from-the-media-tables))

More details about each of these steps, and the order in which they must be
implemented, is included in the following sections.

### Add standardized popularity to the media tables

This step is simple:

```plpgsql
ALTER TABLE image ADD COLUMN standardized_popularity DOUBLE PRECISION;
ALTER TABLE audio ADD COLUMN standardized_popularity DOUBLE PRECISION;
```

The column can (and indeed _must_) be nullable, as not all providers support
popularity data. Because this configuration exactly matches the schema of the
current `image_view` and `audio_view` matviews, we will be able to begin running
data refreshes directly off these tables with very few changes in the ingestion
server.

It should be noted that conventionally, storing calculated fields would be
considered a violation of database normalization principles. However, doing so
in this case will give us much better performance of the data refresh and also
save a significant amount of space, as it will enable us to drop the
materialized views.

### Update provider DAGs to calculate standardized popularity

Using the `ProviderDataIngester`, we can easily add standardized popularity
calculation to all of our providers at once [^1].

1. In `provider_dag_factory.py`, add a new
   `get_popularity_constants_and_metrics` task which runs prior to `pull_data`.
   This task will fetch the `metric` and `constant` for this provider from the
   `<media>_popularity_metrics` table.
   1. We will need to fetch metrics and constants for _each media type_
      supported by the provider, and return it as a dictionary. This information
      will be posted to XComs.
1. In `provider_dag_factory.py`, read the popularity data from XComs and pass it
   to the `pull_data` task and into the `init` for the `ProviderDataIngester`.
1. In `ProviderDataIngester`, create a `get_popularity_enriched_record_data`
   method as a wrapper for the abstract `get_record_data`. It should:
   1. Call `get_record_data`
   1. Calculate standardized popularity using the popularity constant and metric
      passed in from XComs
   1. Return the results of `get_record_data`, with `standardized_popularity`
      appended.
1. Update `ProviderDataIngester#process_batch` to call
   `get_popularity_enriched_record_data` instead of `get_record_data` _if
   popularity constants exist for this provider_. The logic can be skipped for
   providers that do not support popularity metrics.
1. Update the Media stores to accept `standardized_popularity`, defaulted to
   `None`, and write to tsv.
1. Update the `columns` used in the loader sql to write this column to the
   database.

When this work is completed:

- Standardized popularity scores will be calculated at ingestion for all new
  records
- For non-dated DAGs, popularity scores will immediately be backfilled for
  historical records as soon as the DAG has a successful run.
- For dated DAGs, the existing reingestion DAGs will begin slowly backfilling
  standardized popularity scores for historical records.

[^1]:
    There is one exception: iNaturalist does not use `get_record_data`, instead
    doing its data processing in postgres. We do not need to do anything to
    address this now because we do not track popularity data for iNaturalist;
    _however_, if we want to add popularity data for it in the future we will
    need to handle it separately.

### Create a `popularity_refresh` DAG

Once popularity calculation happens at ingestion (and assuming the media tables
are backfilled -- more on that later), we need only handle the following cases:

- A new popularity metric is added (for a new or existing provider)
- The popularity constants are recalculated

In both cases, we need to refresh the `<media>_popularity_constants` view (in
order to recalculate constants). Note that once the constants have been updated,
_the provider DAGs will immediately pick up the new constant and begin using it
at ingestion_. All that remains is to update the scores for historical data.

**Note**: It is true that our reingestion DAGs will also immediately begin
updating the standardized scores of historical data using the new constant.
However, this process is slow and some reingestion DAGs are currently running on
sparse schedules. I think it is still worth it to explicitly updates the scores
in this DAG, especially because that will allow us to use the DAG to do the
initial backfill.

As with our data refresh DAGs, we will use a factory to generate a
`popularity_refresh` DAG for each media type. The DAG will do the following:

1. Update the `<media>_popularity_metrics` table to include any newly added
   metrics.
1. Refresh the `<media>_popularity_constants` view to recalculate the popularity
   constants.
   1. This is done `CONCURRENTLY` so that provider DAGs can continue reading
      from the view while it updates.
1. For each unique `provider` in the `<media>_popularity_constants` view,
   generate a `refresh_<provider>_scores` task. The task will run an `UPDATE` of
   the `standardized_popularity` on all records matching that provider which
   were last updated before the task began.
   1. We may consider running the `refresh_<provider>_scores` tasks in parallel
      to speed up the update.
   1. Optionally, we can hard code a `SKIPLIST` of providers that are present in
      the `<media>_popularity_constants` view, but for which we do not want to
      create a refresh task. We currently have some providers (Nappy, Rawpixel,
      Stocksnap) that support popularity data but are not dated, meaning scores
      for **all** of their records will be updated the next time the DAG runs.
      _Note that some of these DAGs are on a `@monthly` schedule however, which
      means skipping them in this DAG could result in delayed recalculation
      time._
1. Report to Slack when the scores have finished updating.

Some notes:

- The DAG will initially run on a `None` schedule, while we get a sense of how
  long it will take to complete. Thereafter we will enable it on a `@monthly`
  schedule if possible, or quarterly if it proves too long-running.
- This DAG can run completely independently of the data refresh. The data
  refresh will always have access to the most recently ingested records, with
  standardized popularity. They will at worst be calculated using slightly
  outdated constants, which is the case today in production.

#### Special Considerations: Avoiding Deadlocks and Timeouts

The popularity refresh tasks must be written carefully to avoid deadlocks. The
key issues to understand are:

- Provider DAGs may be running and upserting historical data in the media tables
  at the same time that popularity refresh tasks are updating _the same data_.
- The `upsert_data` step of a provider DAG upserts all records in a single
  transaction, meaning that the changes are not committed until all rows have
  been upserted.

If the popularity refresh task _also_ updates all records for a provider in a
single transaction, a deadlock scenario could happen. Imagine that the records
'A' and 'B' already exist on the `image` table for Flickr, and the Flickr
reingestion DAG is reingesting them at the same time the `refresh_flickr_scores`
task is refreshing their popularity scores. Concurrent updates might happen in
this order:

| Flickr Reingestion DAG | `refresh_flickr_scores` | Comment                                                                                                                                                               |
| ---------------------- | ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Upsert record A        | Update record B         |                                                                                                                                                                       |
| Upsert record B        |                         | `refresh_flickr_scores` has a lock on the row containing record B, so the Flickr Reingestion DAG must wait.                                                           |
|                        | Update record A         | The Flickr Reingestion DAG has a lock on the row containing record A, so `refresh_flickr_scores` must wait. The transactions are now waiting on each other. Deadlock! |

We can avoid deadlock by noting that writes from a provider DAG will necessarily
_always have more up-to-date data_: so when a popularity refresh task encounters
a locked row, we can tell it to simply skip that record using `SKIP LOCKED`
(example code below).

We have now avoided deadlock but we still have a problem with our example: the
Flickr reingestion DAG must still wait for `refresh_flickr_scores` to release
the lock on record B. Our upsert task will hang and likely time out, as the
popularity refresh task will take a considerably long time to complete.

To avoid this, we must break up the popularity refresh into smaller
transactions, committing after every 10,000 rows are updated (this number can be
tweaked as necessary). This ensures that a concurrently running provider DAG
will only ever have to wait for a second or two before locked rows are released.

The approach is easiest explained with some sample code:

```plpgsql
-- The final product will be generalized by provider and media type.
-- In a local test, this successfully updated ~1 million Flickr
-- records in ~6 seconds, while the reingestion DAG was running.
DO $$
DECLARE
  rows_per_loop int := 10000;
  min_row int := 1;
  max_row int;
  max_timestamp timestamp;
BEGIN
  -- We will use this to select rows that have not been recently updated.
  SELECT NOW() INTO max_timestamp;

  -- A temporary table storing the identifiers of all records that need
  -- to be updated, plus their row number. The row number will be used to
  -- paginate the results more efficiently than using OFFSET. The table
  -- identifier must be unique for each provider to prevent conflict.
  CREATE TEMP TABLE rows_to_update AS
    SELECT ROW_NUMBER() over() row_id, identifier
    FROM image
    WHERE provider='flickr' AND updated_on < max_timestamp;
  CREATE INDEX ON rows_to_update(row_id);

  SELECT COUNT(*) INTO max_row FROM rows_to_update;

  -- Loop over `rows_to_update` 10k rows at a time, updating scores.
  -- Avoid deadlock using SKIP LOCKED
  FOR i IN min_row..max_row BY rows_per_loop LOOP
   UPDATE image
   SET standardized_popularity = standardized_image_popularity(
       image.provider,
       image.meta_data
   )
   WHERE identifier in (
       SELECT identifier FROM rows_to_update
       WHERE row_id >= i AND row_id < i+rows_per_loop
       FOR UPDATE SKIP LOCKED
   );
   -- COMMIT this batch
   COMMIT;
END LOOP;
END;
$$;
```

This is much less efficient than doing a single `UPDATE`, but has clear
advantages:

- It allows provider DAGs to continue running unimpeded.
- The data refresh can run at any time, even while the refresh tasks are
  running.
- Because updates are committed incrementally, each batch of updated scores will
  be 'live' on the image table as soon as they are committed. Rather than
  waiting for all rows to be calculated before making the update, as much
  up-to-date data as possible will be present each time the data refresh runs.

### Remove popularity steps from the data_refresh DAGs

We can simply remove the popularity tasks from the relevant data refresh DAG
factories. See the [Parallelizable Streams](#parallelizable-streams) section for
more information on the timing of this change.

### Run the data refresh from the media tables

Once the `image` and `audio` tables contain up-to-date standardized popularity
data, we can update the data refresh to read from these tables rather than their
respective materialized views. Because the schema of the media tables now
matches what the ingestion server already expects, we can simply change the
table name each place it is referenced:

- [`_get_shared_cols`](https://github.com/WordPress/openverse/blob/003c0d3e5c2813b671120144756659775f3369f4/ingestion_server/ingestion_server/ingest.py#L75)
- [`refresh_api_table`](https://github.com/WordPress/openverse/blob/003c0d3e5c2813b671120144756659775f3369f4/ingestion_server/ingestion_server/ingest.py#L310)
- [`get_copy_data_query`](https://github.com/WordPress/openverse/blob/003c0d3e5c2813b671120144756659775f3369f4/ingestion_server/ingestion_server/queries.py#L206)

## Dependencies

### Tools & packages

<!-- Describe any tools or packages which this work might be dependent on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

We should not need any additional dependencies.

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

This does not _depend_ on any existing projects. However, we should be careful
to follow along with the
[Documenting Media Properties](https://github.com/WordPress/openverse/issues/412)
project which is also in progress, and make sure that schema changes are
documented in accordance with that work.

### Infrastructure

<!-- Note any infrastructure this plan is dependent on. -->

This project directly affects our Catalog database schema, Airflow DAGs, and
ingestion server. All necessary changes are described in this document.

Notably, because this plan would allow us to drop the materialized `image_view`
and `audio_view`, we should net some DB storage savings in the long term.

## Alternatives

### Duplicate table

Another approach was considered which, rather than updating records directly on
the `image` table, would have instead created a duplicate table with updated
scores and ultimately swapped tables. This has the benefit of avoiding
concurrent writes to the `image` table, but the following disadvantages:

- While the duplicate table is being built, writes to the `image` table from
  provider DAGs would need to be propagated to it via a Postgres
  [`Trigger`](https://www.postgresql.org/docs/current/plpgsql-trigger.html)
  rule. Thus the same deadlocking precautions are necessary, and the writes must
  still be batched, offering no improved performance.
- This approach requires much more space for the duplicate table (although
  roughly equivalent to the current materialized view approach).
- This approach is much less efficient because it unnecessarily re-inserts
  **all** rows, including those that do not support popularity data at all.

### Separate `image_popularity` view

We considered keeping the `image` table as is, and an `image_popularity`
materialized view equivalent to the current `image_view`. A new,
non-materialized `image_view` would join `image` and `image_popularity` and be
used for the data refresh. The advantage is that the `image_popularity` view
could be refreshed independently of the data refresh; this approach would also
be very quick and easy to implement. The disadvantages:

- Would require a `join` at the time of data refresh
- The `image_popularity` view still needs to be refreshed, and will still take
  an untenably long time.
- When the data refresh runs, records that have not yet been refreshed in the
  `image_popularity` view will make it to the API, but without any standardized
  popularity score.

### Separate `image_popularity` table

Rather than having `popularity_score` as a column on the `image` table, we could
have a separate `image_popularity` table which contains only the scores, and
`identifier` for the purpose of joins. Initial popularity would still be
calculated at ingestion, and written to the new table. The data refresh would be
run on a (non-materialized) view which joins the two tables. This prevents the
media tables from becoming larger, and may possibly be faster to update
popularity. However:

- It is more complex to implement, because updates now have to be made to two
  tables at ingestion
- It still requires the same batching logic to avoid deadlocks/timeouts, so it
  is unlikely to be significantly faster at updating popularity scores
- It may result in a longer running data refresh because of the join
- It may result in longer loading times for provider DAGs
- It will use more space as long as there is a high proportion of records with
  popularity data, because we need to store two columns for each

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

As part of this project, we should add documentation for the new popularity
refresh DAGs and the calculations themselves.

## Parallelizable streams

<!-- What, if any, work within this plan can be parallelized? -->

The order of operations for this project is very important.

1. Add `standardized_popularity` column to media tables.
2. Update the Media stores to accept `standardized_popularity`, defaulted to
   None, and write this column to tsv.
3. Update the provider DAGs to calculate `standardized_popularity` at ingestion,
   and write to the database.
4. Create the `popularity_refresh` DAG factory.
5. Enable the `popularity_refresh` DAGs in production, to backfill scores on the
   media tables.
6. Once the `popularity_refresh` DAGs have completed their initial run, update
   the ingestion server to begin copying data from the media tables rather than
   the matviews.
7. Remove the popularity steps from the data refresh DAGs.
8. Drop the materialized views.

Steps 3 and 4 may be done in parallel.

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

These changes will only go into effect when we update the ingestion server to
begin reading from the media tables. We can rollback by reverting just this last
change. Consequently we should wait to drop the materialized views until we are
confident that the process is working.

Because we have a far smaller number of `audio` records, we should test the
process with `audio` first. We should also test the data refresh in staging.

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

This approach would add an additional column to our media tables; it also
requires a temp table used for storing the ids of rows that need to be updated.
There will be a net decrease in storage needed when the materialized views are
finally dropped, but in the interim we will use extra space.

We do not have a clear estimate for how long the popularity refresh DAG will
take, and a complete run is necessary before we can begin running the data
refresh. If the popularity refresh takes an extremely long time, this will delay
our ability to restart the image data refresh. _After_ the initial run, we will
be able to data refresh without waiting for subsequent popularity refreshes --
but an extremely long popularity refresh time is still undesirable because it
could cause our popularity scores to become relatively outdated.

It's also possible that we may see some increase in ingestion time for providers
with popularity data, due to:

- the addition of the calculations themselves. This should be insignificant as
  the calculation runs in constant time, and the popularity constant/metric need
  only be fetched once.
- concurrent writes from the popularity refresh tasks. The batched approach will
  prevent provider DAGs from hanging indefinitely while waiting on the
  popularity refresh, but there may still be some competition for locks which
  could add several seconds of waiting time. This is also unlikely to be
  significant, especially as the `upsert_data` steps are not currently a
  bottleneck in our provider DAGs.

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->

- [Investigation into data refresh failures due to popularity calculation timeouts post-iNaturalist](https://make.wordpress.org/openverse/2023/02/21/post-inaturalist-data-refresh-status/)
