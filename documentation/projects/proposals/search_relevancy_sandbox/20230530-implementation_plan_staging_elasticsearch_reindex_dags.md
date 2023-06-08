# 2023-06-08 Implementation Plan: Staging Elasticsearch Reindexing DAGs

**Author**: @krysal

## Reviewers

- [ ] @AetherUnbound
- [ ] @sarayourfriend

## Project links

- [Project Thread](https://github.com/WordPress/openverse/issues/392)
- [Project Proposal](./20230331-project_proposal_search_relevancy_sandbox.md)

## Overview

This document describes the addition of two DAGs for Elasticsearch index
creation ––full and proportional-by-provider–– which will allow us to decouple
the process from the extended Ingestion server's data refresh process and
iterate faster experimenting with smaller indices.

## Expected Outcomes

- 1 DAG for fully recreation of the index that the API uses which includes the
  includes all the database contents.
- 1 DAG to create indexes of reduced size but
  proportional-to-production-by-provider index.

## Dependencies

Same as for
[Implementation Plan: Update Staging Database](./20230406-implementation_plan_update_staging_database.md).

This work does not depend on any other projects and can be implemented at any
time.

## Outlined Steps

### `recreate_full_<media>_index` DAG

#### Parameters

1. `media_type`: The media type for which the index is being created. Presently
   this would only be `image` or `audio`.
2. `promote`: (Optional) A boolean value to indicate if result index will
   replace the current one pointed by the `media` alias. If `True`, then the new
   index will be the one used by the staging API. Defaults to `False`.
3. `delete_old_if_promoted`: (Optional) A boolean value to indicate if the old
   index pointed by the `<media>` alias should be deleted after replacement.
   Defaults to `False`.

#### Description

This DAG will leverage the Ingestion server's API and use the existing
[`REINDEX` task](REINDEX), which is the same used by the data refresh process to
create the index.

1. Get the current timestamp in order to create the index suffix with the form
   of `full-<timestamp>`.
2. Use the `ingestion_server.trigger_and_wait_for_task()` utility to send the
   `REINDEX` call to ingestion server, passing the previously generated
   `index_suffix` in the data payload.
3. If `promoted=True` is passed, then inmediatly make the `media` alias point to
   the new index. A
4. If the index is promoted then the DAG checks if `remove_old_if_promoted=True`
   and proceeds to [trigger the task in the ingestion server](DELETE_INDEX).
   Otherwise the DAG ends at the previous step.

[reindex]:
  https://github.com/WordPress/openverse/blob/7427bbd4a8178d05a27e6fef07d70905ec7ef16b/ingestion_server/ingestion_server/indexer.py#L282
[delete_index]:
  https://github.com/WordPress/openverse/blob/7427bbd4a8178d05a27e6fef07d70905ec7ef16b/catalog/dags/data_refresh/data_refresh_task_factory.py#L222-L239

### `create_proportional_by_provider_<media>_index` DAG

#### Parameters

## Alternatives

<!-- Describe any alternatives considered and why they were not chosen or recommended. -->

## Parallelizable streams

<!-- What, if any, work within this plan can be parallelized? -->

Both DAGs can be developed in parallel.

## Blockers

<!-- What hard blockers exist which might prevent further work on this project? -->

There is nothing currently blocking the implementation of this proposal.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

Elasticsearch does not impose any limit on the amount of indices one can create
but naturally they come with a cost. We don't have policies for creating or
deleting indices by the time being so we should monitor if we reach a point
where this impact the cluster performance.

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->
