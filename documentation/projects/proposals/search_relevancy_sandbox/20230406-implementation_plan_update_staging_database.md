# Implementation Plan: Update Staging Database

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [ ] @stacimc
- [ ] @krysal

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/392)
- [Project Proposal]() _TBD_

## Overview

<!-- A brief one or two sentence overview of the implementation being described. -->

This document describes how we will implement a mechanism for updating the
staging database with the latest data from the production database.

## Outlined Steps

<!-- Describe the implementation step necessary for completion. -->

The final product of this plan will be a DAG (scheduled for `@monthly`) which
will recreate the staging database from the most recent snapshot of the
production API database. This will be accomplished by:

1. Determine the most recent automated **production** snapshot using boto3's
   [`describe_db_snapshots`](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds/client/describe_db_snapshots.html)
   function (an Airflow operator does not exist for this operation). This step
   should also check the `Status` value of the response for the most recent
   snapshot to ensure that it is `available`.
2. In the case where the snapshot is not yet available, wait for the status of
   the most recent snapshot using the
   [`RdsSnapshotExistenceSensor`](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/sensors/rds/index.html#airflow.providers.amazon.aws.sensors.rds.RdsSnapshotExistenceSensor).
3. Create a new database from this snapshot using boto3's
   [`restore_db_instance_from_db_snapshot`](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds/client/restore_db_instance_from_db_snapshot.html)
   function (an operator does not exist for this operation). This database will
   be named in a way that does not conflict with the existing dev database name,
   e.g. `dev-next-openverse-db`. Careful consideration will need to be made when
   drafting this step to ensure that the generated database matches the settings
   for the existing database exactly. Specifically, the following should be
   matched:
   - Availability should be a single DB instance (not multi-AZ)
   - It should be attached to our default VPC
   - It should not be publicly accessible
   - It will need access to the following VPC security groups: `default`,
     `openverse-vpc-db-access`, `staging-dev-rds-sg`
   - It should match the dev database's instance size (currently `m5.xlarge`)
   - It should have 3000 GB of allocated gp2 storage
   - It should use password authentication (this may not need to be changed from
     the default, as the snapshot should contain the same connection
     information)
4. Wait for the new database to be ready using the
   [`RdsDbSensor`](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/sensors/rds/index.html#airflow.providers.amazon.aws.sensors.rds.RdsDbSensor)
   ([example](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/operators/rds.html#howto-sensor-rdsdbsensor)).
5. Rename the old staging database to `dev-old-openverse-db` using boto3's
   [`modify_db_instance`](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds/client/modify_db_instance.html)
   function (an operator does not exist for this operation). We must set the
   `ApplyImmediately` option here to `True` to ensure this operation happens
   immediately rather than waiting for the next maintenance window.
6. Wait for the old database rename to be complete with the `RdsDbSensor` (we
   may need retries on this step, since the database may not be initially
   available/named when the sensor first starts). _**Note**: this will cause a
   temporary outage of the staging API, see
   [the alternatives section](#alternatives) for why this is the case._
7. Rename the new database to `dev-openverse-db` using `modify_db_instance`.
8. Wait for the new database rename to be complete with the `RdsDbSensor` (we
   may need retries on this step, since the database may not be initially
   available/named when the sensor first starts).
9. If the previous steps fail, rename `dev-old-openverse-db` back to
   `dev-openverse-db`. Otherwise, `dev-old-openverse-db` can be deleted using
   the
   [`RdsDeleteDbInstanceOperator`](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/operators/rds/index.html#airflow.providers.amazon.aws.operators.rds.RdsDeleteDbInstanceOperator)
   (the `wait_for_completion` should be left as `True` here so we don't need a
   follow-up sensor).
10. Report the success or failure of the DAG run to Slack.

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

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

This DAG will need to have clear instructions for how to run it for those
unfamiliar with Airflow.

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
