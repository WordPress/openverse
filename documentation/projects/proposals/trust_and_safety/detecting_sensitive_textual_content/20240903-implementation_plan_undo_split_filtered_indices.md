# 2024-09-03 Implementation Plan: Undo the split indices for filtered textual sensitivity

**Author**: @sarayourfriend

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @dhruvkb (API familiarity, especially in code that interacts with ES
      during moderation)
- [x] @stacimc (Data refresh and ingestion worker expertise)

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

This implementation exists as a one-off modification to our textual sensitivity
detection, and does not have a corresponding project proposal.
[Refer to this GitHub issue requesting the implementation plan for discussion of the motivation for this change](https://github.com/WordPress/openverse/issues/3336).

**Before reading this plan**, please review
[the original implementation plan for the split-index approach](./20230330-implementation_plan_filtering_and_designating_results_with_sensitive_textual_content.md).
This document assumes familiarity with the details of the original plan and does
not review them in detail.

When this plan uses the phrase "the sensitive terms" or "sensitive terms list",
it refers to
[the newline-delimited list of sensitive terms described in this related IP](./20230309-implementation_plan_sensitive_terms_list.md).
**This plan does not mention any specific sensitive terms**, it is not necessary
to know the specific terms list to review this plan. However, it may be helpful
to know that the list is nearly 2000 lines long and is UTF-8 encoded.

Finally, this plan assumes that by the time it is relevant to consider it, the
[project to remove the ingestion server](https://github.com/WordPress/openverse/issues/3925)
will be complete. Therefore, this plan gives no consideration to the ingestion
server. It only considers the indexer worker and the new fully
Airflow-controlled data refresh implemented by the linked project.

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

This plan proposes changing our sensitive text detection strategy to accommodate
a single index per media type. The proposed method involves searching for
sensitive textual content in the indexer worker, rather than using the
Elasticsearch reindex API and Elasticsearch text queries.

The indexer worker will create
[a new `sensitivity` object field for each Elasticsearch document](https://github.com/WordPress/openverse/blob/df57ab3eb6586502995d6fa70cf417352ec68402/ingestion_server/ingestion_server/elasticsearch_models.py#L78-L128).
The field will be a nested object of boolean fields. The valid
[property names will match those used by the API](https://github.com/WordPress/openverse/blob/46a42f7e2c2409d7a8377ce188f4fafb96d5fdec/api/api/constants/sensitivity.py#L1-L12)[^provider-supplied-sensitivity]:

- `sensitive_text`: included for a document when the title, tags, or description
  of the work include any of the sensitive terms.
- `user_reported_sensitivity`: included for a document there is a confirmed
  sensitive content report for the work.

Additionally, a denormalised field `sensitivity.any` will be added to simplify
our current most-common query case, where we query for works that have no known
sensitivity designations.

Maintaining the denormalised field and its upstream fields ensures we can use
this data both at query and read time to effectively communicate the known
sensitivity designations for a given work, with no additional computation needed
at query time.

Details of the programming logic for each are covered in the
[step details section](#step-details).

[^provider-supplied-sensitivity]:
    [Please see the note in the linked code above regarding provider supplied sensitivity](https://github.com/WordPress/openverse/blob/46a42f7e2c2409d7a8377ce188f4fafb96d5fdec/api/api/constants/sensitivity.py#L4-L7).
    This plan makes no explicit consideration for provider supplied sensitivity.
    However, I believe the approach described in this plan increases, or at
    least maintains, our flexibility in the event it becomes relevant (i.e., we
    start intentionally ingesting works explicitly designated as sensitive or
    mature by the source).

```{admonition} Rationale for a new index field
:class: hint

While the filtered index currently exists to represent works free of sensitive
textual content, we can somewhat simplify the overall handling of sensitive
works in search by approaching this problem with both modes of sensitivity in
mind. The current approach to searching non-sensitive works is to search the
filtered index _and_ exclude works[^must-not] where `mature=true`. By switching
to a single object populated with the individual sensitivity designations, with the
denormalised `any`, we can simplify the search for non-sensitive works by filtering
for when the `sensitivity.any` field is false. We will effectively be able to swap out
the existing `must_not: mature=true` aspect for `must_not: sensitivity.any=true`.
```

[^must-not]:
    We use the boolean `must_not` with a match query to exclude works.
    Elasticsearch turns the match query into a Lucene `TermQuery`. Elasticsearch
    prefers “positive” queries, so this is faster than a `filter` for
    `mature:false`.

Once the `sensitivity` field is available in the index, we will update the API
to query based on that rather than switching indices and using the `mature`
approach. The API will use a feature flag to determine which querying approach
to use. This makes it easy for us to switch to the old querying approach in case
of failure, without needing to roll back or revert code, which could impact
other ongoing projects.

Finally, once we have confidence the new approach is working, we begin the phase
of cleaning up the multi-index approach. There are two major parts to this:
removing the filtered index management from the data refresh, and removing the
API code that utilises it. Neither of these appear to have much complexity. Both
are described in detail in the [step-by-step section](#step-by-step-plan).

### When to start clean-up

Clean-up will occur only after two full production data refreshes have occurred
with the new code fully available and enabled. This is to ensure we have
sufficiently exercised the new approach during the data refresh and at query
time before starting to take actions that will make rolling back more
cumbersome. Two full production data refreshes will encompass 2 weeks at the
minimum, but will more likely represent a period of 3 weeks.

### Evaluating the performance of the new approach

We should make an effort to compare the new approach to the old. There are two
methods we can use, one which seems intuitive but that I believe will not work,
and another which I believe will work, and which I propose we follow.

To attempt a simultaneous comparison of the two strategies, we could do the
following: preserve the ability for both strategies in the API, and direct a
portion of search requests to the new method. Using a new, temporary response
header, expose the search method used for the request in the Nginx logs. That
will enable us to query Logs Insights and determine whether there is a
meaningful difference in the average, median, p95, and p99 search timings for
the two methods over the same time period. This is an "ad-hoc" approach to
compensate
[for the lack of an existing A/B experimentation framework](https://github.com/WordPress/openverse/issues/421).

However, this presents a problem: it does not compare the final outcome of this
plan with the current state of things. The motivation for removing the filtered
index is predicated on the idea that moving to a single index will improve
Elasticsearch's ability to utilise its query cache and reduce disk operations.
If we are simultaneously using the single and multi-index approaches, the
behaviour of the cluster and application will not reflect the reduction in disk
operations or increase in cache utilisation. That is because the thing causing
the current behaviour will still be operating. In fact, trying both
simultaneously would probably make things worse for all queries across the
board. We would be sending rather different types of queries, still to multiple
indices, thereby reducing Elasticsearch's opportunity for cache utilisation and
thus increasing its disk operations.

To actually implement a simultaneous comparison, I hypothesise that we would
need to have identically resourced clusters, one for executing the new type of
query, and one for the old type. I believe because the performance question in
this plan has to do with reducing disk operations and increasing cache
utilisation, that the metrics are unique from relevance optimisations, which we
would be able to measure side by side.

While possible in theory, it is too complex!

Instead, I believe we should use a regular feature-flag approach as described
above, and compare the performance of the new approach in isolation. Any
significant negative impact will be immediately evident. Provided we don't see
an immediate issue, we can evaluate the performance of the new querying approach
for as long as we like (I propose at least two weeks), before we remove the
filtered index and the API code that uses it.

The original issue makes clear that we can see the improvement that using a
single index makes without needing to remove the additional indices, because the
results described by issue were collected while both indices were available on
the cluster. That fact makes this a viable approach. It means we can reliably
see if we've achieved the goal of reduced disk operations and increased cache
utilisation, without entering a situation where rollback is extremely difficult.

### Initial query performance analysis

The new approach, querying `must_not: sensitivity.any=true`, has identical
query-time performance implications as the `must_not: mature=true` query.
Therefore, there is no need to attempt a direct comparison of the query formats.

```{note}
A previous version of this implementation plan suggested using a keyword-list
field. That version of the plan included a surface-level exploration of the differences
between the must-not boolean-terms query and a must-not exists query. That
is no longer relevant for the sensitivity-as-object based approach now recommended,
but for posterity, it can be found in the commit history of the repository
at this commit:

<https://github.com/WordPress/openverse/blob/d616bf80fb3267887ae02bd27488e78e6508e2a7/documentation/projects/proposals/trust_and_safety/detecting_sensitive_textual_content/20240903-implementation_plan_undo_split_filtered_indices.md#initial-query-performance-analysis>
```

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

I've copied these lists of requirements/not-requirements from
[this comment of mine in the issue for this IP](https://github.com/WordPress/openverse/issues/3336#issuecomment-2288432417).

Requirements:

- **A single index rather than a filtered and unfiltered index**. This is the
  main requirement.
- Arbitrary changes to the list of sensitive terms continue to be reflected in
  search within one data refresh cycle
  - Keeping it “within one data refresh cycle" means the responsiveness to
    changes does not go down, but doesn't preclude it somehow becoming faster
    than one data refresh cycle, if for some reason that's possible.
- No ambiguity between the existing `mature` field and however we indicate
  textual sensitivity in the index.
- No negative change in search performance (i.e., cannot make search worse off
  after this).
- Including or excluding results with sensitive terms must not affect ranking.

Not requirements:

- That textual sensitivity designation exists in the catalogue, as opposed to
  only in Elasticsearch (it is not currently the case and making that a
  requirement would, strictly speaking, expand the scope of the project).
- Excluding a subset of "safe" providers from sensitive text
  scanning[^exclude-source-subset].
- Avoid unnecessary re-evaluation, e.g., by skipping evaluation for works where
  their metadata has not changed since the last time they were evaluated against
  the current sensitive terms list[^avoid-unnecessary-reevaluation].

[^exclude-source-subset]:
    This IP should make this an easy change in the future, if we decide to do
    it. We would just skip the sensitive text detection if the `source` field
    was in the list of sources to ignore.

[^avoid-unnecessary-reevaluation]:
    This IP should also make _this_ an easy change. We could cache the sensitive
    text scan based on a combined hash of
    `{title}{description}{"".join(tags)}{sensitive_terms_hash}`. This could be
    even simpler if we know that `updated_at` on the work is reliable. If it is,
    then we could just cache based on that and a hash of the terms list, rather
    than needing to hash the potentially large text blob of title, description,
    and tags.

Not being a requirement does not exclude the possibility of the thing, if it
turns out that works in our favour. I just want to make sure the scope of
_requirements_ is clear. The last two would be nice to have improvements, and
may or may not be easy to implement, and if they do not end up part of this
project, I will definitely create issues for each of them afterwards.

## Step-by-step plan

<!--
List the ordered steps of the plan in the form of imperative-tone issue titles.

The goal of this section is to give a high-level view of the order of implementation any relationships like
blockages or other dependencies that exist between steps of the plan. Link each step to the step description
in the following section.

If special deployments are required between steps, explicitly note them here. Additionally, highlight key
milestones like when a feature flag could be made available in a particular environment.
-->

These steps must be completed in sequence. Steps with multiple PRs may be
completed simultaneously to each other. Overall, this plan should result in
about 5 main pull requests.

1. Generate usable `sensitivity` fields for Elasticsearch documents (1 PR)
1. Update API with new query method (behind feature flag) (2 PRs, one for
   search, one for moderation tools)
1. Turn on feature flag in production and observe (1 minor infrastructure PR)
1. Clean up (2 PRs)

## Step details

<!--
Describe all of the implementation steps listed in the "step-by-step plan" in detail.

For each step description, ensure the heading includes an obvious reference to the step as described in the
"step-by-step plan" section above.
-->

### Step 1: Generate usable `sensitivity` field for Elasticsearch documents

Complete the following in a single PR:

To set up the sensitive terms list for use in the indexer worker, we will
retrieve the sensitive terms list from the GitHub URL (see data refresh for
reference) and make the list available to the indexer processes without
requiring subsequent outbound requests for the
list[^multiprocessing-future-proofed]:

[^multiprocessing-future-proofed]:
    These steps work from the assumption that an indexer worker may spawn
    multiple concurrent Python multiprocessing processes, which the indexer
    worker refers to as "tasks". While we do not currently utilise this
    functionality—that is, each `distributed_index` of the data refresh only
    calls `POST /task` once per indexer worker, and the indexer worker spawns a
    single multiprocessing process to handle the batch it is assigned—this plan
    is written to be future proofed in the event that we do utilise
    multiprocessing on the indexer worker to run multiple batches per worker.

- Create a new Python module in the indexer worker, `sensitive_terms.py`. It
  will export the following:
  - A function `retrieve_sensitive_terms` which accepts an argument
    `target_index` and retrieves the sensitive terms list from the network
    location and saves it to disk at
    `Path(__file__).parent / f"sensitive_terms-{target_index}.txt"`. This
    function should check an environment variable for the network location of
    the sensitive terms list. If that variable is undefined, it should simply
    write the mock sensitive terms ("water", "running", and "bird") to the disk
    location as a newline-delimited list.
    - The function should check whether the file location already exists, which
      would indicate the terms list was already pulled for the target index. If
      that is the case, then return early and do not re-pull the list.
    - This ensures any given target index uses the same sensitive terms query,
      even if multiple tasks are issued to the indexer worker. In other words,
      it only pulls the sensitive terms list once for a target index, and reuses
      it to service all requests against the same target index.
    - The indexer worker will call `retrieve_sensitive_terms` when handling
      `POST /task` and pass the `target_index` retrieved from the request body.
      Add the call to `retrieve_sensitive_terms` early in
      `api.IndexingJobResource::on_post`.
    - This ensures the file is populated to disk as early as possible, before
      any indexing jobs are actually spawned.
  - A function `get_sensitive_terms`, which will be wrapped in
    `@functools.cache`. The function will read `SENSITIVE_TERMS_LOC` and split
    the result on newline and return a tuple of compiled sensitive term regexes.
    - The regexes will target sensitive terms that are surrounded by word
      boundaries, whitespace, or the start/end of strings. To accomplish this in
      Python, we will use the regex `r"(\A|\b|\s){sensitive_term}(\Z|\b|\s)"`
      with the case-insensitive flag turned on.
      - We cannot merely use `\b` (word boundary) because it considers any
        non-alphanumeric character a word boundary. That means sensitive terms
        starting or ending with special characters like `@` or `$` would not
        match.
      - `\s` expands the matches to include special characters, and preserves
        `\b`'s boundary matching when appropriate.
      - `\A` and `\Z` cover the start and end of a string respectively, for when
        the term starts or ends with a special character. They cannot be used
        alone because we need to match terms within larger strings.
      - Using a regex is unfortunately necessary to ensure we do not have
        false-positives on non-sensitive terms in sub-portions of words, as with
        location names like
        [Shitterton in Dorset County, UK](https://en.wikipedia.org/wiki/Shitterton),
        which would arise if we did a simple `term in string` check. This is a
        minimum consideration we should give in light of our acknowledgement
        that text-based matching
        [is not perfect](./20230309-implementation_plan_sensitive_terms_list.md#this-will-not-be-perfect).
      - The use of compiled regexes makes caching the result especially
        important so that regex compilation is not unnecessarily repeated within
        a single indexer worker subprocess.
      - We should start with a single regex per term. In the future, we can
        consider combining slices of the sensitive terms list into larger regex
        statements, and evaluate whether this performs better or worse for our
        corpus. For now, we will keep it as simple as possible, with a single
        regex per term. It does not change the downstream code to do so, and
        introduces fewer complications with respect to regex construction.
    - Because each indexer worker can spawn multiple multiprocessing processes,
      each of which have independent Python interpreters, we rely on
      `functools.cache` to ensure each subprocess only has to parse
      `get_sensitive_terms` once, regardless of the number of documents it
      processes. This also ensures the list is available to `get_instance_attrs`
      and related functions without needing to pass it around as a new argument
      from somewhere "below" `launch_reindex` in the call stack for document
      processing, and does so without us needing to write the very same logic
      caching logic that `functools.cache` uses.

Now that the sensitive terms list is available as a list of regexes, implement
the primary logic for deriving the new fields:

- Add a new static method `elasticsearch_models.Model::get_text_sensitivity`.
  - This method will use `sensitive_terms.get_sensitive_terms` to retrieve the
    sensitive terms tuple.
  - Iterating through the sensitive term regexes and test the title,
    description, and each tag against the regex. If the term is in any field,
    immediately return true. We only need to test terms until we find one
    matching term, so it is safe to break the loop early once we find one.
- Update `elasticsearch_models.Model::get_instance_attrs` to create a new
  `sensitivity` dictionary field. Set the key `sensitive_text` to the result of
  `Model::get_text_sensitivity`. Set the key `user_reported_sensitivity` to the
  value of `row[schema["mature"]]`. Finally, set the key `any` to
  `sensitive_text or user_reported_sensitivity`.

Finally, add the new fields to the index settings.

- Update the index mappings in to add the new `sensitivity` field set to
  `{"properties": {"sensitive_text": {"type": "boolean"}, "user_reported_sensitivity": {"type": "boolean"}, "any": {"type": "boolean"}}}`.

After merging the PR, run the staging data refresh and confirm the new
sensitivity fields appear in new indices and is queryable (manually run queries
against them). It is not necessary to manually run the production data refresh,
and it is highly unlikely we will complete, review, and merge the API work
before a production data refresh runs. In other words, we do not need to
manually run a production data refresh, because one will surely happen before we
are ready to deploy the API changes. If not, step 3 includes a check to wait for
the production data refresh before enabling the changes in the API.

### Step 2: Update the API to use the new field (behind a feature flag)

Complete the following in two PRs.

#### First PR, **search**:

- Add a new feature-flag environment variable `USE_INDEX_BASED_SENSITIVITY` that
  defaults to false.
- Update search for the new query approach:
  - Modify `search_controller.get_index` to check the feature flag and return
    the unfiltered index when it is true. Otherwise, it should follow its
    existing logic.
  - Update `search_controller.build_search_query` to also check the feature
    flag. When it is false, use the existing `mature` based strategy for
    handling `include_sensitive_results`. When it is true and
    `include_sensitive_results` is false, use `sensitivity.any` instead of the
    existing `mature` field. Follow existing logic for when
    `include_sensitive_results` is true.
  - Finally, update `search_controller.query_media` to check the feature flag,
    and when true, bypass the `SearchContext.build` call and create
    `SearchContext` directly, as described below.
    - Retaining the `result_ids` list, create the `SearchContext` with
      `SearchContext(result_ids, {result.identifier for result in results if result.sensitivity.sensitive_text})`.
    - While this change to a single index and building the sensitivity list
      upstream of the API allows us to eventually remove `SearchContext`, we
      will retain it for now and mock its usage. This allows us to avoid needing
      to add the same feature flag checks in `MediaView` and `MediaSerializer`.
      Instead, we can leave those alone for now, and the same `sensitivity` list
      will continue to be populated by the serializer. Once we confirm this
      feature and enter the clean-up phase, we will remove `SearchContext`
      altogether. Details for this are in the
      [clean-up section](#step-4-clean-up).

#### Second PR, **moderation**:

- Update `AbstractSensitiveMedia._bulk_update_es` to update
  `sensitivity.user_reported_sensitivity` and `sensitivity.any` to `true`,
  alongside the existing update to `mature`
  - This should happen in addition to the `mature` update that already exists,
    but **must not be conditional on the `USE_INDEX_BASED_SENSITIVTY` feature
    flag**. It cannot be conditional in order to truly support the feature
    flag's accuracy in search results. If we toggle the flag on/off/on before a
    data refresh runs, the `sensitivity` fields must still get updated with
    user-reported sensitivity. Otherwise, when the feature goes back on,
    `sensitivity.user_reported_sensitivty/any` would not reflect the fact that
    those works had been reviewed and confirmed as sensitive. In that case, they
    would start reappearing in default search results (non-sensitive search).
- Update `MediaListAdmin.has_sensitive_text` to check
  `sensitivity.sensitive_text` of the Elasticsearch document if
  `USE_INDEX_BASED_SENSITIVITY` is true.
  - The method currently uses a term query to get the result with the
    identifier.
    [We should refactor this to use a single document `get` query by `id`](https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/examples.html#ex-get).
    Elasticsearch document `id` matches the Django model's `pk`. Doing so should
    improve the retrieval speed, and reduces the result to a single document,
    which makes reading the `sensitivity` field when retrieving it much easier.
  - When `USE_INDEX_BASED_SENSITIVITY` is true, query the "full" index instead
    of the filtered index.

### Step 3: Turn on feature flag in live environments and observe

Set `USE_INDEX_BASED_SENSITIVITY` to `True` in staging and redeploy. Confirm
search against the new indices created with the staging data refresh works,
including sensitive and non-sensitive queries. Also test and verify the
moderation features by confirming a sensitivity report in staging and making
sure the work is updated with `user_reported_sensitivity`.

If the production data refresh has not yet run, wait for it to run on its
regular cadence, and confirm the new `sensivitiy` fields as we did in staging in
step 1.

After confirming the production indices, set `USE_INDEX_BASED_SENSITIVITY` to
`True` in production and redeploy. Follow the same tests as listed above for
staging, but ask someone from the content moderation team to find a user
sensitivity report to confirm, and then ask them to check that the document in
ES has `sensitivity.user_reported_sensitive=true`. You may do this yourself, if
you feel comfortable, but it is best practice to defer to the content moderation
team to ensure the safety of everyone on the team.

Monitor production API search times as well as resource usage. Monitor the
production Elasticsearch cluster health in Kibana, and check I/O operations for
the data nodes. You may also check overall disk operations for the entire
cluster in CloudWatch.

### Step 4: Clean up

Refer to the note about when to start clean up in
[the overview](#when-to-start-clean-up).

#### Data refresh

- This essentially involves undoing
  [the filtered-index creation aspects added to the new data refresh in this PR](https://github.com/WordPress/openverse/pull/4833).
- Note that that PR includes fixes for other parts of the new data refresh, and
  so cannot merely be reverted to accomplish this task. Luckily, it still
  shouldn't be too much trouble.
- Delete `create_and_populate_filtered_index` and its usage.
- Remove filtered index promotion (task group ID `promote_filtered_index`).
- Update the DAG flow accordingly.
- This should ideally be implemented in a single PR to make it as easy as
  possible to revert, should the need arise.
- We can, at this point, also delete the `mature` field from the Elasticsearch
  mappings and remove the `raw` versions of `title`, `description`, and
  `tags.name`.

#### API code

- Remove `search_controller.get_index` and its usage.
- Remove mature content exclusion based on the `mature` boolean from
  `build_search_query`.
- Update `MediaView::get_db_results` to merge `sensitivity` from the
  Elasticsearch `Hit` onto the Django model for each result.
- Update `MediaSerializer::unstable__sensitivity` to create the `sensitivity`
  list from the object's merged `sensitivity` dictionary taken from the `Hit`:
- Remove the feature flag.
- As with the data refresh changes, implement these in a single PR if possible,
  to ensure the easiest possible revert if needed.

## Dependencies

### Feature flags

<!-- List feature flags/environment variables that will be utilised in the development of this plan. -->

One new API environment variable will act as the feature flag:
`USE_INDEX_BASED_SENSITIVITY`

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

There are no infrastructure changes required for this, aside from updating
environment variables.

The intentional increase in indexer worker resource usage should not increase
costs directly. However, the complexity of sensitive text designation exists no
matter where it goes in our compute pipeline. In the indexer workers, it will
naturally extend the time each worker spends on any given document. As such, the
overall amount of time the indexer workers are running will increase, and so
will their cost to us. Elsewhere, for example, in the Airflow local executor, we
would pay for it in decreased resources available for other tasks, extending the
time of those tasks, and potentially decreasing the scheduler's stability (if
resource usage increases a lot).

### Tools & packages

<!-- Describe any tools or packages which this work might depend on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

We do not require any new tools or packages to implement this change.

### Other projects or work

<!-- Note any projects this plan depends on. -->

As mentioned in [the project links](#project-links), this plan assumes
[the removal of the ingestion server](https://github.com/WordPress/openverse/issues/3925)
is finished by the time this plan makes modifications to the data refresh and
indexer worker.

## Alternatives

<!-- Describe any alternatives considered and why they were not chosen or recommended. -->

### Elasticsearch ingest pipeline

I spent a few days experimenting with and trying to see whether an ingest
pipeline would be a viable way to approach the creation of the sensitivity list
for this project. I believe it is generally viable, and I was able to make it
work locally with our local sample data and the full sensitive terms list. I
wrote about my evaluation of the ingest pipeline approach in these three
comments on the implementation plan issue:

1. [Describing the approach in general and initial testing](https://github.com/WordPress/openverse/issues/3336#issuecomment-2316894501)
1. [Further local testing with the complete sensitive terms list](https://github.com/WordPress/openverse/issues/3336#issuecomment-2325659270)
1. [Testing the ingest pipeline in staging](https://github.com/WordPress/openverse/issues/3336#issuecomment-2325684604)

Ultimately, despite ingest pipelines working fine to create the sensitivity
designations list, I don't think it's the right approach for us. As noted in the
final comment, whilst dedicated ingest nodes are not required to work with
ingest pipelines, a cluster still needs at least one node with the ingest role
to run ingest pipelines (it just isn't required to be those nodes' only role).
In order to service that requirement, we would need to introduce a new
complexity into our Elasticsearch cluster. We do not have the capacity (time and
knowledge) to fulfil this requirement. Therefore, we should not use
Elasticsearch ingest pipelines to generate the sensitivity designation.

### Move sensitive text detection earlier in the data refresh pipeline

Rather than detect sensitive text in the indexer worker when creating the
Elasticsearch documents, we could attempt to insert the sensitivity list into
the API database when we create the API tables from the catalogue tables. I
chose against recommending this because running several hundred regular
expressions in a loop will be resource intensive. We currently use the local
executor for Airflow, and such intense processing would likely be problematic
for our Airflow instance as it tries to complete other tasks as well. Placing
the regex execution in the indexer worker allows us to take advantage of the
indexer workers' provisioned CPU resources (which are under utilised overall at
only 25% when last evaluated in March of this year, as discussed in the
[ingestion server removal IP](/projects/proposals/ingestion_server_removal/20240328-implementation_plan_ingestion_server_removal.md#approach-to-the-distributed-reindex)).

Ideally, the list of specific sensitivity designations would exist only in the
API database and Elasticsearch would only be required to track a boolean
indicating whether any sensitivity designation exists at all. This would
simplify the following aspects of the plan:

- We would not need to use a script update to add to the sensitivity designation
  list in the Elasticsearch document. We would be able to use a simple `doc`
  update to set a `sensitive` boolean as needed. We could even skip the update
  for documents when moderating user reports if the document already has
  `sensitive=true` due to sensitive text.
- We would not need to query Elasticsearch in the media report admin to
  determine whether a work has sensitive text, as it would already be on the
  work.
- Search could use simple boolean query against the `sensitive` field instead of
  the slightly more complex negated exists against the `sensitivity` keyword
  list field.

I tried to determine whether there was a method of adding the `sensitivity` list
in the indexer worker, so that we could benefit from the indexer worker's
significant compute and memory resources without interrupting other Airflow
work, while still gaining these benefits. I did not see any existing mechanism
for accomplishing this kind of Postgres update in the indexer workers, but I'm
sure [the reviewers](#reviewers) are well-equipped to correct me on this.
Crucially, even if the capability does not currently exist, if we can add it
without significantly increasing this project's complexity, it would be worth
considering.

Additionally, if we were able to use remote compute resources to execute
individual tasks without the complexity that comes with using remote operators
(i.e., if we were using a remote executor), we could also consider doing this in
the data refresh tasks that build the new API tables. The road to that solution
is much more complex than this, though. It also remains an available option
should our Airflow infrastructure gain this capability in the future (for
example, if we were able to use the Kubernetes executor). I'm resistant to using
a remote operator for this single task, rather than rolling it into our existing
pseudo-remote operator of the indexer worker, because of the cost changes we
would incur by doing so.

### Move sensitive text detection to ingestion, supported by an occasional refresh DAG to backfill existing records

Staci and I evaluated this option in depth, over the course of a roughly 90
minute discussion, which built off of prior written discussions.

We evaluated the following approaches, and found all of them to either be wholly
unsuitable, or so complex that any conceivable benefit was nullified by the
complexity.

In general, the main complexity we encountered was in needing to at some point
or another maintain two separate sensitive term checks and identifiable results
of those checks. This is required because ingestion is happening essentially at
all times, and to avoid creating a dependency on the data refresh to the
sensitive terms refresh (which would be triggered whenever the sensitive terms
list changed), we would need ingestion DAGs to derive sensitivity for both the
old version of the list, and the new version of the list. A hypothetical
sensitive terms refresh DAG would do the work of adding the sensitive terms
designation derived from the new list to all pre-existing works. In the
meantime, any data refresh that runs, could continue to use the designation
derived from the old list.

We would use the commit SHA from the sensitive-terms repository to indicate the
"version" used to derive given textual sensitivity designation. For example,
this could be a new jsonb column `sensitivity` that contained an object of the
interface:

```ts
interface SensitivityColumn {
  text: {
    [commitSha: string]: boolean
  }
}
```

The data refresh would be aware of the "current" commit SHA to check, which
would only switch over to the new list's SHA once the refresh was complete and
all works had a designation based on the new SHA.

The primary difficult in this is the significant potential for race conditions,
about which Staci and I spent most of the time trying to solve. The problem is
making sure all works are covered with the new check. If ingesters are
immediately responsive to new versions of the list being made available to them
by the DAG, then they would have partial ingestions, where one portion of the
ingested works were ingested with only the old list, and the later portion both
lists. Because works only have UUIDs created after they are upserted into the
media tables, there is no way to retroactively identify those works. For
example, we could not add the sensitive terms around the clean-data step,
because again, if the new terms list becomes available immediately after that
(or right after upsert), there's no easy way to find out which records are now
missing the new designation. Given that the refresh DAG would use the
batched-update DAG, and that the batched-update DAG selects the records to work
on once at the start (rather than offsetting a select query run for each batch),
it would be working off a snapshot of works before any new works are ingested.
That means it wouldn't naturally pick up the new works as not having the new
designation.

The solution Staci and I arrived at was to have ingesters only pull the
sensitive terms list version(s) they should process once at the beginning of
their run. This ensures any ingesters that start with only the old version
available, complete their entire run with the old version, but new ones start
using both versions. Then, the refresh DAG would create the new terms list
first, and then pull a list of active ingester DAG runs. It would then wait for
only those specific DAG runs to finish before starting the batched update
process. That way, the snapshot of works it is working from, is guaranteed to be
all the works that were ingested without any awareness of the batched update.
That means the select query for the batched update can in fact select based on
`sensitivity->text->[new-list-sha]`. This eliminates the race condition.

Solving this race condition, whilst difficult to parse out at first, does not
create too much complexity. But, it is undeniably more complex than the indexer
worker approach. The indexer worker does not need to make any concessions
whatsoever to race conditions: it has none to contend with.

However, this alone was not enough to make the sensitive terms check viable in
catalogue. We also needed to make it possible to do the sensitive terms check in
Python. The motivation for this was to avoid gnarly string escape and Unicode
issues if we tried to write the check in PL/pgSQL. Likewise, in order to make
the list available to Postgres, we would need to load the sensitive terms list
into a table. To obscure the terms to avoid unintended exposure to the list, we
would need to base64 encode it, incurring a decoding cost (not to mention the
query cost) for each call to the PL/pgSQL function.

We came up with some methods to make it possible to use a Python function in
`update_batches`. Specifically, we would do something like:

- Convert `update_batches` to a task-group factory function
- Provide a new parameter of a Python function to call to generate the
  `update_query` based on the subset of rows. It would be passed the SQL to
  select the rows, and be responsible for building the `update_query` string
  based on whatever it wanted to do with the rows. This Python function would be
  used in a `PythonOperator` and would default to simple function that returns
  the `update_query` string passed to the task-group factory (this covers the
  existing use cases). Each batch of `update_batches` would call the
  `PythonOperator` and then execute the SQL based on its result.

This might be worth doing in the future, but will not be part of this particular
project.

In general, even though it was _possible_ to move sensitive text detection to
ingestion, with a refresh to backfill and update when the list changes, we could
not find any immediate benefit to doing so. The main obvious one was to avoid
unnecessarily re-checking works in each data refresh. However, there are methods
we could use to cache the result of a sensitive text check for the indexer
worker to reuse. Furthermore, we already do re-check every work each time (in
the Elasticsearch `reindex` query to create the filtered index), so the
performance characteristics are no different by doing so in the indexer worker.
There also still remained the issue of not overloading the Airflow EC2 instance
with such potentially long-running a Python-heavy computation tasks like the
sensitive text refresh would require. The indexer workers exist to offload these
kinds of heavy transformations for a reason, and without being able to easily
and confidently offload the sensitive terms check to Postgres, the performance
impact on our Airflow box is hard to precisely anticipate and therefore
impossible to accept ahead of time.

## Design

<!-- Note any design requirements for this plan. -->

There are no interface changes for this plan.

## Blockers

<!-- What hard blockers exist that prevent further work on this project? -->

See [the section on other projects](#other-projects-or-work) regarding this
plans relationship to the removal of the ingestion server.

## API version changes

<!-- Explore or mention any changes to the API versioning scheme. -->

No API version changes.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

None.

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

Before we get to the clean-up step, everything should either have no effect on
existing functionality (new Elasticsearch document field) or can be toggled by
the [feature flag](#feature-flags).

Once we get to the clean-up step, we will start to need to revert or do full
rollbacks if required. The plan should be safe enough such that we won't start
the clean-up step without having verified that the new approach works. Clean-up
will (mostly) be removing the old unused code and simplifying some downstream
effects of the old approach based on the new approach.

## Privacy

<!-- How does this approach protect users' privacy? -->

There are no changes to privacy.

## Localisation

<!-- Any translation or regional requirements? Any differing legal requirements based on user location? -->

We do not require any localisation for this project.

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

The primary risk is the indexer worker performance when executing the sensitive
term regexes. Following that, there is a risk that search performance will not
go well with the `exists` query.

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->

[I did a bit of exploring of different approaches before being assigned this implementation plan, and wrote about them in this GitHub comment](https://github.com/WordPress/openverse/issues/3336#issuecomment-2288432417).

All the other implementation plans and project proposals in the
[trust and safety category](../index.md) are significant in considering how to
approach this and set precedences that need to be followed or considered for a
comprehensive plan.
