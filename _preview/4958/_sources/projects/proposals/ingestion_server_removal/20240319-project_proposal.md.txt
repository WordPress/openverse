# 2024-03-19 Project Proposal: Removal of the Ingestion Server

**Author**: @stacimc

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @Aetherunbound
- [x] @zackkrida

## Project summary

<!-- A brief one or two sentence summary of the project's features -->

Currently, our data refresh process is _orchestrated_ by Airflow, but the work
is actually performed on a bespoke
[ingestion server](https://github.com/WordPress/openverse/tree/fc38553d04cde7586ce680543757d77a15be9a41/ingestion_server).
This server is relatively complex compared to our needs, difficult to maintain,
and makes the data refresh process unnecessarily opaque. Because the refresh is
triggered in a single task on the ingestion server, it is not possible to track
the progress in Airflow or retry it from a point of failure. Progress must be
discerned through periodic Slack notifications and inspection of logs in
Cloudwatch.

In this project, we will move all operational pieces of the data refresh into
Airflow and completely remove the ingestion server.

## Goals

<!-- Which yearly goal does this project advance? -->

This project advances the DevEx/Infrastructure goal.

Moving the process entirely into Airflow will have the following advantages for
the critical data refresh process:

- Easier iteration, as changes to the majority of the implementation can be
  deployed immediately by simply merging code in the catalog
- Increased reusability of code, particularly among the growing number of
  Elasticsearch DAGs (for example, the
  [`recreate_full_staging_index` DAG](https://github.com/WordPress/openverse/blob/fc38553d04cde7586ce680543757d77a15be9a41/catalog/dags/elasticsearch_cluster/recreate_staging_index/recreate_full_staging_index_dag.py)
  could be made entirely redundant by moving the data refresh into Airflow)
- Increased observability of the process: we'll have the ability to see exactly
  what step the refresh is on by inspecting the running DAG, with much more
  granularity even than the existing Slack notifications. This also includes
  much more convenient access to timing information.
- Automatic addition of Airflow features like pausing and retrying, with no
  additional work required beyond moving the process into Airflow:
  - Ability to pause the data refresh. While this won't automatically pause work
    that has been triggered on remote services (like queries being run in the
    API database or reindexing being performed by an indexer worker), it will
    prevent the next steps from running. For example, this allows us to pause
    the DAG before the reindexing steps are reached to prevent them from
    starting.
  - Ability to retry failed tasks without having to restart the process from the
    beginning
- Easier to introduce a staging data refresh DAG, which currently does not exist
  but which would be invaluable for testing of the process

Removing the ingestion server also has the following advantages from an
infrastructure perspective:

- Fewer services to manage overall; no maintenance of a bespoke server
- Reduced costs (no requirement for 24/7 EC2 instance)
- Improved deployments by reducing the number of deployable services, as well as
  reducing the scope of changes that require deployment

## Requirements

<!-- Detailed descriptions of the features required for the project. Include user stories if you feel they'd be helpful, but focus on describing a specification for how the feature would work with an eye towards edge cases. -->

- The data refresh process should be managed entirely by Airflow
  - The expensive reindexing step currently makes use of a fleet of
    `indexer workers`, which will still be required and which can not be
    provided by Airflow directly. These should be managed by Airflow using ECS
    or EC2 operators, but as much of the reindexing logic as possible should
    remain in the catalog itself. More specifics are left to the implementation
    plan.
- There should be no increase in the time it takes to perform a data refresh

## Success

<!-- How do we measure the success of the project? How do we know our ideas worked? -->

The project will be considered a success when at least one full audio and image
data refresh are run successfully with the new implementation, and the ingestion
server is removed. The staging and production ingestion server EC2 instances
should be deleted along with all associated code in the monorepo and
infrastructure repositories.

## Infrastructure

<!-- What infrastructural considerations need to be made for this project? If there are none, say so explicitly rather than deleting the section. -->

This project will involve removing the ingestion server entirely.

Although specific details are left to the implementation plan, at minimum it
will involve significant modifications to the existing indexer workers
responsible for the reindexing work.

## Marketing

<!-- Are there potential marketing opportunities that we'd need to coordinate with the community to accomplish? If there are none, say so explicitly rather than deleting the section. -->

None.

## Required implementation plans

<!-- What are the required implementation plans? Consider if they should be split per level of the stack or per feature. -->

The vast majority of the consideration needed for implementation planning is
related to the modifications needed for the indexer workers. We _could_ split
this work into two implementation plans:

- Mechanism for spinning up the indexer workers from Airflow, along with
  infrastructure changes needed
- Process for moving the rest of the data refresh into Airflow (data copy and
  cleaning, table/index promotion, etc)

Because the latter of these is so straightforward, it is appropriate in this
case to combine these into a single implementation plan.
