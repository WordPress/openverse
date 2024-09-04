# 2024-09-03 Implementation Plan: Undo the split indices for filtered textual sensitivity

**Author**: @sarayourfriend

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [ ] @dhruvkb (API familiarity, especially in code that interacts with ES
      during moderation)
- [ ] @stacimc (Data refresh and ingestion worker expertise)

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
[a new `sensitivity` field for each Elasticsearch document](https://github.com/WordPress/openverse/blob/df57ab3eb6586502995d6fa70cf417352ec68402/ingestion_server/ingestion_server/elasticsearch_models.py#L78-L128).
The field will be a keyword-list field, to match the `unstable__sensitivity`
field in the API. The valid keywords
[will match those used by the API](https://github.com/WordPress/openverse/blob/46a42f7e2c2409d7a8377ce188f4fafb96d5fdec/api/api/constants/sensitivity.py#L1-L12):

- `sensitive_text`: included for a document when the title, tags, or description
  of the work include any of the sensitive terms.
- `user_reported_sensitivity`: included for a document there is a confirmed
  sensitive content report for the work.

Details of the programming logic for each are covered in the
[step details section](#step-details).

```{admonition} Rationale for a new index field
:class: hint

While the filtered index currently exists to represent works free of sensitive
textual content, we can somewhat simplify the overall handling of sensitive
works in search by approaching this problem with both modes of sensitivity in
mind. The current approach to searching non-sensitive works is to search the
filtered index _and_ exclude works[^must-not] where `mature=true`. By switching
to a single field populated with the sensitivity designations, we can simplify
the search for non-sensitive works by filtering for when the `sensitivity` field
is empty.
```

[^must-not]:
    We use the boolean `must_not` with a match query to exclude works.
    Elasticsearch turns the match query into a Lucene `TermQuery`. Elasticsearch
    prefers “positive” queries, so this is faster than a `filter` for
    `mature:false`. We will use `must_not` with an exists query to exclude based
    on the presence of `sensitivity` entries.

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

Based on the requirement to not negatively affect overall search performance, I
wanted to make sure there weren't any obvious or glaring problems with using the
field-exists approach.

Whereas querying the `mature` field for a boolean value is a `match` field
query, querying the existence of a field uses `exists`. We do not have anything
directly analogous to try with in our existing data set. However, we do have
works with no tags. Therefore, I decided to attempt a comparison of queries for
works with no tags and `mature=false` works.

Compare these two queries.

<details>
<summary>The proposed approach: <code>must_not exists:sensitivity</code></summary>

```json
// POST image/_search
{
  "from": 0,
  "highlight": {
    "fields": {
      "description": {},
      "tags.name": {},
      "title": {}
    },
    "order": "score"
  },
  "query": {
    "bool": {
      "must": [
        {
          "simple_query_string": {
            "default_operator": "AND",
            "fields": ["title", "description", "tags.name"],
            "flags": "AND|NOT|PHRASE|WHITESPACE",
            "query": "water"
          }
        }
      ],
      "must_not": [
        {
          "exists": {
            "field": "tags.name"
          }
        }
      ],
      "should": [
        {
          "simple_query_string": {
            "boost": 10000,
            "fields": ["title"],
            "flags": "AND|NOT|PHRASE|WHITESPACE",
            "query": "water"
          }
        },
        {
          "rank_feature": {
            "boost": 10000,
            "field": "standardized_popularity"
          }
        }
      ]
    }
  },
  "size": 20
}
```

</details>

<details>

<summary>Our current mature-filter query: <code>must_not mature=false</code></summary>

```json
// POST image/_search
{
  "from": 0,
  "highlight": {
    "fields": {
      "description": {},
      "tags.name": {},
      "title": {}
    },
    "order": "score"
  },
  "query": {
    "bool": {
      "must": [
        {
          "simple_query_string": {
            "default_operator": "AND",
            "fields": ["title", "description", "tags.name"],
            "flags": "AND|NOT|PHRASE|WHITESPACE",
            "query": "water"
          }
        }
      ],
      "must_not": [
        {
          "term": {
            "mature": true
          }
        }
      ],
      "should": [
        {
          "simple_query_string": {
            "boost": 10000,
            "fields": ["title"],
            "flags": "AND|NOT|PHRASE|WHITESPACE",
            "query": "water"
          }
        },
        {
          "rank_feature": {
            "boost": 10000,
            "field": "standardized_popularity"
          }
        }
      ]
    }
  },
  "size": 20
}
```

</details>

I was worried that a boolean query would perform much better. In fact, if you
remove all other aspects of the query (the actual text-search parts), it does
seem to indicate that an exists query is much slower than the boolean match
query. Crucially, however, if you use a real query from our application as a
starting point, **there appears to be zero performance difference between the
two**.

It's hard to give hard numbers, because I didn't write a script to analyse this
and executed the queries and looked at the results by hand. But, executing both
queries against the staging cluster resulted in the similar "took" results.
Regardless of the approach, "took" was always usually between 39 and 51. Even
when I changed the search term to try to avoid the query cache, both appeared to
perform identically.

However, there were instances where the tags-exists-based query was faster, by
around 4 times. That, I believe, is due to the difference in the output of the
two queries. The tag-exists-based query was naturally spending less time
fetching the list of tags for each document, as none of the results had tags.
The mature-boolean-based query, however had tags in almost every result in the
first 20 which were requested, and so did have to spend time fetching tags for
each document.

The differences between the `tags` field and the proposed `sensitivity` field
make it hard to do an ahead-of-time comparison. However, as I've said above, I
think this broad (and admittedly naïve!) performance analysis is sufficient to
allow us to move forward with implementing the list approach to begin with. If
we encounter a performance issue, we can easily collapse the list into a
`has_sensitivty` boolean for when we just want to exclude anything with a
sensitivity designation.

```{note}
[Please see the note in the linked code above regarding provider
supplied sensitivity](https://github.com/WordPress/openverse/blob/46a42f7e2c2409d7a8377ce188f4fafb96d5fdec/api/api/constants/sensitivity.py#L4-L7).

This plan makes no explicit consideration for provider supplied sensitivity.
However, I believe the approach described in this plan increases, or at
least maintains, our flexibility in the event it becomes relevant (i.e.,
we start intentionally ingesting works explicitly designated as sensitive
or mature by the source).
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

1. Generate a usable `sensitivity` field for Elasticsearch documents (1 PR)
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

- Indexer worker field generation:
  - Retrieve the sensitive terms list from the GitHub URL (see data refresh for
    reference) and make the list available to the indexer processes without
    requiring subsequent outbound requests for the list.
    - Create a new Python module in the indexer worker, `sensitive_terms.py`. It
      will export the following:
      - A constant `SENSITIVE_TERMS_LOC` set to
        `Path(__file__).parent / "sensitive_terms.txt"`. Indexer workers are
        ephemeral, so it is safe to write to disk without risking accidental
        reuse across runs.
      - A function `retrieve_sensitive_terms` which retrieves the sensitive
        terms list from the network location and saves it to disk at
        `SENSITIVE_TERMS_LOC`. This function should check an environment
        variable for the network location of the sensitive terms list. If that
        variable is undefined, it should simply write the mock sensitive terms
        ("water", "running", and "bird") to the disk location as a
        newline-delimited list.
      - A function `get_sensitive_terms`, which will be wrapped in
        `@functools.cache`. The function will read `SENSITIVE_TERMS_LOC` and
        split the result on newline and return a tuple of compiled sensitive
        term regexes. The regexes will target sensitive terms that are
        surrounded by word boundaries.
        [Refer to this demonstration on Regexer using the mock term "water" and the expression `\bwater\b`](https://regexr.com/85gtv).
        - Using a regex is unfortunately necessary to ensure we do not have
          false-positives on non-sensitive terms in sub-portions of words, as
          with location names like
          [Shitterton in Dorset County, UK](https://en.wikipedia.org/wiki/Shitterton).
          This is a minimum consideration we should give in light of our
          acknowledgement that text-based matching
          [is not perfect](./20230309-implementation_plan_sensitive_terms_list.md#this-will-not-be-perfect).
        - The use of compiled regexes makes caching the result especially
          important so that regex compilation is not unnecessarily repeated
          within a single indexer worker subprocess.
        - We should start with a single regex per term. In the future, we can
          consider combining slices of the sensitive terms list into larger
          regex statements, and evaluate whether this performs better or worse
          for our corpus. For now, we will keep it as simple as possible, with a
          single regex per term. It does not change the downstream code to do
          so, and introduces fewer complications with respect to regex
          construction.
    - The indexer worker will call `retrieve_sensitive_terms` on service
      startup. Add this to `api.create_api`. This populates the file to disk.
    - Because each indexer worker spawns multiple multiprocessing processes,
      each of which have independent Python interpreters, we rely on
      `functools.cache` to ensure each subprocess only has to parse
      `get_sensitive_terms` once, regardless of the number of documents it
      processes. This also ensures the list is available to `get_instance_attrs`
      and related functions without needing to pass it around as a new argument
      from somewhere "below" `launch_reindex` in the call stack for document
      processing.
  - The primary logic will live as an extension to the indexer worker's static
    `elasticsearch_models.Model::get_instance_attrs`.
    - Add a new static method
      `elasticsearch_models.Model::get_text_sensitivity`.
      - This method will use `sensitive_terms.get_sensitive_terms` to retrieve
        the sensitive terms tuple.
      - Iterating through the sensitive term regexes and test the title,
        description, and each tag against the regex. If the term is in any
        field, immediately return true. We only need to test terms until we find
        one matching term, so it is safe to break the loop early once we find
        one.
    - Update `get_instance_attrs` to create a new `sensitivity` list field. If
      the call to `Model::get_text_sensitivity` is true, include
      `sensitive_text` in the list. Additionally, if `row[schema["mature"]]` is
      true, add `user_reported_sensitivity` to the list.
- Update the index mappings to add the new `sensitivity` field set to
  `{"type": "keyword"}`.

After merging the PR, run the staging data refresh and confirm the new field
appears in new indices and is queryable (manually run queries against it). It is
not necessary to manually run the production data refresh, and it is highly
unlikely we will complete, review, and merge the API work before a production
data refresh runs.

### Step 2: Update the API to use the new field (behind a feature flag)

Complete the following in two PRs.

- First PR: search
  - Add a new feature-flag environment variable `USE_INDEX_BASED_SENSITIVITY`
    that defaults to false.
  - Update search for the new query approach:
    - Modify `search_controller.get_index` to check the feature flag and return
      the unfiltered index when it is true. Otherwise, it should follow its
      existing logic.
    - Update `search_controller.build_search_query` to also check the feature
      flag. When it is false, use the existing `mature` based strategy for
      handling `include_sensitive_results`. When it is true and
      `include_sensitive_results` is false, add a new `must_not` entry with an
      exists query on the `sensitivity` field.
    - Finally, update `search_controller.query_media` to check the feature flag,
      and when true, bypass the `SearchContext.build` call and create
      `SearchContext` directly, as described below.
      - Retaining the `result_ids` list, create the `SearchContext` with
        `SearchContext(result_ids, {result.identifier for result in results if result.sensitivity})`.
      - While this change to a single index and building the sensitivity list
        upstream of the API allows us to eventually remove `SearchContext`, we
        will retain it for now and mock its usage. This allows us to avoid
        needing to add the same feature flag checks in `MediaView` and
        `MediaSerializer`. Instead, we can leave those alone for now, and the
        same `sensitivity` list will continue to be populated by the serializer.
        Once we confirm this feature and enter the clean-up phase, we will
        remove `SearchContext` altogether. Details for this are in the
        [clean-up section](#step-4-clean-up).
- Second PR: moderation
  - Update `AbstractSensitiveMedia._bulk_update_es` to pass a script update that
    append `user_reported_sensitivity` to the `sensitivity` list, or creates the
    list if needed.
    - Refer to
      [the Elasticsearch documentation on updates for examples of scripted updates](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-update.html#update-api-example).
    - [Refer to the following section for an example script to work from](#bulk-update-painless-script).
    - This should happen in addition to the `mature` update that already exists,
      but **must not be conditional on the `USE_INDEX_BASED_SENSITIVTY` feature
      flag**. It cannot be conditional in order to truly support the feature
      flag's accuracy in search results. If we toggle the flag on/off/on before
      a data refresh runs, the `sensitivity` list must still get updated with
      user-reported sensitivity. Otherwise, when the feature goes back on, the
      `sensitivity` list would not reflect the fact that those works had been
      reviewed and confirmed as sensitive. In that case, they would start
      reappearing in default search results (non-sensitive search).
  - Update `MediaListAdmin.has_sensitive_text` to check the `sensitivity` field
    of the Elasticsearch document if `USE_INDEX_BASED_SENSITIVITY` is true.
    - The method currently uses a term query to get the result with the
      identifier.
      [We should refactor this to use a single document `get` query by `id`](https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/examples.html#ex-get).
      Elasticsearch document `id` matches the Django model's `pk`. Doing so
      should improve the retrieval speed, and reduces the result to a single
      document, which makes reading the `sensitivity` field when retrieving it
      much easier.
    - When `USE_INDEX_BASED_SENSITIVITY` is true, query the "full" index instead
      of the filtered index.

#### Bulk update Painless script

The following script works to safely add a designation to the sensitivity list:

```json
{
  "script": {
    "source": "if (Objects.isNull(ctx._source.sensitivity)) { ctx._source.sensitivity = new String[] {params.designation} } else if (!ctx._source.sensitivity.contains(params.designation)) { ctx._source.sensitivity.add(params.designation) }",
    "lang": "painless",
    "params": {
      "designation": "user_reported_sensitivity"
    }
  }
}
```

We will store the script as a Python multi-line string to aid with readability
and maintenance. The Elasticsearch REST API will accept this string as-is, and
we do not need to modify it to remove newlines. Add the following to
`constants.sensitivity`:

```py
ADD_SENSITIVITY_DESIGNATION_PAINLESS = """
if (Objects.isNull(ctx._source.sensitivity)) {
    ctx._source.sensitivity = new String[] {params.designation}
} else if (!ctx._source.sensitivity.contains(params.designation)) {
    ctx._source.sensitivity.add(params.designation)
}
"""

def add_sensitivity_designation_script_query(designation):
    return {
        "script": {
            "source": ADD_SENSITIVITY_DESIGNATION_PAINLESS,
            "lang": "painless",
            "params": {
                "designation": designation,
            },
        },
    }
```

The API unit tests run against the real Elasticsearch cluster, so the result of
running the script as part of the sensitive-media document update should be
"painless"[^😛] to test.

[^😛]: 😛

### Step 3: Turn on feature flag in live environments and observe

Set `USE_INDEX_BASED_SENSITIVITY` to `True` in staging and redeploy. Confirm
search against the new indices created with the staging data refresh works,
including sensitive and non-sensitive queries. Also test and verify the
moderation features by confirming a sensitivity report in staging and making
sure the work is updated with `user_reported_sensitivity`.

If the production data refresh has not yet run, wait for it to run on its
regular cadence, and confirm the new `sensivitiy` field as we did in staging in
step 1.

After confirming the production indices, set `USE_INDEX_BASED_SENSITIVITY` to
`True` in production and redeploy. Monitor production API search times as well
as resource usage. Monitor the production Elasticsearch cluster health in
Kibana, and check I/O operations for the data nodes. You may also check overall
disk operations for the entire cluster in CloudWatch.

### Step 4: Clean up

1. Data refresh

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

1. API code

- Remove `search_controller.get_index` and its usage.
- Remove mature content exclusion based on the `mature` boolean from
  `build_search_query`.
- Update `MediaView::get_db_results` to merge `sensitivity` from the
  Elasticsearch `Hit` onto the Django model for each result.
- Update `MediaSerializer::unstable__sensitivity` to merely return `sensitivity`
  from the object:
  - Change the field to a `serializers.ListField` and delete
    `get_unstable__sensitivity`.
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
sure [the reviewers](#reviewers) are well equipped to correct me on this.
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
