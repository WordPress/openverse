# 2023-06-08 Implementation Plan: Staging Elasticsearch Reindex DAGs

**Author**: @krysal

## Reviewers

- [ ] @AetherUnbound
- [ ] @sarayourfriend

## Project links

- [Project Thread](https://github.com/WordPress/openverse/issues/392)
- [Project Proposal](/projects/proposals/search_relevancy_sandbox/20230331-project_proposal_search_relevancy_sandbox.md)

## Overview

This document describes the addition of two DAGs for Elasticsearch (ES) index
creation ––full and proportional-by-provider–– which will allow us to decouple
the process from the long Ingestion server's data refresh process and experiment
with smaller indices. Also includes the adoption of two new index aliases for
ease of handling and querying the new index types from the API with the
[`internal__index`][api_ii_param] param.

[api_ii_param]: https://github.com/WordPress/openverse/pull/2073

## Expected Outcomes

- 1 DAG for fully recreation of the index that the API uses which includes the
  includes all the database contents.
- 1 DAG to create indexes of reduced size but
  proportional-to-production-by-provider index.

## Dependencies

Same as for
[Implementation Plan: Update Staging Database](/projects/proposals/search_relevancy_sandbox/20230406-implementation_plan_update_staging_database.md).

This work is related to the [Staging database recreation
DAG][staging_db_recreation] plan for having production volumes in the staging
DB, which is expected to finish soon.

[staging_db_recreation]: https://github.com/WordPress/openverse/issues/1989

## DAGs

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

#### Outlined Steps

This DAG will leverage the **Ingestion server's API** and use the existing
[`REINDEX` task][reindex], which is the same used by the data refresh process to
create the index.

1. Get the current timestamp in order to create the index suffix with the form
   of `full-<timestamp>`.
2. Use the `ingestion_server.trigger_and_wait_for_task()` utility to send the
   `REINDEX` call to ingestion server, passing the previously generated
   `index_suffix` in the data payload.
3. If `promoted=True` is passed, then inmediatly make the `media` alias point to
   the new index. A
4. If the index is promoted then the DAG checks if `remove_old_if_promoted=True`
   and proceeds to trigger the [DELETE_INDEX][delete_index] task in the
   Ingestion server. Otherwise the DAG ends at the previous step.

[reindex]:
  https://github.com/WordPress/openverse/blob/7427bbd4a8178d05a27e6fef07d70905ec7ef16b/ingestion_server/ingestion_server/indexer.py#L282
[delete_index]:
  https://github.com/WordPress/openverse/blob/7427bbd4a8178d05a27e6fef07d70905ec7ef16b/catalog/dags/data_refresh/data_refresh_task_factory.py#L222-L239

<!--------------------------------------------------------------------------->

### `create_proportional_by_provider_<media>_index` DAG

This DAG is intented to be used most likely with the index resulting from the
previous DAG or from the data refresh process, that is, an index with the
database fully indexed, as the `source_index` for the ES
[Reindex][es_reindex_api] API.

[es_reindex_api]:
  https://www.elastic.co/guide/en/elasticsearch/reference/7.12/docs-reindex.html

#### Parameters

1. `media_type`: The media type for which the index is being created. Presently
   this would only be `image` or `audio`.
2. `source_index`: (Optional) The existing index on Elasticsearch to use as the
   basis for the new index. If not provided, the index aliased to
   `<media_type>-full` will be used.
3. `percentage_of_production`: The proportion of items to take from each
   provider from the total amount existing in production.

#### Outlined Steps

1. Get the list of media count by sources from the production Openverse API
   [`https://api.openverse.engineering/v1/<media>/stats/`](https://api.openverse.engineering/v1/<media>/stats/)
2. Calculate the total media adding up all the counts by provider
3. Calculate the name of the new index with the following format:

```python
 f"{media_type}-{percentage_of_production}-percent-of-providers-{current_datetime}"
```

4. Make a dictionary mapping all the providers with the required amount of items
   for the new index based on the provided `percentage_of_production` param.
5. Iterate over the items of the resulting dictionary to index the subset of
   each provider.

```
POST _reindex?wait_for_completion=false
```

```json
{
  "max_docs": num_items,
  "source": {
    "index": "image-full",
    "query": {
      "term": {
        "source.keyword": "stocksnap"
      }
    }
  },
  "dest": {
    "index": "image-50-percent-of-providers-20230608183000"
  }
}
```

6. Make the alias `<media>-subset-by-provider` point to the new index.
7. Optionally. Query the stats of the resulting index and print the results.

```
GET /image-reindexed-by-provider/_stats
```

## Alternatives

### Combining both DAGs into one

One alternative to creating two different indices by separate is to create the
proportional by provider index using the Ingestion server. This would require
modifying the REINDEX task of the ingestion server or creating a new one that
takes only a subset of the providers by the indicated proportion.

However, I discarded this option in favor of the one explained above because
having both DAGs is much simpler and provides more possibilities for the
creation of different indexes, which is the end goal of the project.

## Parallelizable streams

Both DAGs can be developed in parallel.

## Blockers

There is nothing currently blocking the implementation of this proposal.

<!--
## Accessibility

 Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

We can discard the DAGs if the results are not as expected.

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

Elasticsearch does not impose any limit on the amount of indices one can create
but naturally they come with a cost. We don't have policies for creating or
deleting indices for the time being so we should monitor if we reach a point
where having many indexes impact the cluster performance.

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->

- [Script which added 100 records per provider into the testing ECS database](https://github.com/WordPress/openverse-infrastructure/pull/314)
