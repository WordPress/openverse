# 2024-01-22 Implementation Plan: Bulk Moderation Actions

**Author**: @stacimc

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @sarayourfriend
- [x] @obulat

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/383)
- [Project Proposal](https://docs.openverse.org/projects/proposals/trust_and_safety/content_report_moderation/20230411-project_proposal_content_report_moderation.html#bulk-moderation-actions-requirement-3)

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

Typically, moderation actions are applied to individual records in response to a
Report (see this
[IP](https://docs.openverse.org/projects/proposals/trust_and_safety/content_report_moderation/20231208-implementation_plan_django_admin_moderator_access.html)
for more details). However it may occasionally be necessary to perform a
moderation action to a large set of records at once.

For example, after receiving a large number of user reports for images from a
particular creator, it may be beneficial to quickly mark all results from that
creator as sensitive, or else deindex them entirely. Because these bulk actions
necessarily affect large numbers of records without careful individual review,
it's also necessary to be able to _undo_ these actions (for example, if further
investigation reveals that only a subset of the records needs to be marked
sensitive). We should also be able to view these bulk decisions as part of the
complete moderation history of an individual record.

This IP extends the work described in the
[Django admin moderator access control and base improvements](https://docs.openverse.org/projects/proposals/trust_and_safety/content_report_moderation/20231208-implementation_plan_django_admin_moderator_access.html)
IP to add support for these features. I have attempted to summarize all relevant
parts of that IP as needed here, but for full context that IP should be
considered prerequisite reading. For brevity it is referred to as "the related
IP" hereafter.

### Models

No new models need be added; rather, we will make some small changes to the
`ModerationDecision` model described in
[this section](https://docs.openverse.org/projects/proposals/trust_and_safety/content_report_moderation/20231208-implementation_plan_django_admin_moderator_access.html#moderationdecision)
of the related IP. See the [Alternatives section](#alternatives) of this
document for a discussion of why we choose this route, rather than adding new
models.

As a reminder, these are the fields from the `ModerationDecision` model which
will not be changed:

- `id`
- `created_on`
- `moderator_id`
- `explanation`

The following changes will be made to the `media_identifier` and `action`
fields:

#### `media_identifiers`

`media_identifier` (previously a one-to-one relationship to the media the
decision is related to), will be updated to `media_identifiers` _plural_: a
many-to-many relationship to potentially multiple media records the decision is
related to. Under the covers, this will be implemented by a join table. As
pointed out in the related IP, the media identifiers must be non-constrained
(indexed non-unique UUIDs rather than foreign keys, using the
[`db_constrained` argument](https://docs.djangoproject.com/en/5.0/ref/models/fields/#django.db.models.ManyToManyField.db_constraint)
to the ManyToManyField), because deindexing media removes them from the API
database.

The relationship is many-to-many because:

- A moderation decision _may_ affect many records, in the case of a bulk
  decision
- A record may be affected by multiple decisions, with the addition of actions
  to undo deindexing and marking sensitive.

Using the join table to tie multiple records to a single decision (rather than,
for example, creating a separate `ModerationDecision` record for each record
selected for bulk update), has significant cost savings and more accurately
models the data as a single decision.

#### `action`

This is a slug column describing the action taken. In addition to the action
types defined in the related IP, we will add two new options:

- `reversed_deindex` - Undo a previous deindexing decision.
- `reversed_mark_sensitive` - Undo a previous decision marking the applicable
  records sensitive.

For consistency we will also update the existing action type
`confirmed_sensitive` to `marked_sensitive` to describe the effect of the action
without the use of the word "confirm", which is accurate when describing single
decisions made by moderators but potentially inappropriate for describing bulk
actions that do not include individual review of records. We will also update
the existing action type `duplicate_reports` to `deduplicated_reports` for
clarity and consistency.

## Actions

The related IP describes adding new custom Django
[admin actions](https://docs.openverse.org/projects/proposals/trust_and_safety/content_report_moderation/20231208-implementation_plan_django_admin_moderator_access.html#actions)
for each of the action types described in that IP. These actions are called from
the Report view and take action on a list of MediaReports to create a
ModerationDecision. They do not need to be modified, except to use the
many-to-many `media_identifiers` column (although in this workflow only a single
record will ever be added.)

We will need to add new actions for making moderation decisions directly from a
list of Media, as well as two new actions for the `reversed_<x>` action types.

_All bulk_ actions go through an intermediate confirmation page which:

- Indicates the number of records that will be affected by the action
- Collects the required `explanation` text (all other columns, such as
  `moderator_id` and `created_on`, are filled in automatically)

### Bulk Mark Sensitive: mark the works as sensitive

This action takes a queryset of `AbstractMedia` records. It filters the queryset
for those records **which do not already have a related `SensitiveMedia`
record**, then adds them to a new ModerationDecision with type
`marked_sensitive`. It then creates and saves `SensitiveMedia` records for each
of the added records.

The confirmation page for this action should indicate the number of records that
will actually be affected. If some records are already marked sensitive, that
should be indicated on the confirmation page as well.

### Bulk Deindex sensitive: entirely exclude the works from Openverse due to sensitivity

This action takes a queryset of `AbstractMedia` records. It creates a
ModerationDecision with type `deindexed_sensitive` and adds all records from the
queryset. It then creates and saves `DeletedMedia` records for each of these,
deleting the record from the API and deindexing it in Elasticsearch. The
confirmation page for this action should include a highly visible warning that
once records are deindexed, they cannot be restored immediately.

Note that it is not necessary to check that a `DeletedMedia` record does not
already exist, because deindexing a record deletes it from the database (so it
is not possible to call this action on already deleted records).

### Bulk Deindex copyright: entirely exclude the works from Openverse due to copyright

Identical to the other bulk deindex, except the action type is
`deindexed_copyright`.

### Reverse Mark Sensitive: undo marking the selected works as sensitive

This action takes a queryset of `SensitiveMedia` records, rather than
`AbstractMedia`. Each `SensitiveMedia` record has a related `media_obj`, which
are what will be added to the ModerationDecision. It creates a
ModerationDecision with type `reversed_mark_sensitive`, and adds the related
media. Then it first calls `_update_es` on the `SensitiveMedia` records to
update the Elasticsearch index with the "sensitive" field for each media record,
and finally deletes the actual `SensitiveMedia` records.

Although the `SensitiveMedia` records are deleted, the ModerationDecisions
preserve the history of these actions, and Django's LogEntry table will also
automatically record the creation and deletion of the `SensitiveMedia` records.

### Reverse Deindex: undo deindexing the selected works

This action takes a queryset of `DeletedMedia` records, rather than
`AbstractMedia`. Like `SensitiveMedia`, each `DeletedMedia` record has a related
`media_obj`, which will be added to the ModerationDecision. The action creates a
ModerationDecision with type `reversed_deindex` and adds the related records.
Then it deletes the `DeletedMedia` records.

It is extremely important to note that this action does not immediately result
in deindexed records being added back to the DB and Elasticsearch indices. When
the records were originally deindexed, they were deleted from both, and there is
no quick way to restore them without running a data refresh. The confirmation
page should contain a highly visible `info` block explaining this to the user.

Although the `DeletedMedia` records are deleted, the ModerationDecisions
preserve the history of these actions, and Django's LogEntry table will also
automatically record the creation and deletion of the `DeletedMedia` records.

### Other actions

We do _not_ need to add any new action types for `rejected_reports` and
`deduplicated_reports`, which are only applicable to the Report view flow
described in the related IP.

## Views

We will add one new read-only view for viewing ModerationDecisions, but most
changes will be to existing views.

### Media views

We will add the custom bulk actions for `deindex_sensitive`,
`deindex_copyright`, and `mark_sensitive` to the dropdown in the Media views.
Bulk moderation decisions of these types will be created by taking these
actions.

However the current Media views only allow filtering records by uuid. To
facilitate selecting records for bulk action, we'll add some additional custom
text filters to the sidebar:

- `query` - this field searches for a match in `description`, `tags`, or `title`
- `provider`
- `creator` - this field should have helptext reminding the user to also filter
  by provider in order to disambiguate a specific creator.

The custom filters should be implemented to query Elasticsearch rather than
Postgres for records, for significantly improved search efficiency. Additional
filters may be added in the future as appropriate.

### DeletedMedia List View

We'll add the `reversed_deindex` action to this list view, allowing maintainers
to select a list of deindexed records and undo deindexing from this view.

To facilitate easily undoing a particular bulk ModerationDecision, we will add a
text filter for searching by ModerationDecision id. That allows you to select
all records that were deleted as part of a particular decision.

### SensitiveMedia List View

We will add the `reversed_mark_sensitive` action to this list view, allowing
maintainers to select a list of sensitive media and unmark them as sensitive
from this view.

Similar to the DeletedMedia list view, we will add a filter for
ModerationDecision id to facilitate easily undoing an entire bulk
ModerationDecision.

### ModerationDecisions List View

To make it easy to view historical ModerationDecisions, we will add one new list
view. In the view, decisions will be sorted by creation date, and will display:

- `id`
- `action`
- `explanation` - truncated `explanation` column
- `record_count` - a count for the number of records affected by this decision

This view is useful for getting the id of a moderation decision that you want to
reverse. We will add a custom filter to display only bulk moderation decisions,
defined as a ModerationDecision with more than one media record.

Clicking on an individual ModerationDecision will take you to a detail view that
is entirely read-only, as a moderation decision should not be edited after it is
created. For ModerationDecisions with a `deindexed_sensitive`,
`deindexed_copyright`, or `marked_sensitive` action type, we will include a link
to the SensitiveMedia or DeletedMedia view, filtered by the ModerationDecision
id for convenience.

We will disable the option to add a ModerationDecision object directly.

### Report view

No changes are needed to the Report view. Note that by extending the
ModerationDecision model rather than adding a new model, when a record is viewed
from the Report view _all_ related moderation decisions (including bulk actions)
will automatically be visible to moderators.

## Access control

Because bulk moderation decisions can affect a very large number of records,
access should be limited to only maintainers. We will use Django's existing
permissions support to ensure that the relevant actions are only visible to
maintainers.

If we would like to change this policy in the future to allow moderators to make
bulk decisions, that can be added easily.

## Concurrency

It's possible, even likely, that reports may exist for some records that we'd
like to take bulk action on. For example, imagine a scenario where a particular
creator is producing large numbers of sensitive images that are not caught by
existing filters. We may discover this situation after receiving many user
reports, and decide to mark all of the creator's records as sensitive in bulk.
It is therefore necessary to ensure that moderators do not, for example, deindex
an individual record that is simultaneously being deindexed by a bulk action.

To do this, we will use atomic transactions and Django's
[select_for_update](https://docs.djangoproject.com/en/5.0/ref/models/querysets/#select-for-update)
to lock the records being selected for bulk action in each of the custom
actions.

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

When this work is completed we will be able to do the following new things:

- Filter media in the media views by search terms, or by provider/creator
- Mark a selection of multiple records as sensitive, as part of a single
  decision
- Deindex a selection of multiple records, as part of a single decision
- Undo marking sensitive and deindexing, for one or more records
  - This includes undoing individual ModerationDecisions by moderators
  - This also includes undoing a subset of a previous ModerationDecision

It is equally important to identify what is out of scope for this work:

Performing a bulk moderation decision will only affect records that are
currently in the API, with no effect on records in the Catalog. For example, if
a maintainer uses this workflow to deindex all records made by a particular
Flickr user, this does not prevent the Flickr DAG from ingesting _new_ records
by that same user, which will be added to the API in the next data refresh.
Preventing new records from being added, or otherwise propagating deleted
records to the Catalog, is out of scope for this project.

## Step-by-step plan

<!--
List the ordered steps of the plan in the form of imperative-tone issue titles.

The goal of this section is to give a high-level view of the order of implementation any relationships like
blockages or other dependencies that exist between steps of the plan. Link each step to the step description
in the following section.

If special deployments are required between steps, explicitly note them here. Additionally, highlight key
milestones like when a feature flag could be made available in a particular environment.
-->

The basic steps are:

- Create the actions
- Update the Media views with new filters and bulk actions
- Add new bulk actions to the Media views
- Add action and filter to the DeletedMedia view
- Add action and filter to the SensitiveMedia view
- Create the read-only ModerationDecision view

We will also need to modify the
[existing issue](https://github.com/WordPress/openverse/issues/3636) for
creating the ModerationDecision model to meet the new requirements.

## Step details

<!--
Describe all of the implementation steps listed in the "step-by-step plan" in detail.

For each step description, ensure the heading includes an obvious reference to the step as described in the
"step-by-step plan" section above.
-->

### Create the actions

[See "Actions" section for a description of all actions](#actions)

Create the custom admin actions for:

- bulk deindex sensitive
- bulk deindex copyright
- bulk mark sensitive
- bulk reverse mark sensitive
- bulk reverse deindex

### Update the Media views with new filters and bulk actions

[See "Media views" section for details](#media-views)

- Add the actions for bulk deindexing and marking sensitive to the media views,
  available only for maintainers
- Add the new filters for search terms, provider, and creator, querying
  Elasticsearch

### Add action and filter to the DeletedMedia view

[See "DeletedMedia List View" section for details](#deletedmedia-list-view)

- Add the bulk reverse deindex action
- Add a filter for ModerationDecision id

### Add action and filter to the SensitiveMedia view

[See "SensitiveMedia List View" section for details](#sensitivemedia-list-view)

- Add the bulk reverse mark sensitive action
- Add a filter for ModerationDecision id

### Create the read-only ModerationDecision view

[See "ModerationDecisions List View" section for details](#moderationdecisions-list-view)

- Add the list view
- Add read-only detail view

## Dependencies

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

No changes needed.

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

This is heavily tied to the
[related IP](https://docs.openverse.org/projects/proposals/trust_and_safety/content_report_moderation/20231208-implementation_plan_django_admin_moderator_access.html)
and in fact changes some pieces of it slightly.

## Alternatives

<!-- Describe any alternatives considered and why they were not chosen or recommended. -->

Several alternative ideas were explored as part of this work:

### Creating a separate BulkModerationDecision model

Many variations on creating additional models were considered and rejected
because:

- It resulted in additional complexity for ultimately very similar models
- By having a single model instead we get many things for free, such as:
  - bulk decisions are visible in the Report view, which is valuable context for
    moderators
  - individual decisions are visible in the ModerationDecision view
  - the DeletedMedia and SensitiveMedia views allow filtering by id for any type
    of moderation decision

For example, one option was to create a separate ModerationDecision for each
record in a bulk decision, with an optional foreign_id to the
BulkModerationDecision parent object. This would result in potentially massive
duplication of information, however, if large bulk decisions are made.

I also considered having `provider` and `creator` as columns on a special type
of ModerationDecision for all of a particular creator's records.

- This adds complexity and even more ModerationDecision types; alternatively,
  these would be nullable columns that are not always applicable (again, adding
  complexity)
- May cause confusion by implying that a record which does have these fields
  should apply to absolutely all records by that creator, when this may not be
  the case (for example, if some records by this creator have already been
  deindexed/marked sensitive by previous decisions)
- Ultimately this context should be included in the `explanation` field
  regardless

### Having a special form for creating ModerationDecisions that affect all records by a creator

I considered including the ability to add a ModerationDecision directly, with a
modified form that would take `creator` and `provider` rather than selecting the
individual records to add.

However, this duplicates some work, and makes it much more confusing to explain
the various ways that a decision can be made. It is also already possible to do
this sort of bulk action by filtering in the Media views on creator/provider.

### Having an "undo" action on individual decisions in the ModerationDecision list view

This was an alternative to requiring the user to look up the id of the decision
they want to reverse, and then filter for those records in the SensitiveMedia or
DeletedMedia views to create a new decision.

However this quickly becomes much more complicated. One example is that it does
not make sense to undo a decision twice. It also makes it extremely difficult to
add some useful features like:

- Undoing a _subset_ of a decision, for example if we deindex all of a
  particular creator's record but realize upon further investigation that only
  some of them needed to be deindexed.
- Undoing _all_ deindexing/marking sensitive for a particular creator, including
  ones that were originally acted upon by individual reports.

### A DAG for bulk decisions

It's difficult to anticipate all the ways that we might need to filter records
for selecting a set to take action on. Moreover, filtering in the Django admin
views (especially by text search terms) may be extremely slow for some use
cases.

The project proposal's requirements indicate that we need to be able to make
bulk decisions with selections from admin views. However, I considered adding a
DAG in addition to the custom actions that would allow for maximum flexibility.
The DAG which would take an arbitrary SELECT query for selecting records to add
to a new ModerationDecision.

However, this duplicates some logic and may be excessive optimization for now.
It would also prevent us from easily extending permission to moderators if
desired. A DAG may be considered for future optimization if necessary.

## Design

<!-- Note any design requirements for this plan. -->

None, we'll stick with Django admin default styles.

## Blockers

<!-- What hard blockers exist that prevent further work on this project? -->

We must first resolve the overlap with the
[related IP](https://docs.openverse.org/projects/proposals/trust_and_safety/content_report_moderation/20231208-implementation_plan_django_admin_moderator_access.html).

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

Nothing that can't be easily rolled back, except the changes to
ModerationDecision relative to the original plan. This IP does not require
making changes to any other models.

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

This work allows for bulk actions which would have dramatic effects, like for
example deindexing an extremely large number of records. When that happens, we
can reindex but we still need to do a data refresh afterward to get the data
back, which may take several days.

This is mitigated by tightly restricting access and adding a confirmation page
that reiterates the number of records that are about to be affected by a
decision, so a maintainer does not accidentally deindex much more than intended.
We _could_ also put a limit to the number of records that can be deindexed in a
single moderation decision as an additional precaution; however, this new bulk
action does not add any _new_ risk compared to the existing bulk delete actions
so I do not think this is necessary.

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->

- [Django admin moderator access control and base improvements IP](https://docs.openverse.org/projects/proposals/trust_and_safety/content_report_moderation/20231208-implementation_plan_django_admin_moderator_access.html)
- [Django admin documentation](https://docs.djangoproject.com/en/4.2/ref/contrib/admin/#inlinemodeladmin-objects)
