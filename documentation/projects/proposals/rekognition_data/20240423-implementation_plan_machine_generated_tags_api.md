# 2024-04-23 Implementation Plan: Machine-generated tags in the API

**Author**: @AetherUnbound

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [ ] @krysal
- [ ] @obulat

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/431)
- [Project Proposal](/projects/proposals/rekognition_data/20240320-project_proposal_rekognition_data.md)

[parse_tags_logic]:
  https://github.com/WordPress/openverse/blob/df57ab3eb6586502995d6fa70cf417352ec68402/ingestion_server/ingestion_server/elasticsearch_models.py#L196-L206

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

The project proposal linked above endeavors to add a new set of
machine-generated tags to our catalog database as its end goal, however we
[already have records in our dataset that include machine-generated tags](https://github.com/WordPress/openverse/pull/3948#discussion_r1552301581).
Nothing currently exists to distinguish these tags from creator-generated ones.

This implementation plan will describe how we plan on conveying
machine-generated tags in the API, and also how they will be handled when
searches are made in Elasticsearch. It will not cover the semantics of the
actual labels (i.e. which machine-generated labels to retain or discard), as
that is the purview of #4040.

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

When this work is completed, it is expected that we will be able to clearly
distinguish which tags returned by the API are machine-generated. We will also
have a clearly documented approach for handling duplicate tags and how this
affects search results.

## Step-by-step plan

<!--
List the ordered steps of the plan in the form of imperative-tone issue titles.

The goal of this section is to give a high-level view of the order of implementation any relationships like
blockages or other dependencies that exist between steps of the plan. Link each step to the step description
in the following section.

If special deployments are required between steps, explicitly note them here. Additionally, highlight key
milestones like when a feature flag could be made available in a particular environment.
-->

The implementation of this work involves two primary pieces:

1. [Expose provider information for each tag within the results](#expose-provider-in-tags)
2. [Apply modifications (if necessary) to the Elasticsearch document scoring](#modify-elasticsearch-document-scoring)

## Step details

<!--
Describe all of the implementation steps listed in the "step-by-step plan" in detail.

For each step description, ensure the heading includes an obvious reference to the step as described in the
"step-by-step plan" section above.
-->

### Expose provider in tags

This step will be relatively straightforward, as the provider information for
tags already exists in the API database. In order to have them show up in the
API results, we would need to modify the
[`TagSerializer`](https://github.com/WordPress/openverse/blob/3ed38fc4b138af2f6ac03fcc065ec633d6905d73/api/api/serializers/media_serializers.py#L442)
to include the `provider` field as well. This would change the returned `tags`
entry for a result from:

```json
[
  {
    "name": "businesscard",
    "accuracy": null
  },
  {
    "name": "design",
    "accuracy": null
  },
  {
    "name": "projects",
    "accuracy": null
  },
  {
    "name": "achievement",
    "accuracy": 0.94971
  },
  {
    "name": "box",
    "accuracy": 0.90665
  },
  {
    "name": "business",
    "accuracy": 0.9916
  },
  {
    "name": "card",
    "accuracy": 0.94793
  }
]
```

to the following:

```json
[
  {
    "name": "businesscard",
    "accuracy": null,
    "provider": "flickr"
  },
  {
    "name": "design",
    "accuracy": null,
    "provider": "flickr"
  },
  {
    "name": "projects",
    "accuracy": null,
    "provider": "flickr"
  },
  {
    "name": "achievement",
    "accuracy": 0.94971,
    "provider": "flickr"
  },
  {
    "name": "box",
    "accuracy": 0.90665,
    "provider": "clarifai"
  },
  {
    "name": "business",
    "accuracy": 0.9916,
    "provider": "clarifai"
  },
  {
    "name": "card",
    "accuracy": 0.94793,
    "provider": "clarifai"
  }
]
```

Because this is the addition of a new entry in the `tags` object array and not a
removal or modification of the existing data, we should not need to modify the
API version at this time.

The availability of `provider` here will make it possible to visually
distinguish the different tag sources, which will be established in #4039.

### Modify Elasticsearch document scoring

We already have records in our dataset that include duplicate tags (one
creator-generated tag, and one machine-generated tag,
[example with "light" duplicated](https://api.openverse.engineering/v1/images/a487f4eb-ce05-43e1-acae-73c4ab090cc9/)).
As we grow the number of machine-labeling providers we apply to our data, it's
possible we will end up with multiple copies of a single tag from different
providers. There are four approaches we can take for these cases concerning
scoring in Elasticsearch:

- Prefer creator-generated tags and exclude machine-generated tags
- Prefer machine-generated tags and exclude creator-generated tags
- Prefer the creator-generated tags, but use the presence of an identical
  machine-labeled tag to boost the score/weight of the creator-generated tag in
  searches
- Keep both tags, acknowledging that this will increase the score of a
  particular result for searches that match said tag (**current behavior,
  recommended approach moving forward**)

For text-based fields, Elasticsearch provides
[two options for scoring that don't require further configuration](https://www.elastic.co/guide/en/elasticsearch/reference/master/similarity.html):
`BM25` and `boolean`. `BM25` is the default algorithm, and it will boost a
document's score based on the number of times the search term appears in the
document[^bm25_explanation]. The `boolean` algorithm only scores a document
whether the search term matches _at all_, rather than the number of times it is
matched within the document.

We presently use `boolean` for the
[`title`](https://github.com/WordPress/openverse/blob/3f3376cfea8a4355229d4fb7d3a69a299de8cba4/ingestion_server/ingestion_server/es_mapping.py#L80)
and
[`description`](https://github.com/WordPress/openverse/blob/3f3376cfea8a4355229d4fb7d3a69a299de8cba4/ingestion_server/ingestion_server/es_mapping.py#L89)
fields[^bm25_change]. The `tags` field (specifically the
[`name` subfield which is what gets indexed](https://github.com/WordPress/openverse/blob/3f3376cfea8a4355229d4fb7d3a69a299de8cba4/ingestion_server/ingestion_server/es_mapping.py#L110-L117))
does not have an explicit `similarity` defined, and therefore it is already
using the `BM25` algorithm.

Below is a discussion of each approach, with the advantages & disadvantages for
taking said approach.

[^bm25_explanation]:
    Note that it does not do this naively, as Okapi BM25 has additional
    complexity involved for how prevalent the search term is in the entire
    dataset. For more information, see: https://en.wikipedia.org/wiki/Okapi_BM25

[^bm25_change]:
    #751 intends to explore changing this, but it is blocked by #421.

#### Prefer creator-generated tags and exclude machine-generated tags

The easiest way to handle this approach would be to add some logic to the data
refresh's [tag processing step][parse_tags_logic] which would exclude any tags
that did not match the document's provider. However, this would also mean that
the machine-generated tags would not be able to contribute to a document's
scoring (and therefore its search relevancy). This seems counter to our desire
for adding the machine-generated labels in general and would only serve to
provide more context/information for API consumers _once they have the result_.
If they're unable to find the result in the first place, then the presence of
the machine-generated labels is irrelevant here.

#### Prefer machine-generated tags and exclude creator-generated tags

Similar to
[the previous step](#prefer-creator-generated-tags-and-exclude-machine-generated-tags),
this could be accomplished by adding logic to the [tag processing
step][parse_tags_logic] to exclude tags that have a provider which matches the
document's provider. This feels like the wrong approach for a few reasons:

- At present, we have far fewer machine-generated tags than we do records with
  creator-generated tags. This change would necessarily have an impact on search
  performance, and since tags are one of the 3 text fields that get searched for
  a query term, it would likely make a large portion of records no longer show
  up in the results.
- Many of our sources include
  [GLAM institutions](<https://en.wikipedia.org/wiki/GLAM_(cultural_heritage)>).
  These groups often go to great lengths to appropriately catalog and tag the
  works that we ingest, and excluding those tags from being searched against
  would go against that effort.
- Machine-generated labeling is inherently biased, and may be incorrect in some
  cases.

#### Prefer the creator-generated tags, but boost on duplicate machine-generated tags

This approach would likely need to leverage a custom
[`rank_feature`](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-rank-feature-query.html)[^rank_feature]
or
[`function_score`](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-function-score-query.html).
This would only give us the benefit of machine-generated tags _in cases where
the machine tags matched the creator tags_. In other words, this would only
improve the relevancy of results that were already present in search results for
a given search term, it would not add any _new_ records to searches if the
record did not already match for that term. In some of the exploratory analysis
that was performed on the Rekognition-labeled images, maintainers discovered
that the machine-generated tags were able to add relevant terms for images which
did not have those tags already. For instance, an image of a cat with only the
tag "best friend" from the creator would not show up under a search for "cat" in
this case, even though the image has a cat in it and even if a machine-generated
tag for "cat" were present.

[^rank_feature]:
    We already have a number of `rank_feature` fields, which could be used as a
    basis for this approach:
    https://github.com/WordPress/openverse/blob/3f3376cfea8a4355229d4fb7d3a69a299de8cba4/ingestion_server/ingestion_server/es_mapping.py#L96-L104

#### Keep both tags and allow that to affect the document score

This is the current approach, and also the simplest: leave the default
`similarity` setting for `tags` and allow a result with duplicate tags to
receive a higher score. This has the following advantages:

- No action on the Elasticsearch index settings is needed (save more
  documentation).
- Machine-generated labels can help boost images with content that's relevant
  for searches even if the other fields (`title`/`description`/`tags`) do not
  mention the image content.
- Records with duplicate machine- and creator-generated tags mean those tags are
  likely quite relevant, and a higher score for them seems appropriate.
- Records which don't have machine-generated labels are unaffected.

#### Conclusion

For all the reasons and explanation provided above, we should move forward with
the
[approach to keep both sets of tags](#keep-both-tags-and-allow-that-to-affect-the-document-score).

## Dependencies

### Feature flags

<!-- List feature flags/environment variables that will be utilised in the development of this plan. -->

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

### Tools & packages

<!-- Describe any tools or packages which this work might be dependent on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

## Alternatives

<!-- Describe any alternatives considered and why they were not chosen or recommended. -->

## Design

<!-- Note any design requirements for this plan. -->

## Blockers

<!-- What hard blockers exist that prevent further work on this project? -->

## API version changes

<!-- Explore or mention any changes to the API versioning scheme. -->

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

## Privacy

<!-- How does this approach protect users' privacy? -->

## Localization

<!-- Any translation or regional requirements? Any differing legal requirements based on user location? -->

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->
