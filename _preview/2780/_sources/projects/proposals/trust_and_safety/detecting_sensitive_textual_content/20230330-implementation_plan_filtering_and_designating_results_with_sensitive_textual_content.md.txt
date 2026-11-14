# 2023-03-30 Implementation Plan: Filtering and designating results with sensitive textual content

**Author**: @sarayourfriend

## Reviewers

- [x] @stacimc
- [x] @dhruvkb

## Project links

- [Project Thread](https://github.com/WordPress/openverse/issues/377)
- [Project Proposal](./20230309-project_proposal_detecting_sensitive_textual_content.md)
- [Milestone (pending)](https://github.com/WordPress/openverse/milestone/5)
- [Implementation Plan: Managing A Sensitive Terms List](https://github.com/WordPress/openverse/pull/911)

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

A new Django setting `ENABLE_FILTERED_INDEX_QUERIES` will be used in the API to
enable querying the filtered index. If this setting is not enabled, then the new
parameter will still be used (as the downstream alias of the to-be-deprecated
`mature` parameter), but it will behave exactly as the current `mature`
parameter.

## API versioning

There are no API versioning concerns. We already filter sensitive content based
on provider data, we'll just be expanding upon that existing feature by
incorporating a new signal into the filter. I do not believe this requires a new
API version prefix or distinctly new parameter.

## Areas touched

Implementing this plan will require making changes in the following areas:

- API
- Elasticsearch
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
     - `SENSITIVE_TERMS_URL` injected as new environment variable. See
       [the related IP](./20230309-implementation_plan_sensitive_terms_list.md)
       for how this list will be managed. Details about how this environment
       variable will be used are below.
     - Ingestion server action to create the new index using `reindex` and an
       update the promote action to allow it to promote (point alias) for the
       filtered index
     - Updates to the `load_sample_data.sh` script to generate the filtered
       index
     - A benign list of terms to use for local testing that matches results in
       the sample data
1. Create a new `create_filtered_index` DAG that is triggered by the existing
   data refresh DAG.
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

## Feasibility

Whether the approach in this implementation plan is feasible was an open
question for some time. After extensive discussions with folks who know
Elasticsearch well, I decided on this approach and was able to test it in
staging. The full process, index creation, reindex, refresh, was run on a
production dataset from before iNaturalist was added. This means the origin
index was smaller than our current one, but still large: 550 million documents.
In staging, the whole process took just over six and a half hours. The resulting
index had 444 million documents, meaning it excludes approximately 20% of the
origin index.

Therefore, I consider this approach feasible: it is sufficiently quick, it
produced a dataset of unsurprising size (once quoted terms were used to prevent
false positives), and is easy to implement with the tools we already have, use,
and (mostly) understand.

## Technical description of plan

Each heading refers to one of the steps in the previous section.

### Ingestion server (overview step 1)

To efficiently filter sensitive content, we will create a secondary "filtered"
index using Elasticsearch's
[`reindex` API](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/docs-reindex.html).
This API allows us to copy documents from one index into another and using a
query to select specific documents from the origin index. With this, we can
create a large negated `multi_match` filter to exclude all results that contain
any of the sensitive terms in their textual content. This will happen in the
ingestion server as a separate step during data refresh.

The `SENSITIVE_TERMS_URL` environment variable will point to a URL for a
new-line separated list of sensitive terms. The default value of this variable
will point to a localhost route to retrieve a list of testing terms. This file
will be served by Falcon in the ingestion server. In production, this variable
will point to the GitHub raw link for the `sensitive-terms.txt` document in the
sensitive terms repository created as part of
[the related implementation plan](./20230309-implementation_plan_sensitive_terms_list.md).

An example of the query built as a Python object iterating over a list of
sensitive terms follows:

```py
sensitive_terms = requests.get(SENSITIVE_TERMS_URL).read().split("\n")
query = {
    "bool": {
        "must_not": [
            {
                "multi_match": {
                    # ``term`` must be quoted or terms with multiple
                    # words will be treated with "OR" between each
                    # word, leading to false positives on innocuous words
                    # that are part of sensitive phrases. Quoting mitigates
                    # this by telling ES to treat the entire term as
                    # a single token.
                    # See the ``operator`` parameter in the match
                    # documentation for further details
                    # https://www.elastic.co/guide/en/elasticsearch/reference/7.5/query-dsl-match-query.html#match-field-params
                    "query": f'"{term}"',
                    "fields": ["tags.name", "title", "description"],
                }
            }
            for term in sensitive_terms
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

In order for the new index to have the same settings as the original index
(sharding, mappings, etc), we need to take special action before calling the
reindex API. While the reindex API can create new indexes (if the destination
index specified does not exist), it does not support configuring the index in
the same request.

There are two approaches to ensuring the correct configuration of the filtered
index:

1. Create the new filtered index before calling reindex, using the
   [`index_settings`](https://github.com/wordpress/openverse/blob/38af21c359703d3faee9e160f1ac69372661d6a2/ingestion_server/ingestion_server/es_mapping.py#L1)
   function to configure this index in the same way as the origin index for the
   model.
2. Create an index template that Elasticsearch will automatically apply to new
   indexes that match the template pattern.
   - In this option we can rely on the reindex API to create the new index as ES
     will apply the template settings automatically.

The first is my recommendation as it matches our current approach and is trivial
to implement. The code sample at the end of this section demonstrates it in the
call to `es.indices.create`.

The second option, using index templates, is an interesting alternative that we
could explore in the future, especially once we remove the ingestion server.
However, it breaks significantly from our current approach to index
configuration and I do not think is worth pursuing as part of this project.

A sample implementation in a new `TableIndexer` method would look something like
this:

```py
def create_and_populate_filtered_index(
  self, model_name: str, index_suffix: Optional[str], **_
):
    # Rely on the alias to always created the filtered index from the up-to-date origin
    source_index = f"{model_name}"
    index_suffix = index_suffix or uuid.uuid4().hex
    destination_index = f"{source_index}-{index_suffix}-filtered"

    self.es.indices.create(
        index=destination_index,
        body=index_settings(model_name),
    )

    self.es.reindex(
        body={
            "source": {
                "index": source_index,
                "query": {
                    "bool": {
                        "must_not": [
                            {
                                "multi_match": {
                                    "query": f'"{term}"',
                                    "fields": ["tags.name", "title", "description"],
                                }
                            }
                            for term in SENSITIVE_TERMS
                        ]
                    }
                },
            },
            "dest": {"index": destination_index},
        },
        slices="auto",
        wait_for_completion=True,
    )

    self.refresh(index_name=destination_index, change_settings=True)

    self.ping_callback()
```

Please note the following important details:

1. `wait_for_completion` defaults to `True`, but it's worth explicitly including
   as we rely on the fact that the request will block the process until the
   reindexing is finished so that we know when we can promote the index.
1. `slices` is set to `"auto"` so that Elasticsearch is free to decide the
   optimal number of slices to use to parallelise the reindex.
1. The source index name is not passed explicitly to the API: instead the method
   must build it. This means we match the API of other calls (making updates to
   the data refresh DAG much simpler) and can avoid needing to parse the model
   name from the source index name for the call to `index_settings`.
1. We explicitly refresh the index after it is finished reindexing to prime it
   to be searched. ES only automatically refreshes indexes that are being
   actively used, and the index should be refreshed before it starts being used.

The creation of the new index follows the same pattern of creating the regular
index: create the index, copy the data into the index, then issue the command to
point the alias to the new index. This process is encapsulated in two actions:
the `create_and_populate_filtered_index` action described above, and the
existing `point_alias` action.

```{note}
While both processes have a "copy" step, they are notably different. The
origin index receives its documents from Postgres via ingestion workers, which
push the documents into Elasticsearch. The filtered index receives its
documents via the reindex API and does not require the ingestion workers.
```

### Airflow data refresh DAG factory (overview step 2)

To enable running filtered index creation independently of the data refresh
DAGs, we will create a separate DAG that will be triggered by the data refresh
DAGs using the
[`TriggeredDagRunOperator`](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/trigger_dagrun/index.html).
The new DAG will be named `create_filtered_<media_type>_index`. It will not run
on a schedule (only triggered), it will have a max concurrency of one, and it
will accept the following
[Airflow params](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/params.html):

- `model_name`: The model being filtered. Used as the alias of the origin index
  to use.
- `index_suffix`: Optionally, the suffix to add to the destination index.
- `force`: Used by the data refresh DAG to override the locking behaviour of the
  DAG that prevents it from running during a data refresh.

Splitting the process into a separate DAG presents complexities that are
reflected in the last variable, `force`. Consider the following situation: a
data refresh is currently happening, but you want to create a new filtered
index. You can theoretically kick off the reindex job from the existing index.
However, after the data refresh is finished, the previous index will be deleted!
This will prevent the reindex from completing successfully. Therefore, we cannot
create a filtered index if a data refresh is currently underway. Additionally,
if filtered index creation is underway, then we cannot run a data refresh
either. Even though the data refresh process takes considerable time before it's
ready to delete the previous index, we don't want to play with race conditions.

Rather than trying to use a complex lock, we will read the data refresh DAG
status at the start of the filtered index creation DAG run to check if the
corresponding data refresh DAG is running, e.g.:

```py
from data_refresh.dag_factory import image_data_refresh

@task
def prevent_concurrently_running_during_data_refresh():
    if image_data_refresh.get_active_runs() and not :
        # fail dag
```

In the data refresh, however, rather than failing if the filtered index creation
DAG is running, we'll merely tell it to wait, using the
[`ExternalTaskSensor`](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/sensors/external_task/index.html#airflow.sensors.external_task.ExternalTaskSensor).
That way it'll already be running and no new filtered index creation runs can be
triggered between some potential lag time of the first one finishing before the
data refresh is ready.

When the data refresh DAG triggers filtered index creation, it should pass the
suffix of the newly created origin index so that they match. We can identify
filtered indexes created during data refresh because they will have a matching
suffix to the origin index. Manual runs of the filtered index creation DAG
should exclude this so that a new suffix is created to prevent clashing with the
existing filtered index that was created for the previous data refresh run.

The new DAG should be modelled on the existing data refresh DAG's patterns for
making requests to the ingestion server. It must do the following:

1. Read the existing filtered index alias destination and save it (for deleting
   later)
   - The
     [data refresh DAG does this here](https://github.com/WordPress/openverse-catalog/blob/75990f356ed6d79601ecf3ecd96e48c3932acb47/openverse_catalog/dags/data_refresh/data_refresh_task_factory.py#L167-L174).
1. Create a new suffix to use if one is not provided in the variables
1. Call the `CREATE_AND_POPULATE_FILTERED_INDEX` action in the ingestion server
   and wait for completion
   - See existing data refresh DAG strategy for making and waiting for ingestion
     server requests
1. Call the `POINT_ALIAS`[^no-promote-action] action in the ingestion server and
   wait for completion.
1. Delete the previous filtered index whose canonical name we retrieved in the
   first step (`DELETE_INDEX` action)

[^no-promote-action]:
    We cannot use the `PROMOT` action used by the regular data refresh flow
    because while that action does point the alias to the newly created index,
    it also promotes the API tables, which is not necessary for filtered index
    creation. Therefore, we use the `POINT_ALIAS` action which only points
    aliases and nothing else.

Because the image and audio data refreshes run concurrently, it is necessary for
the filtered index creation DAG to also be a DAG factory, in the same style as
the data refresh DAG factory. This will result in a new DAG per media type. With
our current media types, that means we will add `image_filtered_index_creation`
and `audio_filtered_index_creation` DAGs.

### Query the filtered index (overview step 3)

We must add a new boolean query parameter to the search query serialiser,
`unstable__include_sensitive_results`. This parameter will default to the
disabled state. We will remove the `unstable` designation during the wrap-up of
this implementation plan. This parameter should also reflect the state of the
`mature` parameter: when `mature` is enabled, the new parameter should also be
enabled. This prepares us to deprecate the `mature` parameter when we remove the
`unstable` designation from the new parameter.

If the `mature` parameter and the new parameter are both supplied on the
request, the request should 400 with a note about the conflict and stating that
the `mature` parameter is deprecated and that `include_sensitive_results` should
be used instead.

While the new parameter can be used in the search controller to simplify the
code, querying the filtered index should only happen with the
`ENABLE_FILTERED_INDEX_QUERIES` setting is enabled. When that is the case and
when `unstable__include_sensitive_results` is not enabled for the request, query
the filtered index by appending the `-filtered` suffix to the index name. Update
the existing `mature` parameter handling to check
`unstable__include_sensitive_results` instead. When the new parameter is not
enabled on the request, results marked "mature" should also be filtered out, as
they are already when the `mature` parameter is not enabled on the request.

When the `unstable__include_sensitive_results` parameter is enabled on the
request, query the origin index so that results with sensitive textual content
are included.

### Derive the list of sensitive document IDs based on the filtered index (overview step 4)

When `unstable__include_sensitive_results` is enabled, we need to derive which
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

Additionally, we will query the content reports to disambiguate between provider
supplied mature results and results that users have reported as sensitive:

```py
# continuing previous example...
user_reported_sensitive_content_ids = MatureImage.objects
    .get(identifier__in=result_ids)
    .values_list("identifier", flat=True)
```

Add the resulting `sensitive_text_result_ids` and
`user_reported_sensitive_content_ids` sets to the result serialiser context so
that the media serialisers can reference them to derive the sensitive field:

```py
sensitivity = serializers.SerializerMethodField()

def get_sensitivity(self, obj):
    result = []
    if obj["identifier"] in self.context["user_reported_sensitive_content_ids"]:
        result.append("user_reported_sensitive")
    elif obj["mature"]:
        # This needs to be elif rather than a separate clause entirely
        # because reported content gets "mature" applied in Elasticsearch.
        # Provider supplied mature settings are only accurate if there
        # is not a corresponding, approved content report.
        # This assumes that anything with a content report that is confirmed
        # but not specifically de-indexed was not already marked as sensitive
        # by the provider and also violated our terms anyway so would be excluded.
        result.append("provider_supplied_sensitive")

    if obj["identifier"] in self.context["sensitive_result_ids"]:
        result.append("sensitive_text")

    return result
```

```{note}
We _must_ disambiguate between provider supplied sensitivity, user reported sensitivity, and sensitive textual content detected. Not only is it important to provide transparent information for _why_ these documents are marked as sensitive for general use, our own frontend will need to know the difference in order to present the correct copy to users. See the discussion in [this GitHub issue](https://github.com/WordPress/openverse/issues/791#issuecomment-1486952983) for more details on how this will be used.
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

```py
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
```

Note how the final resulting list of IDs includes results marked mature, but
that do not have sensitive textual content (result 2). Unfortunately there is no
way around this as if we were to exclude the results marked `mature` from the
origin result IDs in the final set subtraction, we'd end up with the following
situation:

```py
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

sensitive_result_ids =
  origin_index_less_mature_result_ids - filtered_index_result_ids
# => [1, 3] - [1] = [3]
```

Notice how we still have a problem: we've excluded the result that has sensitive
text _and_ is marked mature (result 4).

It's tempting to think we could move the mature filtering to _after_ when we've
derived the list of sensitive result IDs. However, the problem will remain the
same: we will exclude results that are both marked mature and have sensitive
textual content:

```py
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
results from the filtered index to begin with. Keep in mind that the `mature`
field on documents is an indexed boolean field. Searching these fields is
extremely efficient. Any potential performance benefit at query time would be
negligible and certainly not worth the additional complications of the only
potential way to exclude mature results from the filtered index.

## Wrap up

To wrap up the implementation, once the final step has been completed and
results are filtered or correctly marked as sensitive, we will promote the
`include_sensitive_results` parameter by removing the `unstable` designation.
Additionally, we will deprecate the `mature` parameter by removing it from the
documentation. To maintain API version backwards compatibility, it should
continue to operate as an undocumented alias for the `include_sensitive_results`
parameter. Finally, we will remove the `ENABLE_FILTERED_INDEX_QUERIES` setting
and make it the default behaviour.

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
