# Zero Downtime and Database Management

Openverse practices zero-downtime deployments. This puts a handful of
constraints on our database migration and data management practices. This
document describes how to ensure migrations can be deployed with zero downtime
and how to implement and manage long-running data migrations.

Zero-downtime deployments are important to ensure service reliability. Following
the practices that enable zero-downtime deployments also promotes best practices
like ensuring changes are incremental and more easily reversible.

## External resources

This document assumes a general understanding of relational databases, including
concepts like database tables, columns, constraints, and indexes. If this is not
something you are familiar with,
[the Wikipedia article on relation databases](https://en.wikipedia.org/wiki/Relational_database)
is a good starting point.

Django's
[database migration documentation](https://docs.djangoproject.com/en/4.1/topics/migrations/)
also contains helpful background knowledge, though this document takes a more
general approach than addressing only Django specific scenarios.

## Terms

- "Zero-downtime deployment": An application deployment that does not result in
  any period of time during which a service is inaccessible. For the purposes of
  Openverse, these require running two versions of the application at once that
  share the same underlying database infrastructure.
- "Schema": The structure of a database. The tables, columns, and their types.
- "Downtime deployment": An application deployment that does result in a period
  of time during which a service is inaccessible. The Openverse project goes to
  great lengths to avoid these. These are often caused when a new version of an
  application is incompatible with the underlying infrastructure of the
  previously deployed version.
- "Database migration": A change to the schema of a database. Common migrations
  include the addition or removal of tables and columns.
- "Data transformation": A change to the data held in a database that does not
  include (but can be related) to a database migration. Common examples include
  backfilling data to remove null values from a column or moving data between
  two related columns.
- "Data migration": A data transformation that is executed as part of a Django
  migration.
- "Long-running data transformation": A data transformation that lasts longer
  than a few seconds. Long-running data transformations are commonly caused by
  the modification of massive data, especially data in indexed columns.

## How zero-downtime deployments work

To understand the motivations of these best practices, it is important to
understand how zero-downtime deployments are implemented. Openverse uses the
[blue-green deployment strategy](https://en.wikipedia.org/wiki/Blue-green_deployment).
The blue-green strategy requires running the new version of the application and
the previous version at the same time during the duration of the deployment.
This allows us to replace the multiple, load-balanced instances of our
application one-by-one. As a result, we are able to verify the health of the
instances running the new version, before fully replacing our entire cluster of
application instances with the new version. At all times during a successful
deployment process, both versions of the application must be fully operable and
healthy and able to handle requests. During deployment, the load-balancer will
send requests to both the previous and new versions of the application during
the entire time of the deployment, which can be several minutes. This requires
both versions of the application to be strictly compatible with the underlying
database schema.

## What causes downtime during a deployment?

The most common cause of downtime during a deployment are database schema
incompatibilities between the previous and new version of the application. The
classic example of a schema incompatibility involves column name changes.
Imagine there is a column on a table of audio files called "length", but we
wanted to change the column name to specify the expected units, to make it
clearer for new contributors. If we simply change the name of the column to
"length_ms", then when the new version of the application deploys, it will apply
the migration to change the name. The new version will, of course, work just
fine, in this case. However, during deployments, the previous version of the
application will still be running for a period of time. Requests by the previous
version of the application to retrieve the "length" column with fail
catastrophically because the "length" column will no longer exist! It has been
renamed to "length_ms". If we prevented the new version of the application from
applying the migration, the same issue would arise, but for the new versions as
the "length_ms" column would not yet exist. This, in addition to column
data-type changes, is the most common reason why downtime would be required
during a deployment process that is otherwise capable of deploying without
downtime. When schema incompatibilities arise between new and the previous
version of an application, it is impossible to safely serve requests from both
using the same underlying database.

Other causes are variations on this same pattern: a shared dependency is neither
forward nor backwards compatible between two subsequent versions of the
application.

> **Note**: This issue of incompatibility only applies to _subsequent_ versions
> of an application because only subsequent versions are ever deployed
> simultaneously with the same underlying support infrastructure. So long as
> there is at least one version between them, application versions may and
> indeed sometimes do have fundamental incompatibilities with each other and
> could not be simultaneously deployed.

## How to achieve zero-downtime deployments

Sometimes you need to change the name of a column or introduce some other,
non-backwards compatible change to the database schema. Luckily, this is still
possible, even with zero-downtime deployments, though admittedly the process is
more tedious.

Continuing with the column name change case-study, the following approach must
be followed.

1. Create a new column with the desired name and data type. The new column must
   be nullable and should default to null. This step should happen with a new
   version of the application that continues to use the existing column.
1. If the column is written to by the application, deploy a new version that
   starts writing new or updated data to both columns. It should read the data
   from the new column and only fall back to the old column if the new column is
   not yet populated.
1. Use a data transformation management command to move data from the previous
   column to the new column. To find the rows that need updating, iterate
   through the table by querying for rows that do not have a value in the new
   column yet. Because the version of the application running at this point is
   writing and reading from the new column (falling back to the old for reads
   when necessary), the query will eventually return zero rows.
1. Once the data transformation is complete, deploy a new version of the
   application that removes the old column and the fallback reads to it and only
   uses the new column. Also, add the corresponding constraints for the said
   column if required, e.g. non-nullable, default value, etc.

To reiterate, yes, this is a much more tedious process. However, the benefits to
this approach are listed below.

Relatively similar processes and patterns can be applied to other
"downtime-causing" database changes. These are covered in
[this GitHub gist](https://gist.github.com/majackson/493c3d6d4476914ca9da63f84247407b)
with specific instructions for handling them in a Django context.

### Benefits of this approach

#### Zero-downtime

The entire point, of course. This benefits everyone who depends on the
application's uptime and reliability.

#### Reversibility

If the new version of the application has a critical bug, whether related to the
data changes or not, we can revert each step to the previous version without
issue or data loss. Even during the data transformation process, because the
version of the application running is updating both columns, if you have to
revert to the first version (or even earlier) that doesn't use the new column,
the old column will still have up-to-date data and no user data will be lost.
This would complicate the data migration process, however, as previous versions
of the application will not be updating the new column and would likely require
deleting the data from the new column to start the data migration process over
from the start. This can cause massive time consumption but is overall less of a
headache than data loss or fully broken deployments.

#### Intentionality and expediency

Due to the great lengths it takes to change a column name, the process will
inevitably cause contributors to ask themselves: is this worth it? While
changing the name of a column can be helpful to disambiguate the data in the
column, using a model attribute alias can be just as helpful without any of the
disruption or time of a data transformation. These kinds of questions prompt us
to make expedient choices that deliver features, bug fixes, and developer
experience improvements faster.

#### Shorter deployment times

Ideally maintainers orchestrating a production deployment of the service are
keenly aware of the progress of the deployment. This is only a realistic and
sustainable expectation, however, if deployments take a "short" amount of time.
What "short" means is up for debate, but an initial benchmark can be the
Openverse production frontend deployments, which currently take about 10
minutes. Longer than this seems generally unreasonable to expect someone to keep
a very close eye on the process. Sticking to zero-downtime deployments helps
keep short deployments the norm. Even though it sometimes asks us to deploy more
_often_, those deployments can—and in all likelihood, should—be spread over
multiple days. This makes the expectation of keeping a close watch on the
deployment more sustainable long-term and helps encourage us to deploy more
often. In turn, this means new features and bug fixes get to production sooner.

#### Possibility to throttle

Management commands that iterate over data progressively can be throttled to
prevent excessive load on the database or other related services that need to be
accessed.

#### Unit testing

Management command data migrations can be far more easily unit tested using our
existing tools and fixture utilities.

### Long running migrations

Sometimes long-running schema changes are unavoidable. In these cases, provided
that the instructions above are followed to prevent the need for downtime, it is
reasonable to take alternative approaches to deploying the migration.

At the moment we do not have specific recommendations or policies regarding
these hopefully rare instances. If you come across the need for this, please
carefully consider the reasons why it is necessary in the particular case and
document the steps taken to prepare and deploy the migration. Please update this
document with any general findings or advice, as applicable.

## Django management command based data transformations

### Why use management commands for data transformations instead of Django migrations?

Django comes with a data transformation feature built in that allows executing
data transformations during the migration process. Transformations are described
in Django's ORM and executed in a single pass at migration time. If you want to
move data between two columns, it is trivial to do so with these "data
migrations" and Django makes it just as easy.
[Documentation for this Django feature is available here](https://docs.djangoproject.com/en/4.1/topics/migrations/#data-migrations).

When considering the potential issues with using Django migrations for data
transformations with our current deployment strategy, keep in mind the following
details:

- Migrations are run _at the time of deployment_ by the first instance of the
  new version of the application that runs in the pool.
  - **Note**: This specific detail will only be the case once we've fully
    migrated to ECS based deployments. For now one of the people deploying the
    application manually runs the migrations before deploying. The effect is the
    same though: we end up with a version of the application running against a
    database schema that it's not entirely configured to work with. Whether that
    is an issue depends solely on whether the practices described in this
    document regarding migrations have been followed.
- Deployments should be timely so that developers are able to reasonably monitor
  their progress and have clear expectations for how long a deployment should
  take. Ideally a full production deployment should not take much longer than 10
  minutes once the Docker images are built. Those minutes are already spent by
  the process ECS undergoes to deploy a new version of the application.

With those two key details in mind, the main deficiency of using migrations for
data transformations may already be evident: time. Django migration based data
transformations dealing with certain smaller tables may not take very long and
this issue, in some cases, might not be applicable. However, because it is
extremely difficult to predetermine the amount of time a migration will take,
even data transformations for small datasets should still heed the
recommendation to use management commands. In particular, it can be difficult to
predict tables with indexes (especially unique constraints) will perform during
a SQL data migration.

Realistically (and provided it is avoidable), any Django migration that takes
longer than 30 or so seconds, is not acceptable for our current deployment
strategy. Because the vast majority of them will take longer than a few seconds,
there is a strong, blanket recommendation against using them. Exceptions may
exist for this recommendation, however. If you're working on an issue that
involves a data transformation, and you think a migration is truly the best tool
for the job and can demonstrate that it will not take longer than 30 seconds in
production, then please include these details in the PR.

### General rules for data transformations

These rules apply for data transformations executed as management commands or
otherwise.

#### Data transformations must be [idempotent](https://en.wikipedia.org/wiki/Idempotence)

This one particularly applies to management commands because they can
theoretically be run multiple times, either by accident or as an attempt to
recover from or continue after a failure.

Idempotency is important for data transformations because it prevents
unnecessary duplicate processing of data. Idempotency can be achieved in three
ways:

1. By checking the state of the data and only applying the transformation to
   rows for which the transformation has not yet been applied. For example, if
   moving data between two columns, only process rows for which the new column
   is null. Once data has been moved for a row, it will no longer be null and
   will be ignored from the query.
1. By checking a timestamp available for each row before which it is known that
   data transformations have already been applied.
1. By caching a list of identifiers for already processed rows in Redis.

#### Data transformations should not be destructive

Data transformations should avoid being destructive, if possible. Sometimes it
is avoidable because data needs to be updated "in place". In these cases, it is
imperative to save a list of modified rows (for example, in a Redis set) so that
the transformation can be reversed if necessary.

### If a Django migration _must_ be used

In the rare case where a Django migration must be used, keep in mind that using
a
[non-atomic migration](https://docs.djangoproject.com/en/4.1/howto/writing-migrations/#non-atomic-migrations)
can help make it easier to recover from unexpected errors without causing the
entire transformation process to be reversed.
