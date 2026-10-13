# 2023-04-06 Project Proposal: Popularity Calculation Optimizations

**Author**: @stacimc

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @AetherUnbound
- [x] @obulat

## Project summary

<!-- A brief one or two sentence summary of the project's features -->

Reduce the length of time required for a data refresh by optimizing the
popularity calculation steps, which are currently both time consuming and
required steps. These optimizations will enable the data refresh to be run on a
regular automated schedule.

## Goals

<!-- Which yearly goal does this project advance? -->

Yearly goal: **Data Inertia**

## Requirements

<!-- Detailed descriptions of the features required for the project. Include user stories if you feel they'd be helpful, but focus on describing a specification for how the feature would work with an eye towards edge cases. -->

Any changes to the data refresh and popularity calculations must meet the
following criteria:

1. A full data refresh should reliably complete in less than one week, for each
   media type.
2. During a data refresh, all updates made to existing records since the
   previous refresh should propagate to the API DB and Elasticsearch.
3. During a data refresh, all _new_ records ingested since the previous refresh
   should propagate to the API DB and Elasticsearch.
4. Records for providers that support popularity metrics should have
   standardized popularity scores as soon as they become available in
   Elasticsearch.
5. When popularity constants and standardized scores are being updated, the data
   refresh runtime should not be affected.
6. There must be no 'down-time' in the Catalog, where writes to the media tables
   are locked (i.e., ingestion workflows should be able to continue as normal at
   all times).
7. Query time in the API must not be increased.

Ideally, we should have no regression in the regularity with which popularity
constants are recalculated and normalization scores refreshed. Currently this
happens monthly. However, as long as the stated requirements are met, it will be
acceptable to recalculate constants and scores on a quarterly basis.

## Success

<!-- How do we measure the success of the project? How do we know our ideas worked? -->

For this project to be considered a success, we must be able to turn on the data
refresh DAGs with an automated weekly schedule. This requires that the data
refresh must be able to complete in under a week.

The requirements in the section above should also be met to prevent regressions
in data quality and availability.

## Participants and stakeholders

<!-- Who is working on the project and who are the external stakeholders, if any? Consider the lead, implementers, designers, and other stakeholders who have a say in how the project goes. -->

- Lead: @stacimc
- Implementation:
  - @stacimc
  - TBD
- Stakeholders:
  - Openverse Team

## Infrastructure

<!-- What infrastructural considerations need to be made for this project? If there are none, say so explicitly rather than deleting the section. -->

This project will require:

- changes to the Catalog database schema
- creation and modification of Airflow DAGs related to the data refresh
- minor changes in the ingestion server

Specifics will be detailed in the implementation plan. For testing, this will
require connecting Airflow with the staging ingestion server and API database.

I do not anticipate changes to the Elasticsearch mapping or queries. However it
should be noted that if this changes, we may require access to the Search
Relevancy Sandbox in order to test.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this project? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

This project should not have any frontend facing changes. However it will touch
many complex parts of ingestion, popularity calculation, and the data refresh,
and there must be a significant effort at each stage to document both previously
undocumented processes and the additions made here.

## Marketing

<!-- Are there potential marketing opportunities that we'd need to coordinate with the community to accomplish? If there are none, say so explicitly rather than deleting the section. -->

This change is largely internal and may present few marketing opportunities.
However, since it will enable us to get automated data refreshes running
consistently, there may be a significant increase in records in Elasticsearch
after the project completes. We should check the record count difference and
make an announcement if it is significant.

## Required implementation plans

<!-- What are the required implementation plans? Consider if they should be split per level of the stack or per feature. -->

1. Removing the popularity steps from the data refresh DAG
   - This plan will describe changes needed to separate the popularity
     calculations from the data refresh, including necessary changes to:
     - The data structure
     - New and existing DAGs
     - The ingestion server
