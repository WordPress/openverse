# 2023-04-06 Implementation Plan: Update Staging Database

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @stacimc
- [x] @krysal

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/392)
- [Project Proposal](https://docs.openverse.org/projects/proposals/search_relevancy_sandbox/20230331-project_proposal_search_relevancy_sandbox.html)

## Overview

<!-- A brief one or two sentence overview of the implementation being described. -->

This document describes how we will implement a mechanism for updating the
staging database with the latest data from the production database.

## Outlined Steps

<!-- Describe the implementation step necessary for completion. -->

There are two primary products of this plan. The first will be a DAG (scheduled
for `@monthly`) which will recreate the staging database from the most recent
snapshot of the production API database. The second will be modifications to the
Django Admin UI notifying maintainers of the next scheduled staging database
update.

### DAG

This will be accomplished by:

1. Use a new `SKIP_STAGING_DATABASE_RESTORE`
   [Airflow Variable](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/variables.html)
   to control whether the DAG should run or not. This will allow us to skip the
   DAG in the case where we have made diverging chances to the staging database
   for testing a new feature that we do not want to be overwritten. If this
   Variable is set to `True`, the DAG should issue a Slack message notifying the
   maintainers of the skipped run and raise an `AirflowSkipException`.
2. Determine the most recent automated **production** snapshot using boto3's
   [`describe_db_snapshots`](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds/client/describe_db_snapshots.html)
   function (an Airflow operator does not exist for this operation). This step
   should also check the `Status` value of the response for the most recent
   snapshot to ensure that it is `available`.
3. In the case where the snapshot is not yet available, wait for the status of
   the most recent snapshot using the
   [`RdsSnapshotExistenceSensor`](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/sensors/rds/index.html#airflow.providers.amazon.aws.sensors.rds.RdsSnapshotExistenceSensor).
4. In parallel, gather the attributes of the **staging** database using boto3's
   [`describe_db_instances`](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds/client/describe_db_instances.html)
   function (an Airflow operator does not exist for this operation). Namely, the
   following attributes should be gathered and set to ensure they match:
   - Availability should be a single DB instance (not
     [multi-AZ](https://docs.aws.amazon.com/fsx/latest/WindowsGuide/high-availability-multiAZ.html))
   - It should be attached to our default Virtual Private Cloud (VPC)
   - It should not be publicly accessible
   - It will need access to the following VPC security groups: `default`,
     `openverse-vpc-db-access`, `staging-dev-rds-sg`
   - It should match the staging database's instance size (currently
     `m5.xlarge`)
   - It should have 3000 GB of allocated gp2 storage
   - It should use password authentication (this may not need to be changed from
     the default, as the snapshot should contain the same connection
     information)
5. Create a new database from this snapshot using boto3's
   [`restore_db_instance_from_db_snapshot`](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds/client/restore_db_instance_from_db_snapshot.html)
   function (an operator does not exist for this operation). This database will
   be named in a way that does not conflict with the existing staging database
   name, e.g. `dev-next-openverse-db`. The database configuration information
   from the previous step will be used to ensure the new database matches the
   old database's configuration exactly.
6. Wait for the new database to be ready using the
   [`RdsDbSensor`](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/sensors/rds/index.html#airflow.providers.amazon.aws.sensors.rds.RdsDbSensor)
   ([example](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/operators/rds.html#howto-sensor-rdsdbsensor)).
7. Rename the old staging database to `dev-old-openverse-db` using boto3's
   [`modify_db_instance`](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds/client/modify_db_instance.html)
   function (an operator does not exist for this operation). We must set the
   `ApplyImmediately` option here to `True` to ensure this operation happens
   immediately rather than waiting for the next maintenance window.
8. Wait for the old database rename to be complete with the `RdsDbSensor` (we
   may need retries on this step, since the database may not be initially
   available/named when the sensor first starts). _**Note**: this will cause a
   temporary outage of the staging API, see
   [the alternatives section](#alternatives) for why this is the case._ A Slack
   notification should be sent out at the start of this step to alert the team
   of the outage, and again once the outage is resolved.
9. Rename the new database to `dev-openverse-db` using `modify_db_instance`.
   (Noting that `ApplyImmediately` should be set to `True` here as well.)
10. Wait for the new database rename to be complete with the `RdsDbSensor` (we
    may need retries on this step, since the database may not be initially
    available/named when the sensor first starts).
11. If the previous steps fail, rename `dev-old-openverse-db` back to
    `dev-openverse-db`. Otherwise, `dev-old-openverse-db` can be deleted using
    the
    [`RdsDeleteDbInstanceOperator`](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/operators/rds/index.html#airflow.providers.amazon.aws.operators.rds.RdsDeleteDbInstanceOperator).
    We should use the following configuration options:
    - `wait_for_completion` should be left as `True` here so this stop will hang
      until the database removal is complete.
    - `SkipFinalSnapshot` should be set to `True` to avoid creating a final
      snapshot of the database before deletion.
12. Once the database rename is complete, the following actions will also need
    to occur (they can occur simultaneously in the DAG):
    1. The staging API must be deployed to apply any necessary migrations to the
       new copy the database. In order to do this we must augment the existing
       [GitHub API class](https://github.com/WordPress/openverse/blob/aedc9c16ce5ed11709e2b6f0b42bad77ea1eb19b/catalog/dags/common/github.py#L4)
       with additional functions for **getting the latest GHCR image tag** and
       **triggering the deployment workflow**. Once those functions exist, the
       steps for this piece would be:
       1. Get the latest image tag for the
          [`openverse-api` package](https://github.com/WordPress/openverse/pkgs/container/openverse-api).
       2. Trigger the deployment workflow
          [in a similar manner to the existing CI/CD workflow](https://github.com/WordPress/openverse/blob/1f7b8e670a0f7812494375570d076a7c33142062/.github/workflows/ci_cd.yml#L833-L846)
          using the tag from the previous step and the `openverse-bot` actor.
    2. Update the Elasticsearch indices corresponding to each media type. This
       can be done by using the
       [`UPDATE_INDEX` action](https://github.com/WordPress/openverse/blob/7427bbd4a8178d05a27e6fef07d70905ec7ef16b/ingestion_server/ingestion_server/indexer.py#L314)
       on the ingestion server. The steps for this piece would be:
       1. Get the date for the last successful run of the update DAG (see the
          [`_month_check` function](https://github.com/WordPress/openverse/blob/aedc9c16ce5ed11709e2b6f0b42bad77ea1eb19b/catalog/dags/data_refresh/dag_factory.py#L85)
          from the data refresh DAG for a similar example).
       2. For each media type:
          1. Get the current index (see the
             [`get_current_index` task](https://github.com/WordPress/openverse/blob/aedc9c16ce5ed11709e2b6f0b42bad77ea1eb19b/catalog/dags/data_refresh/data_refresh_task_factory.py#L167-L175)
             on the data refresh DAG)
          2. Initiate the
             [`UPDATE_INDEX` action](https://github.com/WordPress/openverse/blob/7427bbd4a8178d05a27e6fef07d70905ec7ef16b/ingestion_server/ingestion_server/api.py#L107-L113)
             using the date and index suffix retrieved above
          3. Wait for the index update to complete
    3. Truncate the OAuth tables to prevent production API applications from
       working in staging. Each of these truncate operations can be run
       simultaneously using
       `TRUNCATE TABLE <table_name> RESTART IDENTITY CASCADE;` in a
       [`PGExecuteQueryOperator`](https://github.com/WordPress/openverse/blob/aedc9c16ce5ed11709e2b6f0b42bad77ea1eb19b/catalog/dags/common/sql.py#L137).
       The tables that need to be truncated are:
       - `api_throttledapplication`
       - `api_oauth2registration`
       - `api_oauth2verification`
       - `oauth2_provider_accesstoken`
       - `oauth2_provider_grant`
       - `oauth2_provider_idtoken`
       - `oauth2_provider_refreshtoken`
13. Report the success or failure of the DAG run to Slack.

### Django Admin UI changes

The above section describes the process for performing the staging update. A
side-effect of this method of updating is that the data in staging will be
destroyed in favor of the data from the production database. Maintainers can use
the `SKIP_STAGING_DATABASE_RESTORE` Airflow Variable described above to prevent
the deletion of the staging database. We will also add a notice to the top of
Django Admin UI denoting when the next scheduled database recreation will occur.
This can be done by
[overriding the base Django Admin template](https://docs.djangoproject.com/en/4.2/howto/overriding-templates/#extending-an-overridden-template)
and adding a notice to the top of the page. Since the DAG is intended to be run
`@monthly`, a countdown to the next run can be calculated and displayed for
maintainers. We will also want to provide instructions or a link to instructions
for how to disable the staging database recreation using the aforementioned
Airflow Variable.

## Dependencies

### Tools & packages

<!-- Describe any tools or packages which this work might be dependent on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

We already have the `amazon` provider (and thus `boto3`)
[installed on Airflow](https://github.com/WordPress/openverse-catalog/blob/46281fc9fda60ab2df0df6d85043565dfc51b12d/requirements_prod.txt#L5).
We should not need any additional dependencies.

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

This does not depend on any existing projects.

### Infrastructure

<!-- Note any infrastructure this plan is dependent on. -->

This project directly affects our infrastructure, but should not require any
additional dependencies or changes. After this DAG is run, the infrastructure
should mirror what existed before (albeit with an updated staging database).

## Alternatives

### Database cut-over

The plan described above will incur a short (<10 minute) outage of the staging
API. This is because the database name is changed in the middle of the process.
If we want to avoid this outage, we could instead create a new database with a
different name, and then switch the staging API and any other dependent services
(such as the ingestion server) over to the new database. This would eliminate
the outage, but would instead require that we deploy all staging services which
depend on the database as part of the DAG workflow. We do not yet have an
automated way for Airflow to trigger a deployment itself, so this would require
additional work to get Airflow integrated with GitHub Actions. Furthermore,
changes to the services environment variables would require changes to the
infrastructure repository and an application of the updated terraform
configuration.

With this in mind, it seems much easier to handle the outage for staging rather
than try and avoid it.

### Per-table update policy

We could also update the database in a more granular fashion, updating each
table individually. This would allow us to avoid the outage, would enable
further granularity with respect to which tables we update when, and could be
used to reduce the delay between when the production database is updated and
when the staging database receives the same data. This was discussed heavily
[in the implementation plan PR](https://github.com/WordPress/openverse/pull/1154),
and several potential mechanisms for this method of updating were discussed,
namely:

1. Foreign Data Wrapper to point staging media tables to production
2. Postgres' "logical replication" feature to keep production and staging media
   tables in sync
3. Foreign Data Wrapper to insert all records from production media tables into
   staging

We opted to defer the persuit of this alternate approach for the time being for
the following reasons:

- The FDW/replication approach(es) described may have numerous pitfalls,
  unknowns, or drawbacks which the maintainers are not privy to due to
  unfamiliarity with the functionality.
- The proposed alternative solution is essentially describes an ETL framework
  for production -> staging replication. While such a system could be
  significantly more flexible, it would by necessity also be more complex, and
  would warrant its own project process to flesh out.
- At the time of writing this is the first of
  [three implementation plans this project requires](https://docs.openverse.org/projects/proposals/search_relevancy_sandbox/20230331-project_proposal_search_relevancy_sandbox.html#required-implementation-plans),
  the other two being "Rapid iteration on ingestion server index configuration"
  and "Staging Elasticsearch reindex DAGs for both potential index types". Any
  elongations to the project timeline at this step could also affect the
  timeline for drafting and implementing those plans as well.
- The DAG described here does not present any **permanent, lasting, and
  irreversible** changes; it can be disabled and replaced at any time in favor
  of a more thorough update approach down the line.

It is intended to be explored further in
[another project in the future](https://github.com/WordPress/openverse/issues/1874).

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

This DAG will need to have clear instructions for how to run it for those
unfamiliar with Airflow.

## Parallelizable streams

<!-- What, if any, work within this plan can be parallelized? -->

Based on the above steps, the following work can be parallelized:

1. Alterations to the
   [GitHub API class](https://github.com/WordPress/openverse/blob/aedc9c16ce5ed11709e2b6f0b42bad77ea1eb19b/catalog/dags/common/github.py#L4)
   to include new methods for pulling the latest GHCR image tag and for
   triggering a workflow.
2. The addition of the notification banner to the Django Admin UI.

After the above work is complete, the primary DAG can be written and tested.

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

A rollback for this would work would only require deleting the created DAG.

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

Because this DAG modifies our existing infrastructure directly, there is risk
that we may adversely affect production databases with this DAG. Therefore, care
should be taken in asserting that _only_ staging is affected. One way to
accomplish this would be to provide a wrapper around all the functions we will
need for interacting with `boto3` that checks that `prod` is not in any of the
references made to database assets (save for the initial snapshot acquisition
step). If `prod` is found in any of the references, the DAG should fail.

Additionally, I have enabled deletion protection on the `prod-openverse-db`.
This does not affect rename operations and thus does not fully mitigate a
production outage if the database was renamed, but it does prevent a full
deletion of the database.

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->

- [Airflow documentation](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/operators/rds.html)
- Internal discussions regarding restoring from snapshots in the past (these
  links are not publicly available but may serve as useful references for
  maintainers):
  - [Catalog RDS instance expansion plan](https://teamopenverse.wordpress.com/2023/03/27/catalog-rds-instance-storage-expansion-plan/)
  - [Discussion around snapshot restores as part of the API ECS migration](https://teamopenverse.wordpress.com/2022/07/26/api-ecs-deployment/#comment-3404)
  - [Discussion around snapshot restores as part of an API outage recovery after-incident review](https://teamopenverse.wordpress.com/2022/05/18/openverse-api-outage-2022-05-18-debrief/#comment-1066)
