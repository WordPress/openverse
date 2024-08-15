# 2024-03-20 Project Proposal: Incorporate Rekognition data into the Catalog

**Author**: @AetherUnbound

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @stacimc
- [x] @obulat

## Project summary

<!-- A brief one or two sentence summary of the project's features -->

[AWS Rekognition data][aws_rekognition] in the form of object labels was
collected by
[Creative Commons several years ago](https://creativecommons.org/2019/12/05/cc-receives-aws-grant-to-improve-cc-search/)
for roughly 100m image records in the Openverse catalog. This project intends to
augment the existing tags for the labeled results with the generated tags in
order to improve search result relevancy.

[aws_rekognition]: https://aws.amazon.com/rekognition/

## Goals

<!-- Which yearly goal does this project advance? -->

Improve Search Relevancy

## Requirements

<!-- Detailed descriptions of the features required for the project. Include user stories if you feel they'd be helpful, but focus on describing a specification for how the feature would work with an eye towards edge cases. -->

This project will be accomplished in two major pieces:

1. Determining how machine-generated tags will be displayed/conveyed in the API
   and the frontend
2. Augmenting the catalog database with the tags we deem suitable

Focusing on the frontend first may seem like putting the cart before the horse,
but it seems prudent to imagine how the _new_ data we add will show up in both
the frontend and the API. While both of the above will be expanded on in
respective implementation plans, below is a short description of each piece.

### Machine-generated tags in the API/Frontend

Regardless of the specifics mentioned below, the implementation plans **must**
include a mechanism for users of the API and the frontend to distinguish
creator-generated tags and machine-generated ones. Even across providers,
creator-generated tags can have quite different characteristics: some providers
machine-generate their own tags, in some providers we use the categories the API
provides as tags. It's important that we differentiate these tags from the ones
we apply after-the-fact with our own ML/AI techniques.

#### API

The API's [`tags` field][api_tags_field] already has a spot for `accuracy`,
along with the tag `name` itself. This is where we will include the label
accuracy that Rekognition provides alongside the label. We should also use the
[existing `provider` key within the array of tag
objects][catalog_tags_provider_field] in order to communicate where this
accuracy value came from. In the future, we may have multiple instances of the
same label with different `provider` and `accuracy` values (for instance, if we
chose to apply multiple machine labeling processes to our media records).

Multiple instances of the same label will also affect relevancy within
Elasticsearch, as duplicates of a label will constitute multiple "hits" within a
document and boost its score. While the exact determination should be made
within the API's implementation plan, we will need to consider one of the
following approaches for resolving this in Elasticsearch:

- Prefer creator-generated tags and exclude machine-generated tags
- Prefer machine-generated tags and exclude creator-generated tags
- Keep both tags, acknowledging that this will increase the score of a
  particular result for searches that match said tag
- Prefer the creator-generated tags, but use the presence of an identical
  machine-labeled tag to boost the score/weight of the creator-generated tag in
  searches

_NB: We believe this change to the API response shape for `tags` would not
constitute an API version change. I do think having a mechanism to share tag
provider will be important going forward[^1]._

[^1]:
    It should be relatively easy to expose the `provider` in the `tags` field on
    the API by adding it to the
    [`TagSerializer`](https://github.com/WordPress/openverse/blob/3ed38fc4b138af2f6ac03fcc065ec633d6905d73/api/api/serializers/media_serializers.py#L442)

[api_tags_field]:
  https://api.openverse.engineering/v1/#tag/images/operation/images_search
[catalog_tags_provider_field]:
  https://github.com/WordPress/openverse/blob/3ed38fc4b138af2f6ac03fcc065ec633d6905d73/catalog/dags/common/storage/media.py#L286

#### Frontend

We should also distinguish the machine-generated tags from the creator-added
ones in the frontend. Particularly with the introduction of the
[additional search views](../additional_search_views/index.md), we will need to
consider how these machine-generated tags are displayed and whether they can be
interacted with in the same way. Similar to the API, it may also be useful to
share the label accuracy with users (either visually or with extra content on
mouse hover) along with its provider (for cases where we may have multiples of
the same machine-generated tags from different sources). It would be beneficial
to have a page much like our
[sensitive content explanation](https://openverse.org/sensitive-content) (either
similarly available in the frontend or on our documentation website) that
describes the nature of the machine generated labels, the means by which they
were determined, and how to report an insensitive label.

None of the above is specific to Rekognition, but it will be necessary to
determine for Rekognition or any other labels we wish to add in the future.

### Augmenting the catalog

Once we have a clear sense of how the labels will be shared downstream, we can
incorporate the labels themselves into the catalog database. This can be broken
down into three steps:

1. Determine which labels to use (see
   [label determination](#label-determination))
2. Determine an accuracy cutoff value
3. Upsert the filtered labels into the database

Once step 3 is performed, the next data refresh will make the tags available in
the API and the frontend. The specifics for each step will be determined in the
implementation plan for this piece. Note that once introduced, the tags will not
be removed by subsequent updates to the catalog data. This means that any
adjustment/removal of the tags will also need to occur on the catalog.

#### Label determination

The exhaustive list of AWS Rekognition labels can be downloaded here:
[AWS Rekognition Labels](https://docs.aws.amazon.com/rekognition/latest/dg/samples/AmazonRekognitionLabels_v3.0.zip).
While this list is already fairly demographically neutral, it is my opinion that
we should exclude labels that have a demographic context in the following
categories:

- Age
- Gender
- Sexual orientation
- Nationality
- Race

These seem the most likely to result in an incorrect or insensitive label (e.g.
gender assumption of an individual in a photo). There are other categories which
might be useful for search relevancy and are less likely to be applied in an
insensitive manner. Some examples include:

- Occupation
- Marital status
- Health and disability status
- Political affiliation or preference
- Religious affiliation or preference

Specifics for how this will be tackled regarding the Rekognition data will be
outlined in the associated implementation plan.

## Success

<!-- How do we measure the success of the project? How do we know our ideas worked? -->

This project can be marked as success once the machine-generated tags from
Rekognition are available in both the API and the frontend.

If the labels themselves are observed to have a negative impact on search
relevancy, we will need a mechanism or plan for the API for suppressing or
deboosting the machine-labeled tags without having to remove them entirely (_NB:
We may be able to leverage some of the DAGs created as a part of the
[search relevancy sandbox](../search_relevancy_sandbox/20230331-project_proposal_search_relevancy_sandbox.md)
project for this rollback_). We do not currently have the capacity to accurately
and definitively assess result relevancy, though we plan to build those tools
out in #421. We still feel that this project has value _now_, much like the
[introduction of iNaturalist data did](https://make.wordpress.org/openverse/2023/01/14/preparing-for-inaturalist/)
even though we incurred the same risks with that effort.

The S3 bucket containing the Rekognition data will persist in perpetuity even
after this project's completion, though it can be moved to an infrequent access
storage class after the initial data import is complete. This will allow us to
perform additional extractions on the data in the future if desired.

## Participants and stakeholders

<!-- Who is working on the project and who are the external stakeholders, if any? Consider the lead, implementers, designers, and other stakeholders who have a say in how the project goes. -->

- **Lead**: @AetherUnbound
- **Design**: @fcoveram _(if any frontend design is deemed necessary)_
- **Implementation**: Implementation may be necessary for the frontend, API, and
  catalog; all developers working on those aspects of the project could be
  involved.

## Infrastructure

<!-- What infrastructural considerations need to be made for this project? If there are none, say so explicitly rather than deleting the section. -->

The Rekognition data presently exists in an S3 bucket that was previously
accessible to @zackkrida. We will need to ensure that the bucket is accessible
by whatever resources are chosen to process the data. This was
[previously done](https://github.com/WordPress/openverse/issues/431#issuecomment-1675434911)
by manually instantiating an EC2 instance to run
[a python script which generated a labels CSV](https://gist.github.com/zackkrida/cb125155e87aa1c296887e5c27ea33ff).
We may instead wish to either run any pre-processing locally or set up an
Airflow DAG which would perform the processing for us.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this project? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

The greatest concern on accessibility would be ensuring whatever mechanism we
use for conveying the machine-generated nature/accuracy values in the frontend
is also reflected in a suitable manner for screen readers.

## Marketing

<!-- Are there potential marketing opportunities that we'd need to coordinate with the community to accomplish? If there are none, say so explicitly rather than deleting the section. -->

We should share the addition of the new machine-generated tags publicly once
they are present in both the API and the frontend.

## Required implementation plans

<!-- What are the required implementation plans? Consider if they should be split per level of the stack or per feature. -->

The requisite implementation plans reflect the primary pieces of the project
described above:

- Determine and design how machine-generated tags will be displayed/conveyed in
  the API
- Determine and design how machine-generated tags will be displayed/conveyed in
  the frontend
- Augment the catalog database with the suitable tags

The most important, blocking aspect of this work is determining how the labels
will be surfaced in API results. Once that is determined, the frontend can be
modified to exclude those values visually while the designs and implementation
are executed. All work after that point can occur simultaneously.
