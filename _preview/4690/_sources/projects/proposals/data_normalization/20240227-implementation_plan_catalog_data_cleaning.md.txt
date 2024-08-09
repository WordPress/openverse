# 2024-02-27 Implementation Plan: Catalog Data Cleaning

**Author**: @krysal

## Reviewers

- [x] @obulat
- [x] @AetherUnbound

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/430)

This project does not have a project proposal because the scope and rationale of
the project are clear, as defined in the project thread. In doubt, check the
[Expected Outcomes](#expected-outcomes) section below.

## Overview

This document describes a mechanism for rectifying incorrect data in the catalog
database (DB) that currently has to be cleaned up every time a data refresh is
run. This one-time fix is an effort to avoid wasting resources and data refresh
runtime.

## Background

One of the steps of the [data refresh process for images][img-data-refresh] is
cleaning the data that is not fit for production. This process is triggered
weekly by an Airflow DAG, which then runs in the Ingestion Server, taking
approximately just over **20 hours** to complete, according to a inspection of
recent executions as of the time of drafting this document. The cleaned data is
only saved to the API database, which is replaced each time during the same data
refresh, meaning this process has to be repeated each time to make the _same_
corrections.

This cleaning process was designed this way to optimize writes to the API
database, since the most important factor was to provide the correct data to
users via the API. Most of the rows affected were added prior to the creation of
the `MediaStore` class in the Catalog (possibly by the discontinued CommonCrawl
ingestion) which is nowadays responsible for validating the provider data prior
to upserting the records into the upstream database. However, the current
approach entails a problem of wasting resources both in time, which continues to
increase, and in the machines (CPU) it uses, which could easily be avoided
making the changes permanent by saving them in the upstream database.

[img-data-refresh]: ./../../../catalog/reference/DAGs.md#media_type_data_refresh

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

- The catalog database (upstream) contains the cleaned data outputs of the
  current Ingestion Server's cleaning steps
- The image Data Refresh process is simplified by reducing significantly
  cleaning times.

<!-- removing the cleaning steps from the Ingestion Server. -->

## Step-by-step plan

The cleaning functions that the Ingestion Server applies (see the
[cleanup][ing_server_cleanup] file) are already implemented in the Catalog in
the `MediaStore` class: see its [`_tag_blacklisted` method][tag_blacklisted]
(which probably should be renamed) and the [url utilities][url_utils] file. The
only part that it's not there and can't be ported is the filtering of
low-confidence tags, since provider scripts don't save an "accuracy" by tag.

With this the plan then starts in the Ingestion Server with the following steps:

1. [Save TSV files of cleaned data to AWS S3](#save-tsv-files-of-cleaned-data-to-aws-s3)
1. [Make and run a batched update DAG for one-time cleanup](#make-and-run-a-batched-update-dag-for-one-time-cleanups)
1. [Run an image Data Refresh to confirm cleaning time is reduced](#run-an-image-data-refresh-to-confirm-cleaning-time-is-reduced)

[ing_server_cleanup]:
  https://github.com/WordPress/openverse/blob/f8971fdbea36fe0eaf5b7d022b56e4edfc03bebd/ingestion_server/ingestion_server/cleanup.py#L79-L168
[tag_blacklisted]:
  https://github.com/WordPress/openverse/blob/f8971fdbea36fe0eaf5b7d022b56e4edfc03bebd/catalog/dags/common/storage/media.py#L245-L259
[url_utils]:
  https://github.com/WordPress/openverse/blob/a930ee0f1f116bac77cf56d1fb0923989613df6d/catalog/dags/common/urls.py

## Step details

### Save TSV files of cleaned data to AWS S3

In a previous exploration, the Ingestion Server was set to [store TSV files of
the cleaned data][pr-saving-tsv] in the form of `<identifier> <cleaned_field>`,
which can be used later to perform the updates efficiently in the catalog DB,
which only had indexes for the `identifier` field. These files are saved to the
disk of the Ingestion Server EC2 instances, and worked fine for files with URL
corrections since this type of fields is relatively short, but became a problem
when trying to save tags, as the file turned too large and filled up the disk,
causing issues to the data refresh execution.

[aws_mpu]:
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html

To have some numbers of the problem we are dealing with, the following table
shows the number of records cleaned by field for last runs at the moment of
writing this IP, except for tags, which we don't have accurate registries since
file saving was disabled.

| timestamp (UTC)     | 'url' | 'creator_url' | 'foreign_landing_url' | 'tags' |
| ------------------- | :---: | :-----------: | :-------------------: | :----: |
| 2024-02-27 04:05:26 | 22156 |    9035458    |        8809213        |   0    |
| 2024-02-20 04:06:56 | 22157 |    9035456    |        8809209        |   0    |
| 2024-02-13 04:41:22 | 22155 |    9035451    |        8809204        |   0    |

The alternative is to upload TSV files to the Amazon Simple Storage Service
(S3), creating a new bucket or using a subfolder within `openverse-catalog`. The
benefit of using S3 buckets is that they have streaming capabilities and will
allow us to read the files in chunks later if necessary for performance. The
downside is that objects in S3 don't allow appending natviely, so it may require
to upload files with different part numbers or evaluate if the [multipart upload
process][aws_mpu] or more easily, the [`smart_open`][smart_open] package could
serve us here.

[smart_open]: https://github.com/piskvorky/smart_open

### Make and run a batched update DAG for one-time cleanups

A batched catalog cleaner DAG (or potentially a `batched_update_from_file`)
should take the files of the previous step to perform a batched update on the
catalog's image table, while handling deadlocking and timeout concerns, similar
to the [batched_update][batched_update]. This table is constantly in use by
other DAGs, such as those from providers ingestion or the data refresh process,
and ideally can't be singly blocked by any DAG.

[batched_update]: ./../../../catalog/reference/DAGs.md#batched_update

A [proof of concept PR](https://github.com/WordPress/openverse/pull/3601)
consisted of uploading each file to temporary `UNLOGGED` DB tables (which
provides huge gains in writing performance while their disadventages are not
relevant to us, they won't be permanent), and include a `row_id` serial number
used later to query it in batches. The following must be included:

- Add an index for the `identifier` column in the temporary table after filling
  it up, to improve the query performance
- An adaptation to handle the column type of tags (`jsonb`) and modify the
  `metadata`
- Include a DAG task for reporting the number of rows affected by column to
  Slack

### Run an image data refresh to confirm cleaning time is reduced

Finally, after the previous steps are done, running a data refresh will confirm
there are no more updates applied at ingestion. If time isn't significantly
reduced then it will be necessary to check what was missing in the previous
steps. Looking at files generated in the
[step 1](#save-tsv-files-of-cleaned-data-to-aws-s3) may yield clues.

If confirmed the time is reduced to zero, optionally the cleaning steps can be
removed, or leave them in case we want to perform a similar cleaning effort
later, e.g. see the [Other projects or work](#other-projects-or-work) section.

## Dependencies

### Infrastructure

No changes needed. The Ingestion Server already has the credentials required to
[connect with AWS](https://github.com/WordPress/openverse/blob/a930ee0f1f116bac77cf56d1fb0923989613df6d/ingestion_server/ingestion_server/indexer_worker.py#L23-L28).

### Tools & packages

<!-- Describe any tools or packages which this work might be dependent on. If multiple options are available, try to list as many as are reasonable with your own recommendation. -->

Requires installing and familiarizing with the [smart_open][smart_open] utility.

### Other projects or work

Once the steps have been completed and proved the method works we could make
additional similar corrections following the same procedure. Some potentially
related issues are:

- [Some images have duplicate incorrectly decoded unicode tags #1303](https://github.com/WordPress/openverse/issues/1303)
- [Provider scripts may include html tags in record titles #1441](https://github.com/WordPress/openverse/issues/1441)
- [Fix Wikimedia image titles #1728](https://github.com/WordPress/openverse/issues/1728)
- [Add filetype to all images in the catalog DB #1560](https://github.com/WordPress/openverse/issues/1560),
  for when the file type can be derived from the URL.

This will also open up space for more structural changes to the Openverse DB
schemas in a [second phase](https://github.com/WordPress/openverse/issues/244)
of the Data Normalization endeavor.

## Alternatives

A previous proposal was to use the `ImageStore` to re-evaluate every image in
the catalog DB. While this could theoretically be performed in a batched way
too, and presented the advantage of future validations to be easily incorpored
in a single place, it also came with significant shortcomings and complexities.
The class would have to adapt to validations for images ingested by the
CommonCrawl process, for which it was not planned and could open a can of extra
problems. It would also have to go through the entire database to update the bad
rows, unless a mix of both proposal is implemented, but ultimately the process
of this IP is considered more direct and simple for the goal.

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

In the rare case we need the old data back, we can resort to DB backups, which
are performed [weekly][db_snapshots].

[db_snapshots]: ./../../../catalog/reference/DAGs.md#rotate_db_snapshots

<!--
## Risks

What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

## Prior art

- Previous attempt from cc-archive: [Clean preexisting data using ImageStore
  #517][mathemancer_pr]
- @obulat's PR to [add logging and save cleaned up data in the Ingestion
  Server][pr-saving-tsv]

[pr-saving-tsv]: https://github.com/WordPress/openverse/pull/904
[mathemancer_pr]: https://github.com/cc-archive/cccatalog/pull/517
