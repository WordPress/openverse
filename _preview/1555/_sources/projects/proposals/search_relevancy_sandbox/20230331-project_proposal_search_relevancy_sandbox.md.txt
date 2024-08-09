# Project Proposal - 2023-03-31

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] sarayourfriend
- [x] zackkrida
- [x] krysal

## Project summary

<!-- A brief one or two sentence summary of the project's features -->

Develop mechanisms and workflows for sustainably creating & updating our staging
API database & Elasticsearch cluster, in order to enable testing changes to
Elasticsearch indices. The staging setup will reflect production in two separate
ways using two different indices: proportionally by provider and with
production-level volumes.

## Goals

<!-- Which yearly goal does this project advance? -->

Yearly goal: **Result Relevancy**

## Requirements

<!-- Detailed descriptions of the features required for the project. Include user stories if you feel they'd be helpful, but focus on describing a specification for how the feature would work with an eye towards edge cases. -->

The following should be available once this project is complete:

1. A mechanism by which maintainers can easily update the staging API database
   with recent data.
2. A mechanism by which maintainers can create/update a small but
   proportional-to-production-by-provider index.
3. A mechanism by which maintainers can create/update a production-data-volume
   sized index.
4. A mechanism by which maintainers can easily deploy & iterate on new
   Elasticsearch indexing configurations
5. A mechanism by which maintainers can easily point the staging Elasticsearch
   index aliases (currently `image` and `audio`) to one of the above.

Many of these mechanisms will likely be built in Airflow.

### Proportional by provider

The proportional-by-provider index will be a subset of the production data,
constructed so that the number of records by provider is roughly proportional to
the percentages per provider that exist in production. This index will allow us
to iterate rapidly on the following:

- Changes affecting Elasticsearch index configuration (e.g. shard sizes,
  slicing, etc.)
- Changes to the ingestion server's configuration which require running a data
  refresh end-to-end
- Measuring index performance
- Integration testing dead link & thumbnail checks across all providers

This could be done by:

1. Querying the `/stats` endpoint of the production API (e.g.
   https://api.openverse.engineering/v1/images/stats/).
2. Calculating percentage-per-provider.
3. Computing the number of results per provider based on these percentages based
   on the condition that the smallest provider has a minimum `N` results (e.g. a
   minimum of 10 results).
4. Pulling a number of results based on the previous step per-provider either
   into a Postgres table or an Elasticsearch index (the specifics of this step
   will be left for the implementation plan).

This index will allow us to assess how changes to Elasticsearch index or the API
will affect results using a smaller total result count. It will also allow us to
test API results from all currently available providers.

### Production data volume

The production-data-volume index will be an index of similar size (i.e. on the
same order of magnitude in document count) to production. This is how the data
refresh is currently set up and does not require any additional work to set up.

This index will allow us to test how queries and indexing operations perform at
a data volume consistent with production.

## Success

<!-- How do we measure the success of the project? How do we know our ideas worked? -->

This project can be considered a success once any maintainer can make
adjustments to the staging API database & Elasticsearch index based on the
requirements described above.

## Participants and stakeholders

<!-- Who is working on the project and who are the external stakeholders, if any? Consider the lead, implementers, designers, and other stakeholders who have a say in how the project goes. -->

- Lead: @AetherUnbound
- Implementation:
  - @AetherUnbound
  - TBD
- Stakeholders:
  - Openverse Team

## Infrastructure

<!-- What infrastructural considerations need to be made for this project? If there are none, say so explicitly rather than deleting the section. -->

This project may require infrastructure work necessary to assist with the rapid
iteration of the ingestion server. Further details will be determined in the
implementation plan.

The project will also likely involve the creation or modification of Airflow
DAGs related to the data refresh and infrastructure modification. This will
require interfacing Airflow with the staging ingestion server, API database, and
Elasticsearch cluster.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this project? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

Not every member of the maintainer team is intimately familiar with Airflow - we
will need to provide clear instructions for maintainers on how to use Airflow to
run any of the above mechanisms.

## Marketing

<!-- Are there potential marketing opportunities that we'd need to coordinate with the community to accomplish? If there are none, say so explicitly rather than deleting the section. -->

No marketing is required as this is an improvement internal to the team.

## Required implementation plans

<!-- What are the required implementation plans? Consider if they should be split per level of the stack or per feature. -->

In the order they should be completed:

1. Staging API DB update procedure
   - This plan will describe a DAG which can be triggered to update the staging
     API database.
2. Rapid iteration on ingestion server index configuration
   - This plan will describe how rapid iteration of Elasticsearch index
     configurations can happen. This can be done via Airflow interacting
     directly with Elasticsearch rather than having to process requests through
     the ingestion server. Airflow would only need to be aware of the
     [existing index settings](https://github.com/WordPress/openverse/blob/0a5f4ab2ce5d80a48bd1c57d2a2dbcca14fcbedc/ingestion_server/ingestion_server/es_mapping.py)
     and how to augment/adjust them for the new index.
     ([See this comment for further inspiration](https://github.com/WordPress/openverse/pull/1107#discussion_r1155399508))
   - It should be assessed as part of this implementation plan whether it would
     be easier to convert the ingestion server to ECS or provide a mechanism on
     the existing EC2 infrastructure to update the Elasticsearch index
     configuration without issuing a deployment (similar to the
     [dag-sync script for the catalog](https://github.com/WordPress/openverse-catalog/blob/10857e3ee94ae686853984c54d504b152082d4c2/dag-sync.sh)).
3. Staging Elasticsearch reindex DAGs for both potential index types (these will
   be subsets of the full data refresh)
   - This plan will describe the DAG or DAGs which will be used to create/update
     both the proportional-by-provider and production-data-volume indices.
   - It will also describe the mechanism by which maintainers can rapidly switch
     index the staging API uses. This could be done in two separate ways: a DAG
     which allows changing the primary index alias or a set of changes to the
     API which would allow queries to specify which index they use. The
     implementation plan should explore and describe both options.
