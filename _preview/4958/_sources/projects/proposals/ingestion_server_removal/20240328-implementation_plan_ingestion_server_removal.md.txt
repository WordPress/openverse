# 2024-03-28 Implementation Plan: Ingestion Server Removal

**Author**: @stacimc

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @sarayourfriend
- [x] @AetherUnbound

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/3925)
- [Project Proposal](/projects/proposals/ingestion_server_removal/20240319-project_proposal.md)

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

The critical data refresh process is orchestrated by Airflow via the
`<media_type>_data_refresh` DAGs, but the bulk of the work is merely triggered
by Airflow on a remote ingestion server. Due to the reasons laid out in the
Project Proposal, we will be moving all operational pieces of the data refresh
into Airflow itself, and removing the ingestion server entirely.

The work which must be moved into Airflow can be split into these abstract
steps, which will be discussed separately in this IP:

- **Copy Data**: An
  [FDW extension](https://www.postgresql.org/docs/current/postgres-fdw.html) is
  used to connect the API database to the upstream (catalog) database. The
  entire contents of the upstream media table are copied into a new temp table
  in the API database. This temp table will later replace the main media table
  in the API.
- **Clean Data**: Data clean up which includes cleaning URLs. This step will
  become unnecessary when the
  [Catalog Data Cleaning project](https://github.com/WordPress/openverse/issues/430)
  is completed, which moves all data cleaning steps upstream into the initial
  provider ingestion process.
- **Filter Data**: Separate from the clean up step (but currently included as
  part of it). Filter out denylisted tags and machine-generated tags which are
  below our current confidence threshold. This will _not_ be a part of the data
  cleaning project and must be carried forward.
- **Create Index**: Create a new Elasticsearch index, matching the configuration
  of the existing media index.
- **Distributed Reindex**: Convert each record from the new temp table to the
  format required by an Elasticsearch document, and then reindex them into the
  newly created index. Because this step is by far the most time consuming, the
  reindex is distributed across multiple **indexer workers**. In the current
  implementation, the indexer workers are themselves running on EC2 instances (6
  in production, 2 in staging). Each indexer worker serves a small API which can
  be used to trigger a reindexing task for an equal portion of the work. The
  workers are started by the ingestion-server when needed, and automatically
  spun down when complete.
- **Create and Populate Filtered Index**: Create a new Elasticsearch index
  matching the configuration of the existing _filtered_ index, and then reindex
  documents into it from the new media index, applying appropriate filtering for
  sensitive terms.
- **Reapply Constraints**: Recreate indices and constraints from the original
  API table on the new temp table.
- **Promote Table**: Drop the old media table in the API and rename the temp
  table and its indices, which has the effect of promoting them/replacing the
  old table.
- **Promote Index**: Promote the new Elasticsearch index by unlinking the given
  alias from the existing index and moving it to the new one. (Used for both the
  main and filtered indices.)
- **Delete Index**: Delete the old Elasticsearch index. (Used for both the main
  and filtered indices.)

In addition to the data refresh DAGs, some combination of these steps on the
ingestion-server are also used by:

- `recreate_full_staging_index` DAG
- `create_filtered_<media>_index` DAGs
- Our `load_sample_data` scripts, which use the ingestion server to load sample
  data from the catalog into the API and Elasticsearch

This IP includes details for moving all steps into Airflow. The bulk of the plan
deals with the `Distributed Reindex` step, which is the only step that is not
straightforward to move.

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

When this work is completed we will be able to:

- Manage data refreshes entirely in Airflow, without the use of the ingestion
  server
- Completely remove the staging and production ingestion servers, as well as all
  related code in the monorepo and infrastructure repos
- Remove the `recreate_full_staging_index` DAG

## Approach to the Distributed Reindex

The majority of the data refresh process can be implemented in Airflow with only
slight refactoring, using our existing
[Postgres hooks/operators](https://github.com/WordPress/openverse/blob/05ff48d05f2163104151c5589cf352a156bc6a97/catalog/dags/common/sql.py)
and reusable
[Elasticsearch tasks](https://github.com/WordPress/openverse/blob/05ff48d05f2163104151c5589cf352a156bc6a97/catalog/dags/common/elasticsearch.py).
The exception is the _distributed reindex_.

The simplest approach would be to remove the indexer workers entirely in favor
of doing the reindexing in parallelized dynamic tasks in Airflow. However,
currently the indexer workers and catalog EC2 instances are the same size
(m5.xlarge), and each of the six production workers were observed to use up to
~25% CPU and ~52% memory utilization during reindexing. The expense of
permanently increasing resources on the catalog instance to support reindexing
(which may happen concurrently with popularity refreshes, ingestion, and all
other processes that occur on the catalog) would significantly exceed the cost
of maintaining remote workers that can be run only when needed.

Two other options were evaluated for this IP:

- Keep the EC2 instances as they are now, but connect to them directly from
  Airflow. Rather than managing the 8 total EC2 instances directly, we will
  instead set up an EC2 launch template for each environment. The data refresh
  DAGs will spin up instances using the appropriate launch template and existing
  EC2 operators. (More details follow later in this document.)
- Remove the EC2 instances entirely in favor of a new ECS task definition using
  the `indexer-worker` image, which would remove all API code and contain only
  the reindexing script. Airflow would spin up the appropriate number of ECS
  tasks when needed.

### Comparison of EC2 and ECS

The following areas of comparison were considered when choosing between the two
approaches:

#### Cost

Maintaining the
[EC2 worker instances](https://calculator.aws/#/createCalculator/ec2-enhancement),
provided we continue to automatically stop the instances when not in use, would
be cheaper than using [ECS](https://calculator.aws/#/createCalculator/Fargate),
given equivalent resources.

Since our existing indexer workers do not use all of the resources available, we
can also consider reducing resources for the workers. For EC2, we are already
using the cheapest possible offering that will comfortably accommodate our
memory consumption. Since ECS is more flexible and allows scaling vCPU and RAM
independently, it is possible that ECS could be cheaper than EC2 with careful
adjustment of resources[^1].

Notably both solutions are _signifcantly_ cheaper than the current
implementation, because the bulk of the cost comes from constantly running the
two m5.xlarge EC2 instances for the ingestion servers.

#### Ease of infrastructure development

EC2 is also likelier the easier solution to implement, because it requires so
few changes to the indexer-workers as they are currently configured. For ECS,
less total infrastructure scaffolding is required, but it is a greater departure
from the current setup.

#### Code maintainability

The ECS approach requires slightly less code, because it would allow us to
completely remove all of the server logic needed in the EC2 instances. The
Docker image need only contain the script for reindexing.

For the EC2 instances we would continue to serve a minimal API with the
following endpoints:

- `healthcheck`
- `reindexing_task` - Trigger the reindexing task for the given parameters
  (e.g., run the script)
- `task/{task_id}` - Get the status of the running task

That being said, the API needed for the indexer worker is simple and small. The
vast majority of the complexity in the data refresh is in the _ingestion
server's_ API, all of which would still be removed.

#### Supporting local testing & development

This is the most significant area in which EC2 is preferable to the ECS
approach. With the EC2 approach, assigning work to the workers requires starting
the worker instances and then triggering the reindexing task on each worker by
POSTing to its `reindexing_task` endpoint. Locally, we would simply POST to our
local Docker container rather than an EC2 instance. Minimal work is needed to
adapt the process to work in a local environment, and the DAG when run locally
is as close as possible to its production counterpart.

For the ECS approach, in production we must spin up ECS instances using
Airflow's
[EcsRunTaskOperator](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/operators/ecs.html#run-a-task-definition).
Simulating this in a local development environment without actually connecting
to AWS is less straightforward, and requires supporting a separate workflow for
local environments. For example we could have a `branch` operator that checks
the environment and proceeds to the EcsRunTaskOperator in production to spin up
ECS tasks, or a
[DockerOperator](https://airflow.apache.org/docs/apache-airflow-providers-docker/stable/_api/airflow/providers/docker/operators/docker/index.html)
in local development to spin up a worker as a local Docker container.

This is still relatively complex, however, because the worker Docker containers
must be launched from Airflow, which is itself dockerized. This requires either
using a Docker-in-Docker approach, which should typically be avoided, or
modifying the configuration to allow Airflow to launch sibling containers[^2].
Requirements differ across operating systems, yet this **must** be tested and
maintained across platforms because the data refresh is used as a critical step
in setting up our local development environment.

#### Support for progress tracking

With the EC2 approach it is trivial to calculate the `percentage_complete` for
the reindexing task, and report to Airflow via the task status endpoint.
Airflow's ECS Operators do not have out-of-the-box support for streaming the
Cloudwatch logs from the task while it is running, so we would have less insight
into the status of the task from Airflow.

#### Impact on Deployments

This is a great strength of both approaches, each of which would eliminate the
need for deployments when changes are made to the data refresh code (including
changes to the indexer workers).

Each time an ECS task is spun up on Fargate, it will pull the Docker image
configured in the task definition. By using the `latest` tag in this
configuration we can ensure that the latest indexer-worker image is pulled each
time, which means that any changes to the reindexing code will become live in
production as soon as the new docker image is published after merging on `main`.

The EC2 approach uses EC2 operators to achieve a similar result. Because we will
actually terminate (rather than stop) the instances when their work is complete
and create entirely _new_ instances for each data refresh, we can update the
launch template to use the latest Docker image each time an instance is created,
so that the latest code is pulled each time a data refresh starts.

### Conclusion

Both approaches allow us to eliminate the need for deployments in almost all
cases, except for when changes are made to the task definition and launch
template respectively.

The main advantage of the ECS approach is that it allows us to remove 100% of
the server management code. However, it is more difficult to implement, likely
more expensive, and requires a special secondary implementation for running
locally that may be prone to cross-platform issues. The EC2 approach on the
other hand is cheaper, quicker to implement, and gets us the vast majority of
what we want in terms of removing complexity. Consequently I argue here that the
EC2 approach is the one we should pursue.

## Step-by-step plan

<!--
List the ordered steps of the plan in the form of imperative-tone issue titles.

The goal of this section is to give a high-level view of the order of implementation any relationships like
blockages or other dependencies that exist between steps of the plan. Link each step to the step description
in the following section.

If special deployments are required between steps, explicitly note them here. Additionally, highlight key
milestones like when a feature flag could be made available in a particular environment.
-->

Because the data refresh process is critical, we will not remove the ingestion
server or the existing data refresh DAGs until the new process has been
performed successfully in staging and production. The new data refresh will be
developed as separate DAGs alongside the current ones.

1. Create a new data refresh factory to generate new data refresh DAGs for each
   media type for staging and production, with the
   `<environment>_<media>_data_refresh` DAG id. For simplicity of code review,
   these initial DAGs should only perform the `Copy Data`, `Filter Data`, and
   `Create Index` steps, which we will perform entirely in Airflow.
1. Create a new `catalog-indexer-worker` in the Catalog, and build the new
   indexer worker image locally.
1. Add the distributed reindexing step to the DAG (excludes infrastructure
   work).
1. Set up the necessary resources for the EC2 launch templates for staging and
   production in the catalog Terraform configuration.
1. Add all remaining steps to the data refresh DAGs:
   `Create and Populated Filtered Index`, `Reapply Constraints`,
   `Promote Table`, `Promote Index`, `Delete Index`.
1. Deploy the catalog and the new indexer-workers configuration.
1. Run the staging audio data refresh, followed by the staging image data
   refresh.
1. Once successful, run the production audio data refresh and image data
   refresh.
1. Update the `create_filtered_<media>_index` DAGs to remove use of the
   ingestion server.
1. Drop the `recreate_full_staging_index` DAG, which can be removed entirely in
   favor of the staging data refresh.
1. Update the `load_sample_data.sh` script to run the DAG instead of using the
   ingestion server.
1. Fully remove the ingestion server and related infrastructure.

There are few opportunities for multiple streams of work. Updating the
`create_filtered_<media>_index` DAGs can happen at any time.

## Step details

<!--
Describe all of the implementation steps listed in the "step-by-step plan" in detail.

For each step description, ensure the heading includes an obvious reference to the step as described in the
"step-by-step plan" section above.
-->

While this may look daunting, it should be noted that with very few exceptions
the work described below is refactoring of existing logic. Links to the source
files are included for convenience.

### Create the new data refresh DAG factory and move initial steps into Airflow

In this step, we'll create a new data refresh DAG factory to generate data
refresh DAGs for each existing media_type and environment. Currently these four
will be generated:

- staging_audio_data_refresh
- staging_image_data_refresh
- production_audio_data_refresh
- production_image_data_refresh

Because the `environment` is added as a prefix, there will be no collision with
the existing DAG ids. In this initial step, we we will add only a small portion
of the logic in order to make the PR easier to review. The first steps are
already implemented in the current data refresh and can simply be copied:

- Get the current record count from the target API table; this must be modified
  to take the `environment` as an argument
- Perform concurrency checks on the other data refreshes and conflicting DAGs;
  this must be modified to include the now larger list of data refresh DAG ids
- Get the name of the Elasticsearch index currently mapped to the `target_alias`
- Generate the new index suffix

We will include new tasks to perform the initial few steps of the ingestion
server's work:

- `Copy Data`: this should be a TaskGroup that will have multiple tasks for
  creating the FDW from the upstream DB to the downstream DB, running the
  copy_data query, and so on. It should fully replace the implementation of
  [`refresh_api_table`](https://github.com/WordPress/openverse/blob/05ff48d05f2163104151c5589cf352a156bc6a97/ingestion_server/ingestion_server/ingest.py#L248)
  in the ingestion server. All steps in this section are SQL queries that can be
  implemented using the existing
  [PostgresHook and PGExecuteQueryOperator](https://github.com/WordPress/openverse/blob/05ff48d05f2163104151c5589cf352a156bc6a97/catalog/dags/common/sql.py).
- `Filter Data`: initially, this should be a single python task which exactly
  mirrors the behavior of the
  [`clean_image_data` function of `cleanup.py`](https://github.com/WordPress/openverse/blob/47fe5df0e9b8ad3dba06021f4cd4af9139977644/ingestion_server/ingestion_server/cleanup.py#L295)
  (only applying the tag-specific steps) on the ingestion server[^3]. The
  easiest way to do this would be to directly map the functionality of the
  ingestion server on this step within a single Airflow task. The steps for this
  task are as follows (see [Alternatives](#filtering-approach) for possible
  future directions):
  1. Get a batch of records from the database using `CLEANUP_BUFFER_SIZE`
  2. Divide batch up into `multiprocessing.cpu_count()` subbatches
  3. Split the filtering up into separate workers using multiprocessing
  4. On each process
     1. Create a new DB connection & cursor per worker
     2. Iterate through each record
        1. Remove tags below confidence level
        2. Remove tags that need to be filtered (denylisted, machine-generated
           filter list, provider, etc)
        3. Only surface the record if it needs to be changed
        4. Update each records one by one with a single `UPDATE`
     3. Commit cursor and close connection
  5. Repeat steps 1-4 until all batches are consumed
- `Create Index`: we can use our existing
  [Elasticsearch tasks](https://github.com/WordPress/openverse/blob/05ff48d05f2163104151c5589cf352a156bc6a97/catalog/dags/common/elasticsearch.py#L82)
  to create the new elasticsearch index with the index suffix generated in the
  previous task.

### Implement new catalog indexer worker

In this step we will create the new catalog-indexer-worker Docker image. This
step does not include adding the orchestration steps to the DAG, or the related
infrastructure work.

First we will create a new `indexer-worker` directory under
`catalog/dags/data_refresh`, which will contain the contents of the new indexer
worker. **This implementation already exists in the ingestion server. The
relevant pieces can be pulled out and refactored slightly to fit the new, much
smaller image.** Broadly, this is the mapping of existing files to new files
needed:

- `api.py` will defined the API for the worker, and is refactored from the
  existing
  [`indexer_worker.py`](https://github.com/WordPress/openverse/blob/05ff48d05f2163104151c5589cf352a156bc6a97/ingestion_server/ingestion_server/indexer_worker.py).
  It must be refactored to add task state and a `task_status` endpoint, which
  takes a `task_id` and returns the status and progress of the given task.
- `indexer.py` will contain the logic for the actual indexing task. It will be
  refactored from the existing
  [`indexer.py`](https://github.com/WordPress/openverse/blob/05ff48d05f2163104151c5589cf352a156bc6a97/ingestion_server/ingestion_server/indexer.py);
  specifically all we need is the
  [`replicate`](https://github.com/WordPress/openverse/blob/05ff48d05f2163104151c5589cf352a156bc6a97/ingestion_server/ingestion_server/indexer.py#L157)
  function.
- `elasticsearch_models.py`, pulled from the file of the
  [same name](https://github.com/WordPress/openverse/blob/05ff48d05f2163104151c5589cf352a156bc6a97/ingestion_server/ingestion_server/elasticsearch_models.py)
  in the ingestion server. Defines a mapping from a database record to an
  Elasticsearch document.
- Utility files for helper functions for connecting to Elasticsearch and
  Postgres (e.g.
  [`es_helpers.py`](https://github.com/WordPress/openverse/blob/main/ingestion_server/ingestion_server/es_helpers.py))

The
[`Dockerfile`](https://github.com/WordPress/openverse/blob/main/ingestion_server/Dockerfile)
can be copied from the existing ingestion server. It should be updated to
reference the new file structure, and to expose only a single port, which should
be distinguished from the ports currently in use by the ingestion server (8001
and 8002). Other necessary files, including `env.docker`, `.dockerignore`,
`Pipfile`, and `gunicorn.conf.py` can all be copied in from the existing
ingestion server as well.

Finally we will update the monorepo's root
[`docker-compose.yml`](https://github.com/WordPress/openverse/blob/05ff48d05f2163104151c5589cf352a156bc6a97/docker-compose.yml)
to add a new `catalog-indexer-worker` service. Its build context should point to
the nested `data_refresh/indexer_worker` directory, and it should map the
exposed port to enable the API to be reached by the catalog.

When this work is complete, it should be possible to run `just catalog/shell`
and curl the new indexer worker. The existing ingestion-server and
indexer-worker services are unaffected (it is still possible to run legacy data
refreshes locally and in production).

### Implement distributed reindexing locally

In this step we will add tasks to the data refresh DAGs to orchestrate the
distributed reindex. At the end of this step, it will be possible to run a
distributed reindex _locally_. The following code can all be refactored from
[`distributed_reindex_scheduler.py`](https://github.com/WordPress/openverse/blob/main/ingestion_server/ingestion_server/distributed_reindex_scheduler.py).

- Use dynamic task mapping to distribute reindexing across the indexer workers
  by first calculating `start` and `end` indices that will split the records in
  the media table into even portions, depending on the number of workers
  available in the given target environment. Then, for each worker:
  - Use the
    ['EC2CreateInstanceOperator'](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/operators/ec2/index.html#airflow.providers.amazon.aws.operators.ec2.EC2CreateInstanceOperator)
    to create a new EC2 instance. The task returns the id of the created
    instance.
    - Under the covers this operator is using boto3
      [`run_instances`](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/run_instances.html).
      We can pass the name or id for the appropriate launch template in the
      `config` parameter. The launch template names will be hard-coded
      constants.
    - Note: it's possible to use this operator to launch all the workers at once
      by setting the `min_count` and `max_count` parameters. We will instead be
      using dynamic task mapping to create a separate task for creating each
      indexer worker individually: this is so that if a single worker fails
      later in the process, we can retry that worker in isolation.
  - Use the EC2Hook
    [`describe_instances`](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/hooks/ec2/index.html#airflow.providers.amazon.aws.hooks.ec2.EC2Hook.describe_instances)
    to get the private IP address of the worker instance from its instance id
  - Use a Sensor to ping the worker's healthcheck endpoint, ensuring that the
    instance is up and running and the API is accessible.
  - POST to the worker's `reindexing_task` endpoint with the `start_index` and
    `end_index` it should handle, triggering the reindexing.
  - Use a Sensor to ping the worker's `task/{task_id}` endpoint until the task
    is complete, logging the progress as it goes
  - Finally, use the
    [`EC2TerminateInstanceOperator`](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/operators/ec2/index.html#airflow.providers.amazon.aws.operators.ec2.EC2TerminateInstanceOperator)
    to terminate the instance. Make sure to use the
    [`NONE_SKIPPED` TriggerRule](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html#trigger-rules)
    to ensure that the instances are terminated, even if there are upstream
    failures. (Skips in local env.)

### Create the Terraform and Ansible resources needed to deploy the new indexer workers

In this step we will add the launch templates needed to actually create the EC2
instances.

Some important notes:

- Currently, the staging and production workers are split into separate
  environments (i.e., a staging deploy is used to deploy the 2 staging workers
  separately from the 6 production workers). It is more accurate to view all 8
  workers as production instances (i.e., part of the production catalog
  deployment), which merely _operate_ on different environments. As such all 8
  should be part of the production deployment, but there will be two separate
  launch templates which are tagged to indicate their respective environment.
- The playbooks must be updated to check if any of the four _new_ data refresh
  DAGs are running before deploying, as well.
- The `user_data` script should be updated to pull the Docker image with the
  `latest` tag.

### Add remaining steps to the Data Refresh DAGs

The final steps can now be added to the DAGs:

- `Create and Populated Filtered Index`: this should be implemented as a
  reusable TaskGroup. This work can already be implemented using our existing
  Elasticsearch tasks and replaces
  [this function](https://github.com/WordPress/openverse/blob/226aed0890a19ace1e0b54c1e784c86e9f26b4cb/ingestion_server/ingestion_server/indexer.py#L437).
- `Reapply Constraints` and `Promote Table`: these SQL queries can be performed
  with the PostgresHook, and replaces
  [this function](https://github.com/WordPress/openverse/blob/226aed0890a19ace1e0b54c1e784c86e9f26b4cb/ingestion_server/ingestion_server/ingest.py#L340).
- `Promote Index` and `Delete Index`: these can be implemented using our
  existing Elasticsearch tasks, and replaces
  [these](https://github.com/WordPress/openverse/blob/226aed0890a19ace1e0b54c1e784c86e9f26b4cb/ingestion_server/ingestion_server/indexer.py#L311)
  [functions](https://github.com/WordPress/openverse/blob/226aed0890a19ace1e0b54c1e784c86e9f26b4cb/ingestion_server/ingestion_server/indexer.py#L377).

### Deploy the catalog and indexer workers

In this step we'll actually deploy the new workers using the Ansible playbooks.
The existing ingestion server and indexer workers remain untouched, so the
legacy data refresh can continue to run.

### Run the data refreshes

The next step is to run the `staging_<x>` data refreshes, which act on the
staging API DB and Elasticsearch cluster and are therefore lower risk. This will
be the first test of the new process. Once successful, we can run the
`production_<x>` refreshes.

### Update `create_filtered_<media>_index` DAGs

These DAGs currently use the ingestion server to perform the
`create_filtered_index` steps in isolation. We can update these to use the
reusable TaskGroup implemented in an earlier step.

### Remove the `recreate_full_staging_index` DAG

This DAG performs the second half of a data refresh (the distributed reindex and
promotion) in staging. Once the data refresh has been moved to Airflow, we can
add a
[DAG param](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/params.html)
to the data refresh that allows skipping the initial `Copy Data` steps. This DAG
will no longer be necessary and can then be deleted.

### Update the load_sample_data scripts

Our `load_sample_data.sh` scripts currently use `just` commands to
[run parts of the data refresh](https://github.com/WordPress/openverse/blob/226aed0890a19ace1e0b54c1e784c86e9f26b4cb/load_sample_data.sh#L98)
on the local ingestion server, as part of setting up the local development
environment. We should update the scripts to instead use the Airflow CLI to
unpause the two data refresh DAGs and await their completion.

### Remove the ingestion server

Once the new data refresh has been run successfully in production, we can
finally remove all ingestion-server code from the monorepo and the
infrastructure repo, and completely remove the associated EC2 instances.

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

Infrastructure is a large part of this project. We will be adding 8 new EC2
instances but deprovisioning ten, as described above. There will be significant
cost benefits to removing the two EC2 instances which are constantly running.

### Tools & packages

<!-- Describe any tools or packages which this work might be dependent on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

No new tools or packages are required.

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

- [Deploying Airflow with Ansible](https://github.com/WordPress/openverse-infrastructure/pull/829),
  part of the
  [Move Airflow to openverse.org](https://github.com/WordPress/openverse-infrastructure/milestone/6)
  Project.
- [Catalog Data Cleaning project](https://github.com/WordPress/openverse/issues/430),
  which removes the Clean Data steps from the data refresh
- [Switch Python Package Management Away from Pipenv](https://github.com/WordPress/openverse/issues/286)

## Alternatives

<!-- Describe any alternatives considered and why they were not chosen or recommended. -->

### ECS approach

The alternative options of using an ECS approach or performing the reindex
entirely in Airflow are discussed at length in the
[Approach to the Distributed Reindex](#approach-to-the-distributed-reindex)
section.

It is also possible to use EC2 instances but manage them directly in Airflow
using EC2 operators to start and stop the instances as needed. However, more
infrastructure work is required in this approach, and we would require
deployments whenever there are code changes in the indexer workers.

### Filtering approach

There are a number of ways to accomplish the data filtering, including several
ways to improve the approach mentioned.

The Airflow scheduler container has access to 4 cores, which is the same as the
ingestion server where this step was originally running. At present, it takes
about 8 hours for all cleanup steps, but that includes the URL cleaning which is
certainly more time intensive than the tag filtering since it makes outbound
requests. Running the tag filtering on Airflow should not impact any of the
other running tasks or saturate the instance.

There are a few ways this process could be improved, but none of them are
required _at this moment_. We can follow up after this project is complete to
assess what further optimizations might be necessary at this step. Some
potential suggestions for that time:

- Instead of single `UPDATE` queries for each affected records, we could insert
  records from each subbatch to a temporary table. Then the base table could be
  updated with an `UPDATE ... FROM` in bulk. Since the indices haven't been
  applied to the base table yet, this should be fairly performant.
- Instead of using multiprocessing, we could pre-define the batches and run the
  filtering chunks on a set of mapped tasks. The multiprocessing has the benefit
  of iterating over a cursor on the database rather than having to manage the
  record ranges explicitly, but this would allow further parallelization and
  task management.
- The indexer workers themselves could be expanded to run on larger chunks of
  the database for this filtering. This would likely require the most work as it
  would involve expanding the indexer workers' API to handle this additional
  task.

### ASG approach

An earlier draft of this implementation plan used an AutoScaling Group for each
environment. Airflow would use `set_desired_capacity` to set the ASG's capacity,
and the ASG itself would then spin up (and down) EC2 instances. A disadvantage
of this approach was that it is impossible to retry a single indexer worker.

## Blockers

<!-- What hard blockers exist that prevent further work on this project? -->

Development can start immediately, but the infrastructure components of this
project are blocked by completion of the effort to move Airflow to
openverse.org, specifically
[this issue](https://github.com/WordPress/openverse-infrastructure/issues/776)
to run a (legacy) data refresh on the new instance.

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

We will not remove the ingestion server or the existing data refresh DAGs until
the new DAGs have been run successfully against both staging and production. We
can rollback at any time by simply removing the new instances and DAGs.

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

There is minimal risk, as we will be able to test against production data in
staging before running against production. However the data refresh does
completely replace the production media tables and Elasticsearch indices, so
there is always inherent risk that production data could be lost or malformed if
something goes wrong. We will ensure production backups are available and
monitor the first production data refreshes closely.

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->

- [Search relevancy sandbox](https://github.com/WordPress/openverse/issues/392)

[^1]:
    See
    [comment](https://github.com/WordPress/openverse/pull/4026#pullrequestreview-1978477921)
    for specific cost assessment, courtesy of @sarayourfriend

[^2]:
    https://towardsdatascience.com/using-apache-airflow-dockeroperator-with-docker-compose-57d0217c8219

[^3]:
    See #4456 for further context on this. The filtering is a _necessary_ step
    of the data refresh we need to carry forward even after removing the other
    cleanup steps.
