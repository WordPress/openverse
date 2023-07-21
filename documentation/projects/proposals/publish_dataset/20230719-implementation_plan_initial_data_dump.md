# 2023-07-19 Implementation Plan: Initial Data Dump

**Author**: @aetherunbound

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [ ] @obulat
- [ ] @stacimc
- [ ] @apolinario (optional)
- [ ] @Skylion007 (optional)
- [ ] @zackkrida (optional)

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/2545)
- [Project Proposal](https://docs.openverse.org/projects/proposals/publish_dataset/20230706-project_proposal.html)

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

This plan describes how the initial data dump of the media tables within
Openverse's API database will occur on a technical level, as well as information
regarding marketing and documentation of the initial data dump.
[HuggingFace](https://huggingface.co/) has graciously offered to host the
dataset for free, and this plan assumes that a handoff of our data to the
HuggingFace team will be made to accomplish this.

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

Upon the completion of this implementation plan, the following should be
available:

- An unscheduled DAG which is capable of generating the data dump in S3.
- A copy of the Openverse API database's primary media tables (i.e. `image` and
  `audio`), in parquet format, is present within a "requester pays" S3 bucket
  which can be accessed by the HuggingFace team for consumption into their
  platform.
- Documentation describing the "as-is" nature of the provided data, along with
  descriptions of the fields present for each media type and the parquet files
  themselves.
- Updated internal documentation (e.g. API docs, our developer handbook, our
  docs site, and potentially Openverse.org) referencing the dataset hosted by
  HuggingFace (once it is made available)

## Dependencies

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

[ec2createoperator]:
  https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/operators/ec2/index.html#airflow.providers.amazon.aws.operators.ec2.EC2CreateInstanceOperator
[ec2terminateoperator]:
  https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/operators/ec2/index.html#airflow.providers.amazon.aws.operators.ec2.EC2TerminateInstanceOperator

**EC2 instance selection**

Converting the data in our API database into any usable format will require a
non-trivial amount of disk storage and compute time. Our desire is to deliver
one or several parquet files per media type, and AWS does not provide the means,
through its existing services, to accomplish this without additional processing.
The easiest way of achieving this is to spin up an on-demand
[EC2 instance](https://aws.amazon.com/ec2/instance-types/) with either
sufficient on-disk space (as for the
[storage optimized units](https://aws.amazon.com/ec2/instance-types/#Storage_Optimized))
or with an attached [block storage device](https://aws.amazon.com/ebs/)
(available to most EC2 instances).

Below are some rough calculations for potential compute time across various EC2
types. For all EC2 instances except the storage optimized one, these costs
include an attached 3TB HDD
([`st 1` throughput-optimized type](https://aws.amazon.com/ebs/throughput-optimized/))
EBS volume. These costs estimate 168 hours of runtime (~1 week) to process all
the data[^1].

[^1]:
    The 1-week processing estimate is not based on any data, but provides at
    least a benchmark for estimating costs. There are some significant
    differences in compute/memory between the various options which will impact
    the time the parquet generation takes.

| Purpose                          | Instance Type | vCPU | Memory (GiB) | Volume Size     | Cost (USD) |
| -------------------------------- | ------------- | ---- | ------------ | --------------- | ---------- |
| General purpose low performance  | `m7g.xlarge`  | 4    | 16           | 3TB             | ~$60       |
| General purpose high performance | `m7g.4xlarge` | 16   | 64           | 3TB             | ~$141      |
| Memory optimized                 | `r7g.4xlarge` | 16   | 128          | 3TB             | ~$175      |
| Storage optimized                | `i4g.4xlarge` | 16   | 128          | 3.7TB (non-EBS) | ~$200      |

Given the cost of running an instance for one week as listed above, my
recommendation would be to use the **Storage optimized `i4g.4xlarge`** instance
class for easiest configuration.

**Managing the infrastructure**

Presently, the bulk of our infrastructure is defined using Terraform in our
separate
[infrastructure repository](https://github.com/WordPress/openverse-infrastructure).
Given the one-off (or extremely infrequent) nature of these dumps, it is my
recommendation that we **do not** define the configuration for this device in
Terraform. Instead, we can have the infrastructure itself entirely managed by
Airflow. The AWS Airflow provider offers an
[`EC2CreateInstanceOperator`][ec2createoperator], which accepts the run
configuration and parameters for the instance. The config for the instance can
be stored alongside the Airflow DAG code which executes it, and Airflow can
ensure that the instance is terminated (on both success and failure) using the
[`EC2TerminateInstanceOperator`][ec2terminateoperator]. This allows us to
include all of the operational code for the data dump effort in a single
repository rather than have it spread across both repositories (and have to
manage deployment of the instance manually with Terraform prior to running the
data dump).

### Tools & packages

<!-- Describe any tools or packages which this work might be dependent on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

**odbc2parquet**

In order to remain efficient in the processing & transfer of data, the tables
will be written using the [Apache Parquet](https://parquet.apache.org/) file
type. This column-oriented data file is ideal for fast storage, compressed file
types, and relational data. We expect the produced parquet files to be
significantly smaller than any comparable TSV produced from our dataset.
Additionally, HuggingFace has shared that their preferred dataset format is
parquet[^2].

[^2]: <https://github.com/WordPress/openverse/pull/2637#discussion_r1261521786>

Since we will be running this operation on a transient EC2 instance (and we
already have the AWS provider installed for Airflow), new tools & packages
should not be necessary on any of our existing infrastructure. However, the EC2
instance will use the [odbc2parquet](https://github.com/pacman82/odbc2parquet)
CLI utility for pulling the data into one (or several) parquet files. The
utility provides
[a large number of options](https://github.com/pacman82/odbc2parquet/blob/b562c49e6190558e8efe0713c1fbfe56ff254439/src/main.rs#L105-L233)
for defining the maximum size/row count/properties of the output Parquet files.
Some optimization may be required here, but based on my research and Apache's
recommendations I would suggest a 2GB limit[^3].

[^3]:
    The recommendation in
    [Apache Parquet's documentation](https://parquet.apache.org/docs/file-format/configurations/)
    is ~1GB per file, but I've seen numerous other suggestions on Stack Overflow
    and elsewhere that 2GB is a reasonable amount if you don't require
    significant parallel processing (which our use case does not at this time).
    This will reduce the number of files to manage & share.

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

Although not a specific dependency, some of the effort taken as part of the
[document all media properties project][document_all_media] will likely be used
as a reference when generating the documentation to accompany this dataset.

[document_all_media]: https://github.com/WordPress/openverse/issues/412

## Outlined Steps

<!-- Describe the implementation step necessary for completion. -->

### Data dump generation DAG

This DAG will be an unscheduled DAG which creates a series of parquet files from
our production API database[^4] and uploads them to a designated S3 bucket. It
will accomplish most of these steps employing EC2 instances to perform most of
the processing (see the [infrastructure section](#infrastructure) above).

[^4]:
    At present, we will likely be performing a `SELECT *` or a simple join for
    these initial dumps. Since this is a direct read-and-stream operation from
    the database, it should not have a significant impact on the API's query
    performance.

**EC2 instance**:

The EC2 instance will be provided a
["user data" on-launch script](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html)
which will be executed when the container starts. The script steps are as
follows:

- Set necessary environment variables (e.g. AWS credentials, media type to
  process, Postgres connection info, destination S3 bucket, etc).
- [Install `odbc2parquet`](https://github.com/pacman82/odbc2parquet#linux).
- Install the AWS CLI on the instance (if not already installed).
- Run the `odbc2parquet query` command on a given media table with the
  appropriate command line settings.
- Use the AWS CLI to upload the generated files to S3, in a prefix based on the
  generation date (e.g. `s3://data-dump/YYYY-MM-DD/<media-type>/`).
- Add a success semaphore file for the media type (e.g.
  `s3://data-dump/YYYY-MM-DD/<media-type>/_success`), which will be used by the
  DAG to determine when a dump is successful.
- Initiate a shutdown of the EC2 instance (this will prevent the instance from
  running unused before Airflow ultimately terminates it).

**DAG Params**:

These are
[parameters](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/params.html#dag-level-params)
that will be handed into a given DAG run during execution.

- `s3_bucket`: (Optional) The S3 bucket to publish the files into, under the
  prefix `data-dump/YYYY-MM-DD`. This will default to the same bucket as the
  ingestion TSVs for local testing.
- `query`: (Optional) The query to be handed into `odbc2parquet`, formatted with
  the media type. By default, this will be `SELECT * FROM {media_type}`.
- Any additional parameters to be handed into `odbc2parquet` (not defined here
  as testing & exploration will be necessary during development). These should
  have sensible defaults, but can be overridden.

**Variables**:

These are
[Variables](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/variables.html)
that will be present (with noted defaults) and used for the DAG's execution.

- `DATA_DUMP_EC2_INSTANCE_CLASS`: The EC2 instance class mentioned above. The
  default for this should be `m7g.xlarge` (or an even smaller instance) so any
  local runs do not erroneously spin up expensive instances. In production this
  will be provided with the desired class.
- `DATA_DUMP_EBS_BLOCK_SIZE`: The size of the EBS volume, in GB, to attach to
  the EC2 instance. If `0` or negative, then no instance is attached. The
  default for this will be 100GB.

**DAG definition**:

The DAG will execute the following steps (_for each media type_):

- Generate the S3 key prefix that will be used
- Use the [`EC2CreateInstanceOperator`][ec2createoperator] to create the
  instance with the appropriately templated user data & configuration (from the
  params & Variables defined above)
- For each media type, use the
  [`S3KeySensor`](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/sensors/s3/index.html)
  to wait for the `_success` keys to be present
- Use the [`EC2TerminateInstanceOperator`][ec2terminateoperator] to terminate
  the instance once the success key is found, or after the `S3KeySensor` has
  timed out. This step's dependencies should be _both_ the EC2 create & S3 key
  sensor task, and its
  [trigger rule](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html#trigger-rules)
  should be set to `one_success` so it is always run if the EC2 creation is
  successful.
- Alert in Slack that the data dump is complete and under which S3 keys it is
  available.

### Documentation

We will need to provide documentation alongside the data dump describing both
the data fields themselves and the terms under which this data can be used. We
will also specify that the dataset is provided "as-is", although we hope to have
updates in the future.

License & use information can be gathered from the materials
[Creative Commons](https://creativecommons.org/) publishes. We may want to
employ HuggingFace's
[gated access for datasets](https://huggingface.co/docs/hub/datasets-gated) to
ensure these terms are acknowledged and accepted by consumers.

Information about fields will need to be created, although some of this effort
was initiated in the [document all media properties][document_all_media]
project. Specifically, this
[initial media properties description document](https://docs.google.com/spreadsheets/d/1qbzKc4NurABq1oH59QS7PoArNJIComWAciXqANDPlHk/edit#gid=51474613)
can be used as a basis for this information.

### Handoff to HuggingFace

Once the DAG has been run, the data dump has been created in S3, and the
accompanying documentation has been drafted, we can hand this dataset off to
HuggingFace for consumption & publishing on their platform. We will give
HuggingFace representatives access to the S3 bucket in a "requester pays"
fashion. HuggingFace will inform the Openverse maintainers if any other
information or work is necessary once this step is reached.

### Marketing

After the dataset has been published on HuggingFace, we will modify/add the
following pieces of documentation to point to it as a "bulk access" mechanism:

- [API documentation](https://api.openverse.engineering/v1/)
- [Make WordPress Handbook](https://make.wordpress.org/openverse/handbook/)
- [Primary documentation site](https://openverse.org)
- [Monorepo README.md](https://github.com/WordPress/openverse/blob/main/README.md)

We will broadcast the availability of this dataset on our various social media
accounts, and coordinate the announcement with HuggingFace and potentially
Creative Commons as well.

We will also reach out to all of the individuals who contacted us expressing
interest in a data dump to inform them of the newly available dataset.

## Alternatives

<!-- Describe any alternatives considered and why they were not chosen or recommended. -->

A number of alternatives were discussed
[in the issue for this implementation plan](https://github.com/WordPress/openverse/issues/2669).
Below are several alternatives and why they were deemed unsuitable.

### Leveraging a snapshot export

AWS provides a mechanism for our regular API database
[snapshots to be exported to S3](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ExportSnapshot.html)
in the form of parquet files. This requires a new IAM role which the export
process assumes, and an [AWS KMS](https://aws.amazon.com/kms/) key pair for
encrypting the data. The export process also generates parquet partitions which
are about 2-3 MB in size, meaning that our image table has on the order of
40,000 partitions. While we are able to limit the export to a subset of tables,
this reduces the flexibility we would have in post-processing or joining the
data together prior to publishing. Additionally, the large number of parquet
files may make the handoff to HuggingFace more difficult. Ultimately any
post-processing would require the use of EC2 anyway, so we abandoned this
approach in favor of a more flexible one which also did not require we manage
encryption keys during processing.

### AWS's built-in export extension

AWS RDS also provides
[an extension to Postgres for exporting data to S3](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/postgresql-s3-export.html).
This export mechanism, however, is limited to the output types available to
[Postgres's `COPY` command](https://www.postgresql.org/docs/current/sql-copy.html).
Parquet file types are not supported in Postgres for this type of export by
default. Similarly to the previous alternative, any post-processing into parquet
would require EC2 usage, so we are not pursuing this approach.

### AWS Glue

[AWS Glue](https://docs.aws.amazon.com/glue/) provides a mechanism for managing
data pipelines & conversions across many different AWS services.
[This guide by Amree Zaid on dev.to](https://dev.to/amree/exporting-data-from-rds-to-s3-using-aws-glue-mai)
describes a process one might employ to leverage AWS Glue for generating the
output parquet files in S3. We do not use AWS Glue for any other process, so
this could require significant infrastructure work in order to make it
functional. Much of this could be set up by hand as well, but that precludes the
ability to do regular, automated dumps like this in the future.

## Design

<!-- Note any design requirements for this plan. -->

Design work may be required when crafting the announcement social media posts
for the completion of this work.

## Parallelizable streams

<!-- What, if any, work within this plan can be parallelized? -->

Both the documentation and DAG development efforts can be worked on in parallel.
The process will become serial once the handoff to HuggingFace is completed.

## Blockers

<!-- What hard blockers exist which might prevent further work on this project? -->

There are currently no blockers for this work.

## Accessibility

<!-- Are there specific accessibility concerns relevant to this plan? Do you expect new UI elements that would need particular care to ensure they're implemented in an accessible way? Consider also low-spec device and slow internet accessibility, if relevant. -->

There are no additional accessibility considerations for this aspect of the
project.

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

Prior to handing off the dataset, we can remove the data dump DAG and delete any
related S3 buckets/prefixes related to this effort.

Once the handoff to HuggingFace is made, rollback will become much more
difficult. In the event that a rollback is necessary (either for legal or
technical reasons), we will need to coordinate with the HuggingFace team to
determine the appropriate next steps.

## Privacy

<!-- How does this approach protect users' privacy? -->

A full release of this dataset in bulk is a significant endeavor, one which
affects the privacy of all those who have contributed their works to the subset
of the commons which makes up the Openverse dataset. We will need to take effort
to ensure that those who wish to use the dataset understand the terms and
ramifications of the various license types present within the data, and any
models or derivatives from the works.

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

By opening our dataset up to bulk, public access, we are also enabling the
possibility that bad actors may use this dataset nefariously or intentionally
break the terms of the existing licenses within the dataset. We will need to do
all we can to ensure that liability for such acts rests solely on the
consumer/actor and not the Openverse project or HuggingFace as dataset hosts.

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->

- [HuggingFace datasets](https://huggingface.co/datasets)
- Previous issue:
  [Allow entire dataset to be downloaded en-masse](https://github.com/WordPress/openverse/issues/669)
