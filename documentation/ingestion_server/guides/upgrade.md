# Manual index upgrade runbook

A manual index upgrade is similar to a data-refresh except for two key
differences.

- Each step of the process, from index creation, filtered index creation and
  then promotion is done manually by SSH-ing into the ingestion server and
  indexer workers.
- It is faster than a complete data-refresh as there is no transfer of data from
  the catalog database to the API database.

## Steps

### Staging deployment

1. [Deploy the ingestion server](/ingestion_server/guides/deploy.md) to staging.
   This step ensures that the latest schema will be used for the new indices.

2. Determine the real names of the indices behind the following aliases.

   - `image`
   - `image-filtered`
   - `audio`
   - `audio-filtered`

   This information is useful to know what index to use if a rollback is needed
   and to know what index to delete once the upgrade is complete. You can use
   [Elasticvue](https://elasticvue.com) for this.

   ```{tip}
   In staging, the filtered indices may also point to the default index.
   ```

3. Perform [reindexing](/ingestion_server/reference/task_api.md#reindex) of all
   media types. Let's say you use the suffix `abcd` for these indices. New
   indices for each media type, like `image-abcd` and `audio-abcd`, will be
   created.

   ```{caution}
   Staging indices are supposed to be smaller and should not have the same
   number of documents as the production dataset. You can
   [interrupt the indexing process](/ingestion_server/guides/troubleshoot.md#interrupt-indexing)
   once a satisfactory fraction (like ~50%) has been indexed.
   ```

   Wait for the indices to be replicated (and status green) before proceeding.

4. [Point aliases](/ingestion_server/reference/task_api.md#point_alias) (both
   default and filtered) for each media type to the new index.

   - `image` &rarr; `image-abcd`
   - `image-filtered` &rarr; `image-abcd`
   - `audio` &rarr; `audio-abcd`
   - `audio-filtered` &rarr; `audio-abcd`

5. Verify that the staging API continues to work.

   - If the staging API reports errors, immediately switch back the aliases to
     the old indices.
   - If the staging API works,
     [delete the old indices](/ingestion_server/reference/task_api.md#delete_index)
     to recover the free space.

### Production deployment

1. [Deploy the ingestion server](/ingestion_server/guides/deploy.md) to
   production. This step ensures that the latest schema will be used for the new
   indices.

2. Determine the real names of the indices behind the following aliases.

   - `image`
   - `image-filtered`
   - `audio`
   - `audio-filtered`

   This information is useful to know what index to use if a rollback is needed
   and to know what index to delete once the upgrade is complete. You can use
   [Elasticvue](https://elasticvue.com) for this.

3. Perform [reindexing](/ingestion_server/reference/task_api.md#reindex) of both
   media types. Let's say you use the suffix `abcd` for these indices. New
   indices for each media type, like `image-abcd` and `audio-abcd`, will be
   created.

   Wait for the indices to be replicated (and status green) before proceeding.

4. Perform
   [creation of filtered indices](/ingestion_server/reference/task_api.md#create_and_populate_filtered_index)
   for all media types. New filtered indices for each media type, like
   `image-abcd-filtered` and `audio-abcd-filtered`, will be created.

   Wait for the indices to be replicated (and status green) before proceeding.

5. [Point aliases](/ingestion_server/reference/task_api.md#point_alias) for each
   media type to the new default and filtered indices.

   - `image` &rarr; `image-abcd`
   - `image-filtered` &rarr; `image-abcd-filtered`
   - `audio` &rarr; `audio-abcd`
   - `audio-filtered` &rarr; `audio-abcd-filtered`

6. Verify that the production API continues to work.

   - If the production API reports errors, immediately switch back the aliases
     to the old indices.
   - If the production API works,
     [delete the old indices](/ingestion_server/reference/task_api.md#delete_index)
     to recover the free space.

## Rollback

In this process, we are creating the new indices first, remapping the aliases,
and then removing the old indices. So if there is an issue with the new indices,
we can immediately switch back the aliases to the old ones and restore
functionality. Then we can investigate into the new indices as they will still
be present, just unused.
