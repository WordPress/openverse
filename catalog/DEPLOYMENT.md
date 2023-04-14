# Catalog Deployments

The Openverse Catalog consists of two core components: a **Postgres** instance
and an **Airflow** instance. This document describes the environments &
deployment procedures for both components.

# Airflow

> **URL**: https://airflow.openverse.engineering

Airflow has two different deployment mechanisms: **service deployments** and
**DAG deployments**. Service deployments occur when the Airflow service itself
or any dependencies needs to be updated. DAG deployments occur when DAG
definitions or operational code has changed.

## Service deployments

The Catalog's Airflow instance is hosted via AWS's Elastic Compute Cloud (EC2)
service. The EC2 instance is managed by Terraform. If a change is made to the
service initialization bash script, Terraform will recognize this change and can
deploy a new EC2 instance with the updated configuration. This change does not
occur automatically and will need to be manually initiated.

Currently the webserver, scheduler, and worker(s) are all run within a single
docker container on the EC2 instance as defined by
[the Airflow `Dockerfile` and related files](./docker/airflow). The
[`docker-compose.yml`](docker-compose.yml) is used to spin up Airflow in
production.

**Note**: Service deployments are only necessary in the following conditions:

- The Docker image has been modified
- An environment variable needs to be added/removed/changed
- A change to the infrastructure has been made (e.g. networking/routing changes)

For DAG updates and code-only changes, see the
[DAG deployments section](#dag-deployments).

### Deployment workflow

The "🔒" icon below notes that the action must be performed by a core maintainer
with infrastructure access.

1. [Cut a new release on GitHub](https://github.com/WordPress/openverse-catalog/releases).
2. After the release GitHub action has run,
   [check that the new Docker tag corresponding to the release exists on ghcr.io](https://github.com/wordpress/openverse-catalog/pkgs/container/openverse-catalog).
3. Ensure that there are
   [no actively running DAGs](https://airflow.openverse.engineering/dagrun/list/?_flt_3_state=running).
4. 🔒 Update the catalog version in the infrastructure repo by running
   `just bump prod catalog-airflow`
5. 🔒 Initiate the deployment via `just plan prod catalog-airflow` (and
   subsequently `just apply prod catalog-airflow` if the plan looks correct).

## DAG deployments

Due to the
[nature of Airflow](https://airflow.apache.org/docs/apache-airflow/stable/dag-serialization.html),
changes made to DAG definitions or operational code (e.g. any files that are
used by the DAG) will be immediately picked up on the next task run for a DAG.
This means that we can update the python code in-place and the next DAG run or
task in a currently running DAG will use the updated code. In these cases, a new
EC2 instance _does not_ need to be deployed.

The [`dag-sync.sh`](../dag-sync.sh) script is used in production to regularly
update the repository (and thus the DAG files) on the running EC2 instance.

### Deployment workflow

Since this process happens automatically, the only precursor to a DAG deployment
is merging the relevant PR into `main`.

_**Note**: New DAGs are not automatically enabled and will need to be turned on
once deployed._

# Postgres

The Catalog is also backed by a Postgres instance, which serves as the primary
data warehouse for all ingested media data.

This instance is hosted on AWS using [RDS](https://aws.amazon.com/rds/). The
instance can be accessed using [`pgcli`](https://www.pgcli.com/) or a similar
client with the jumphost defined in the infrastructure repository. For more
information on this process see the
[documentation on connecting to the jumphost](https://github.com/WordPress/openverse-infrastructure/blob/main/docs/CONNECTING-TO-JUMPHOST.md)
(note that you will need additional access to view this document, please reach
out to the maintainers if you're interested).

## Migrations

Any migrations to the Catalog database must either be performed by hand or as
part of a DAG's normal operation (see:
[iNaturalist](dags/providers/provider_api_scripts/inaturalist.py)).
