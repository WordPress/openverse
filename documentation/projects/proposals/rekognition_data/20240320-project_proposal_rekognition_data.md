# 2024-03-20 Project Proposal: Incorporate Rekognition data into the Catalog

**Author**: @AetherUnbound

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [ ] @stacimc
- [ ] @obulat

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
creator-generated tags and machine-generated ones.

The API's [`tags` field][api_tags_field] already has a spot for `accuracy`,
along with the tag `name` itself. This is where we will include the label
accuracy that Rekognition provides alongside the label. We should also use the
[existing `provider` key within the array of tag
objects][catalog_tags_provider_field] in order to communicate where this
accuracy value came from. In the future, we may have multiple instances of the
same label with different `provider` and `accuracy` values (for instance, if we
chose to apply multiple machine labeling processes to our media records).

_NB: I'm not sure if this change to the API response shape for `tags` would
constitute an API version change. I do think having a mechanism to share tag
source will be important going forward._

[api_tags_field]:
  https://api.openverse.engineering/v1/#tag/images/operation/images_search
[catalog_tags_provider_field]:
  https://github.com/WordPress/openverse/blob/3ed38fc4b138af2f6ac03fcc065ec633d6905d73/catalog/dags/common/storage/media.py#L286

We should also distinguish the machine-generated tags from the creator-added
ones in the frontend. Particularly with the introduction of the
[additional search views](../additional_search_views/index.md), we will need to
consider how these machine-generated tags are displayed and whether they can be
interacted with in the same way. Similar to the API, it may also be useful to
share the label accuracy with users (either visually or with extra content on
mouse hover).

None of the above is specific to Rekognition, but it will be necessary to
determine for Rekognition or any other labels we wish to add in the future.

### Augmenting the catalog

Once we have a clear sense of how the labels will be shared downstream, we can
incorporate the labels themselves into the catalog database. This can be broken
down into three steps:

1. Determine which labels to use
2. Determine an accuracy cutoff value, if any
3. Upsert the filtered labels into the database

Once step 3 is performed, the next data refresh will make the tags available in
the API and the frontend. The specifics for each step will be determined in the
implementation plan for this piece.

## Success

<!-- How do we measure the success of the project? How do we know our ideas worked? -->

This project can be marked as success once the machine-generated tags from
Rekognition are available in both the API and the frontend.

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
