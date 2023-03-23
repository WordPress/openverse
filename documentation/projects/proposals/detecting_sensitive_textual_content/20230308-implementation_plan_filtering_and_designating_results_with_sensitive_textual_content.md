# Implementation Plan: Filtering and designating results with sensitive textual content

## Reviewers

- [ ] TBD
- [ ] TBD

## Project links

[Project Thread](https://github.com/WordPress/openverse/issues/377)
[Project Proposal](./20230309-project_proposal_detecting_sensitive_textual_content.md)
[Milestone (pending)](#)
[Implementation Plan: Managing A Sensitive Terms List](https://github.com/WordPress/openverse/pull/911)

Please refer to additional prior art linked in the project thread. The most
significant technical prior art is this exploratory PR for creating a filtered
index: https://github.com/WordPress/openverse-api/pull/1108

## Expected outcomes

- Results are filtered efficiently based on a list of sensitive terms.
- API results include a call-out on the result objects designating individual
  results that have sensitive textual content.

## Tools and dependencies

We will not need any new tools on the API side for this work.

## Feature flags

We should introduce a single "feature flag" on the API as an undocumented and
unstable query parameter `unstable__include_sensitive_results`.

## API versioning

There are no API versioning concerns. We already filter sensitive content based
on provider data, we'll just be expanding upon that existing feature by
incorporating a new signal into the filter. I do not believe this requires a new
API version prefix or distinctly new parameter.

## Areas touched

Implementing this plan will require making changes in the following areas:

- API
- Ingestion server
- Airflow data refresh DAG factory

## Terms

- "Origin index": This is the index we have now that includes all documents.
- "Filtered index": This is the index we will have after this implementation
  plan is implemented. Its documents are derived from the origin index but
  exclude any that have sensitive terms in their textual content.

## Overview of implementation process

In depth descriptions of each of these steps are covered below. Each step will
be implemented as a single pull request including appropriate tests.

1. Update the ingestion server with a new action to use the reindex API to
   generate a new index based on the origin index that only includes documents
   that do not have sensitive terms in the three textual content fields
   (`title`, `description`, `tags.name`). This is the filtered index.
   - Requires the following:
     - SENSITIVE_TERMS injected as new environment variable. See
       [the related IP](https://github.com/WordPress/openverse/pull/911) for how
       this will be implemented in Terraform.
     - Ingestion server action to create the new index using `reindex` and an
       update the promote action to allow it to promote (point alias) for the
       filtered index
     - Updates to the `load_sample_data.sh` script to generate the filtered
       index
     - A benign list of terms to use for local testing that matches results in
       the sample data
1. Update the data refresh DAG factory code to call the new filtered index
   actions.
1. Update the API with the new query parameter and query the filtered index when
   not including sensitive results.
1. Update the API to query the filtered index by document `_id` to deduce which
   documents in a query that includes sensitive results do not have sensitive
   terms. Use the resulting list of "safe" IDs to inverse the check and mark
   documents that are sensitive. Simultaneously, update the media serialisers to
   add the new `sensitivity` field. The serialiser field derives the array
   entries based on the results of the previous step and the existing `mature`
   field.

Many thanks to @robfelty for helping me find a much simpler approach to
sensitive result designation than I had originally devised. This solution is
easily 10x more intelligible and simpler to document and implement than the
others I had considered.

## Technical description of plan

Each heading refers to one of the steps in the previous section.

### Ingestion server (overview step 1)

To efficiently filter sensitive content, we will create a secondary "filtered"
index using Elasticsearch's
[`reindex` API](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/docs-reindex.html).
This API allows us to create a new index based on an existing one, while also
applying a query to the existing index. In effect, we can create a large negated
`multi_match` filter to exclude all results that contain any of the sensitive
terms in their textual content. This will happen in the ingestion server as a
separate step during data refresh.

An example of the query built as a Python object iterating over a list of
sensitive terms follows:

```py
query = {
    "bool": {
        "must_not": [
            {
                "multi_match": {
                    "query": term,
                    "fields": ["tags.name", "title", "description"],
                }
            }
            for term in SENSITIVE_TERMS
        ]
    }
}
```

The name of the filtered index will follow this pattern:
`{source_index}-filtered`. The filtered index alias will follow the same
pattern. This allows the API to easily query the filtered index, simply by
appending `-filtered` to the name of the index that was already being filtered.
For example, if the API is querying the filtered images index, it takes the
already designated `image` index name and appends `-filtered`: `image-filtered`.

The creation of the new index follow the same pattern of creating the regular
index: create the index, wait for index creation to finish, then issue the
command to point the alias to the new index. The ingestion server action to
create the filtered index will be called `create_filtered_index`. The ingestion
server action to promote the newly created filtered index will be called
`promote_filtered_index`. These actions follow the same API as the existing
`create` and `promote` actions.

> **Note**
>
> There is a notable exception to the similarity of this process with the
> regular index creation step. Specifically, the filtered index creation does
> not need to push the documents to Elasticsearch using the indexer workers: ES
> already has the documents in the "origin" index.

### Airflow data refresh DAG factory (overview step 2)

Adding these new steps to the Airflow data refresh DAG is simple and only
requires adding the two new actions to the
[existing `action_data_map`](https://github.com/WordPress/openverse-catalog/blob/4b5811aa240ba3ee2d92adea3a8abf88eb1e8aa4/openverse_catalog/dags/data_refresh/data_refresh_task_factory.py#L182)
with the target alias also configured on the `promote_filtered_index` action,
just as it is with the regular `promote` action.

### Query the filtered index (overview step 3)

We must add a new boolean query parameter to the search query serialiser,
`unstable__include_sensitive_results`. This parameter will default to `False`.
We will remove the `unstable` designation during the wrap-up of this
implementation plan. This parameter should also reflect the state of the
`mature` parameter: when `mature` is `True`, the new parameter should also be
`True`. This prepares us to deprecate the `mature` parameter when we remove the
`unstable` designation from the new parameter.

When `unstable__include_sensitive_results` is `False` (default behaviour), query
the filtered index by appending the `-filtered` suffix to the index name. Update
the existing `mature` parameter handling to check
`unstable__include_sensitive_results`. When the new parameter is `False`,
results with the `mature` set to `true` should also be filtered out.

When `unstable__include_sensitive_results` is `True`, query the origin index
(existing behaviour).

### Derive the list of sensitive document IDs based on the filtered index (overview step 4)

When `unstable__include_sensitive_results` is `True`, we need to derive which
documents in the results have sensitive textual content. To do this, we will
rely on the fact that those documents are _not_ in the filtered index.
Therefore, we can pull the list of `_id`s for the documents retrieved from the
origin index and query for their presence in the filtered index. If they are in
the filtered index, then we know they do not have sensitive textual content.
Something along the following lines of pseudocode:

```py
results = query_origin_index()
result_ids = set({r["_id"] for r in results})

results_in_filtered_index = query_filtered_index(results_ids)
ids_in_filtered_index = set({r["_id"] for r in results_in_filtered_index})

# Use set arithmatic to derive the list of sensitive documents
sensitive_text_result_ids = result_ids - ids_in_filtered_index
```

Add the resulting `sensitive_text_result_ids` set to the result serialiser
context so that the media serialisers can reference them to derive the sensitive
field:

```py
sensitivity = serializers.SerializerMethodField()

def get_sensitivity(self, obj):
    result = []
    if obj["mature"]:
        result.append("provider_supplied_mature")

    if obj["identifier"] in self.context["sensitive_result_ids"]:
        result.append("sensitive_text")

    return result
```

#### Mature results

Results with the `mature` field set to `true` will still be included in the
"filtered" index. While it is easy to exclude these results from the filtered
index, we cannot do so without making it harder to derive the list of results
with sensitive textual content based on presence in the filtered index. This is
because if the filtered index also excludes documents marked mature, then the
`origin_result_ids - filtered_result_ids` will generate a set exclusive of
documents marked mature _and_ those with sensitive textual content. Critically
this means that results in the origin index that are mature but do not have
sensitive text would get marked as having sensitive text based on their presence
in the `sensitve_result_ids` set.

The examples below are meant to illustrate this point as it's a bit of a
slippery concept without concrete examples (at least that's what I found when
writing this document).

```
origin_index_results = [
  {id: 1, mature: false}, # no sensitive text
  {id: 2, mature: true}, # no sensitive text
  {id: 3, mature: false}, # has sensitive text
  {id: 4, mature: true}, # has sensitive text
]

filtered_index_results = [
  {id: 1, mature: false}, # no sensitive text
]

origin_index_result_ids - filtered_index_result_ids
# => [1, 2, 3, 4] - [1] = [2, 3, 4]
```

Note how the final resulting list of IDs includes results marked mature, but
that do not have sensitive textual content (result 2). Unfortunately there is no
way around this as if we were to exclude the results marked `mature` from the
origin result IDs in the final set subtraction, we'd end up with the following
situation:

```
origin_index_results = [
  {id: 1, mature: false}, # no sensitive text
  {id: 2, mature: true}, # no sensitive text
  {id: 3, mature: false}, # has sensitive text
  {id: 4, mature: true}, # has sensitive text
]

filtered_index_results = [
  {id: 1, mature: false}, # no sensitive text
]

origin_index_less_mature_result_ids = [r for r in origin_index results if not r["mature"]]
# => [1, 3]

origin_index_less_mature_result_ids - filtered_index_result_ids
# => [1, 3] - [1] = [3]
```

Notice how we still have a problem: we've excluded the result that has sensitive
text _and_ is marked mature (result 4).

It's tempting to think we could move the mature filtering to _after_ when we've
derived the list of sensitive result IDs. However, the problem will remain the
same: we will exclude results that are both marked mature and have sensitive
textual content:

```
origin_index_results = [
  {id: 1, mature: false}, # no sensitive text
  {id: 2, mature: true}, # no sensitive text
  {id: 3, mature: false}, # has sensitive text
  {id: 4, mature: true}, # has sensitive text
]

filtered_index_results = [
  {id: 1, mature: false}, # no sensitive text
]

sensitive_result_ids = origin_index_result_ids - filtered_index_result_ids
# => [1, 2, 3, 4] - [1] = [2, 3, 4]

sensitive_results = [r for r in origin_index_results if r["_id"] in sensitive_result_ids and not r["mature"]]
# => [3]
```

Result 4 is still excluded because we can't tell in the final operation whether
result 4 was not in the set of IDs from the filtered index _only_ because it is
marked mature or if it also has sensitive textual content.

The only way I can think of to solve this is to have an index solely of
documents that _do_ have sensitive textual content and querying it to derive the
final list of sensitive results without needing to rely on the diversely
filtered index. However, this adds a big re-indexing burden (yet another
additional index) that can be bypassed altogether if we just exclude mature
results from the filtered index to begin with.

## Wrap up

To wrap up the implementation, once the final step has been completed and
results are filtered or correctly marked as sensitive, we will promote the
`include_sensitive_results` parameter by removing the `unstable` designation.
Additionally, we will deprecate the `mature` parameter by removing it from the
documentation. To maintain API version backwards compatibility, it should
continue to operate as an undocumented alias for the `include_sensitive_results`
parameter.

## Feature flags

Because the new functionality will all be either internal (ingestion server and
catalogue) or behind an unstable query parameter, we do not need any new feature
flags to manage the rollout of this work.

## Work streams

While the ingestion server and catalogue change could be implemented at roughly
the same time, it's probably useful to implement the ingestion server change
first so that the catalogue change can actually be tested in the local
environment with the new API functions. That means **there is a single work
stream for this implementation plan**.

The frontend implementation is _not_ entirely blocked by this plan as the
frontend can artificially set the "sensitivity" field on results for testing.
Final integration and validation of the frontend will depend on finishing this
implementation, however.
