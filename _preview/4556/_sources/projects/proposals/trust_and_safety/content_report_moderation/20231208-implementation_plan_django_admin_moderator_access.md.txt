# 2023-12-08 Implementation Plan: Django admin tools and access control for moderators

**Author**: @sarayourfriend

## Reviewers

- [ ] @krysal
- [ ] @stacimc

## Project links

- [Project thread](https://github.com/WordPress/openverse/issues/383)
- [Relevant project proposal section](/projects/proposals/trust_and_safety/content_report_moderation/20230411-project_proposal_content_report_moderation.md#volunteer-moderator-django-admin-tools-and-access-control-requirement-2)

## Overview

```{note}
At time of writing, we haven't yet changed the name of the "mature" models to
"sensitive", so I've used the existing terminology for clarity during review of
this implementation plan.

If you're reading this during the actual implementation, keep in mind that those models
may have had their names changed to replace "mature" with "sensitive", as part of an
earlier aspect of this project.
```

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

There are two broad aspects of this implementation plan:

1. Access control for moderator users (in other words, users who should only
   have access to moderation tools and nothing else)
1. Improvements and additions to Django admin tools for working through content
   reports

There is also a significant bug that needs addressing: If a media object has
multiple sensitivity reports, only one can be saved as confirmed because there
is a
[one-to-one relationship between the `AbstractMatureMedia` and `AbstractMedia` models](https://github.com/WordPress/openverse/blob/aa16d4f1be7607b12c428886b9890bdd947cc71c/api/api/models/media.py#L346-L355)
and the report model admin does not handle this. The likelihood of this should
be all but eliminated by the process and tooling changes in this implementation
plan (because moderation reports will be handled in a single unified view for a
given work). However, we'll solve this bug directly anyway by not creating the
mature media object on save if one already exists for the work.

### Additional tools and improvements

We will add the following additional tools and improvements to the report admin:

- `ModerationDecision`
- Improve the table view's default behaviour and sorting
- A media moderation admin view to centralise moderation decisions for a given
  work to include all pending and historical reports and show the work's
  metadata

#### `ModerationDecision`

We will create a new `ModerationDecision` model for each media type, to
accompany the existing report models. The decision model has a many-to-one
relationship with the _media_ and tracks the history of moderation decisions
made for the media, including explanatory notes from moderators. It is not
possible to use `LogEntry`, like the project plan suggests to do, because
`LogEntry`'s `object_id` column is not indexed, and querying it to find all the
changes to all content reports for a given work would not scale.

This table anticipates additional abilities for moderators in the future
including reversing previous decisions (currently impossible, but needed if
users and especially creators can contest decisions) or explicitly marking works
as "not sensitive" (for example, if the work was only marked sensitive because
of erroneous sensitive text detection). Right now the data model and approach to
sensitivity and deindexing don't make these possible. It is outside the scope of
this project to add those features, but this new table, especially its `action`
column, is intentionally flexible to allow for these kinds of things in the
future. This is also why it isn't just a new `explanation` column on the content
report models: because we want to preserve a _record_ of moderation decisions in
chronological order, and describes the progressive changes of a work's
sensitivity designation (or de-indexing). It also separates the moderation
decision (and metadata) from the report, which has its own important metadata
that should not be confused with the moderation decision metadata.

Additional, the "Bulk moderation actions" implementation plan that is also part
of this project would have a good use case for this, with separate action types.
When moderating all works from a particular creator, for example, we wouldn't
need to generate reports for each of the works and action them, just a single
`ModerationDecision` for each work with an appropriate action and consequence.
This avoids need to create "fabricated" reports for bulk moderation actions that
wouldn't have reports in the first place. _This is just a suggested additional
use case and is not a specific implementation detail for that plan. The actual
plan can and probably will have additional considerations beyond this._

It will have the following columns:

- `id` - basic auto-incrementing id
- `created_on` - the date the moderation decision was created, in other words,
  the date the decision was made
  - Provided by `OpenLedgerModel`
- `moderator_id` - a foreign key relationship with moderator who made the
  decision
- `media_identifier` - a one-to-one relationship to the media the decision is
  related to
  - Because deindexing media removes them from the API database, this needs to
    be a non-constrained column, so not a foreign key, just an indexed
    _non-unique_ UUID column
- `explanation` - moderator notes explaining the decision; optional
- `action` - slug column of the action taken
  - `confirmed_sensitive` (marked a work as sensitive)
  - `deindexed_copyright` (deindexed the work from Openverse search due to
    copyright)
  - `deindexed_sensitive` (deindexed the work from Openverse search due to
    sensitivity)
  - `rejected_reports` (the reviewed reports were rejected)
  - `duplicate_reports` (the reviewed reports were duplicates, in other words,
    re-reports that did not result in deindexing but were also accurate, for
    example, re-reports of a sensitive work that add information regarding
    sensitivity but do not require deindexing)

Additionally, the report models will be expanded with an additional nullable
column, `decision_id` that ties the report to a specific moderation decision. A
single moderation decision can happen as a result of multiple pending reports,
so this facilitates the many-to-one relationship between a report and the
moderation decision. See
[the moderation view section below for additional information regarding this](#media-moderation-view).

There will not be a new admin view for `ModerationDecision`. Instead, moderation
decisions will
[show up on an individual media item's admin description page](#media-moderation-view).
The only part of a `ModerationDecision` moderators can manually interact with is
the explanation on the decision. Everything else is handled by the report and
media model admins.

```{tip}
The `action` slugs can be context sensitive, meaning they can take into account
previous moderation decisions to give better descriptions of what happened. These
must be selected automatically based on the history of the media and its reports.
Examples of potential future actions are:
* `reversed_sensitive`, for reversing a sensitivity designation from a work previously
  moderated as sensitive
* `ignore_sensitive_text`, for marking a work to be ignored by sensitive text filtering
* `reversed_deindex`, for reversing a deindex decision of a work
* `submitted_metadata_correction`, for some future magical feature where we allow users
  to submit suggested fixes to the metadata of a work

Again, these are purely hypothetical. They're just meant as examples to drive home the
_idea_ behind the action column. For now we will only implement the five actions listed
in the columns list above.
```

##### Deprecating and removing report status

A final critical aspect of the introduction of `ModerationDecision` is that it
deprecates report status.

Originally I sought to keep the report status and use the moderation decision
"action" to record additional information. However, @krysal pointed out that the
report status was fully duplicated without any additional information recorded
in it. In fact, attempting to maintain the report status made things more
complicated, because it was impossible to disambiguate between different "no
action" statuses on reports, even though the moderation decision action does do
so. We would always have to refer back to the moderation decision to get precise
information about a report anyway, so the report status became effectively
useless.

Therefore, we will deprecate and them remove the report status in favour of
treating reports only in two states: pending and reviewed. The report state is
deduced from whether `decision_id` is populated for a report. To do this, we
will need to back fill moderation decisions for all existing reports. Luckily,
the total number of actioned reports in production is low, so this backfill can
happen quickly. We will follow
[the process for zero-downtime data transformations described here](/general/zero_downtime_database_management.md#django-management-command-based-data-transformations)
and use a management command to do the following, after we have completed the
work to add all new functionality to the Django admin:

For each report where status is not `pending` and where `decision_id` is empty,
create a new moderation decision with the following:

- `moderator_id` set to the `opener` django admin user
- `action` set to the relevant action based on the report status and reason:
  - For any report reason with a status `mature_filtered`, set the action to
    `confirmed_sensitive`
  - For any report reason with a status `no_action`, set the action to
    `rejected_reports`
  - For `mature` or `other` reports with a status `deindexed`, set the action to
    `deindexed_sensitive`
    - There is no reliable way to tell if a report with `other` reason that led
      to deindexing was for sensitivity or copyright, so we'll just assume
      sensitivity because it is a safer assumption than copyright
  - For `dmca` reports with a status `deindexed`, set the action to
    `deindexed_copyright`
- `explanation` set to the following text to indicate it is a backfilled record:
  `__backfilled_from_report_status`
- `decision_id` on the report to the new moderation decision

After the backfill is complete, we will drop `status` from the reports.

Because we are not currently doing active moderation, we won't do anything to
maintain the `status` column between when we add the moderation decision and
when we remove the status column. Any moderation that needs to happen during the
implementation of this work will always result in a valid end state. Either the
moderation decision will not yet exist, and so the report will have a null
`decision_id` and will get included in the above backfill logic; or, the
moderation decision will exist, the status will be left at pending, but
`decision_id` will not be empty, and so the backfill will ignore it.

At the end of this process, we will drop the status column from the report
tables and all actioned reports, regardless of whether they were handled by the
backfill or happened after the moderation decision functionality was introduced
and available, will correctly have a `decision_id` pointing to a moderation
decision that mirrors whatever the status of the report would have been, either
based on the backfill logic or based on the new workflow introduced by this
plan.

#### Table view improvements

We will scrap the existing reports view. Instead of showing a list of reports,
we'll show a list of reported media, sorted by the total number of pending
reports, and then by the age of the oldest pending report. This will have the
effect of sorting re-reported works to the top of the list, under the assumption
that a work with multiple pending reports is probably higher priority, because a
decision to report it was taken multiple times. By default, we will only show
works with "pending" reports (reports where `decision_id = NULL`). This creates
a queue to work through progressively, from top to bottom. Remove any manual
sorting options for now. We can add those back if we get feedback that
moderators want them, but for now they just clutter and confuse the interface,
and make the foundational feature more complex.

#### Media moderation view

##### Information presentation

Clicking on a single reported media object should show the following:

- The details of the reported media:
  - title
  - description
  - tags
  - the work itself, in other words, the viewable image or the playable audio
  - whether sensitive text detection thought it had sensitive text
  - provider/source
  - links to foreign landing url and Openverse.org page for the work
- A chronological list of all moderation decisions for the work
- A chronological list of all reports for the work
  - Include at least the following columns: description, reason, date

The idea here is that the "report view" is not focused on taking an action for a
single _report_, but rather showing all relevant information for a single work
to make a moderation decision on the work, based on all pending and historical
reports.

We could take two approaches for this view: either create a brand new view or
build this into the media view itself. My preference and recommendation is the
latter, because while it creates complexity in the media admin view, that view
doesn't currently have much of a purpose anyway, and if we're making it possible
to view all the metadata for a work, we might as well take advantage of the
existing admin view for media items that already has some of that built into it.
I'll cover more details about how we'll accomplish this in the step-by-step.

##### Actions

To understand the rationale in this section, keep in mind that there are
currently three report types (sensitive, DMCA, and "other"), and that users can
select any of these. There is little guidance beyond the report type labels
themselves to indicate to users which one to select. This means that reports of
different types get mixed up, and especially the "other" type ends up with
reports that would have been better suited as sensitive or DMCA reports. This
means there is no coherent way to handle "all pending reports". A previous
version of this implementation plan attempted to do that, but it's far too
complex and has so many edge cases, that it's _easier_ to handle a set number of
reports at a time, selected by the moderator.

In the future, we could try to include links that open tables to show all
moderation decisions for works by the same creator, etc, in case there is useful
information, particularly for identifying potential bulk moderation actions.
These kinds of additional views are out of scope for this current project,
however.

Each pending report should have a checkbox allowing it to be selected for
actioning. If there is only a single pending report, it should be automatically
selected when the form loads.

The expanded view should have the following context-sensitive actions:

- "Mark sensitive: mark the work as sensitive based on selected reports"
  - Only available if a work is not already marked sensitive
  - `confirmed_sensitive` action
- "Deindex sensitive: entirely exclude the work from Openverse due to
  sensitivity based on selected reports"
  - There are no real conditions for this because deindexing can happen for
    works that are or are not marked sensitive
  - `deindexed_sensitive` action
- "Deindex copyright: entirely exclude the work from Openverse due to copyright
  based on selected reports"
  - `deindexed_copyright`
- "Reject reports: take no action and mark all selected reports as reviewed"
  - `rejected_reports` action
- "Mark selected reports duplicates: take no action and mark all selected
  reports as duplicates"
  - `duplicate_reports` action

Each of these actions should create a single `ModerationDecision` with
explanation, action, moderator ID, and so forth populated. The admin view should
update the selected reports to set the `decision_id` to point to the new
moderation decision. All actions rely on the selected set of reports and should
not modify any other reports.

Remove all logic from the report models `save` methods that bulk actions
reports. That approach will no longer be valid and we will operate on specific
reports individually following the `ModerationDecision`.

##### Multiple-decision prevention (soft-locking)

To prevent multiple moderators unintentionally looking at the same report, we'll
track works currently in moderation whenever a moderator loads the view using a
soft-lock approach. The lock on the work should automatically expire after five
minutes. It is a "soft" lock because we won't use it to _lock_ anything
explicitly, but only to make moderators aware that someone else is already
looking at that work. The lock will be in Redis as a set of work identifiers.
We'll need to use the
[sorted set approach described in the project proposal](/projects/proposals/trust_and_safety/content_report_moderation/20230411-project_proposal_content_report_moderation.md#redis-based-cache-invalidation-strategy)
to use for caching in order to implement a set with expiring members. To reword
that section for this completely different use case:

> Redis does not support expiring set elements, but we can use a sorted set
> where the score is the unix timestamp of the expiration time, in other words,
> "now plus five minutes". Whenever retrieving the list of locked works, we'll
> remove all entries that have scores less than the current unix timestamp, and
> then use the remaining list of identifiers as the list of locked
> works[^workaround-kudos].

[^workaround-kudos]:
    Kudos to
    [this old Google Groups discussion](https://web.archive.org/web/20211205091916/https://groups.google.com/g/redis-db/c/rXXMCLNkNSs)
    for the sorted set workaround.

We'll maintain an additional value per-moderator to track their currently viewed
page. Whenever the moderator enters a work, we'll add it to the sorted set
described above and set `currently_moderating:<moderator_id>` to the work
identifier. When the moderator navigates back to the table view, we'll delete
`currently_moderating:<moderator_id>`, but only after removing the identifier
that was in that key from sorted set. The per-moderator key should have the same
TTL as the sorted set, five minutes, in case the moderator just closes their
browser rather than navigating back to the table view.

We'll implement this list at this stage, but it will also be used to annotate
works currently in moderation on the table view. When rendering the table view,
retrieve a list of works in moderation by retrieving identifiers from the scored
set that have a score higher than the current unix timestamp. For each work in
the table, check if it's identifier is in the list of in-moderation identifiers,
and if it is, render the table line for that work with a light orange
background. Add a key to the page to explain what the light orange background
indicates.

#### Moderator preferences

Finally, for moderation improvements we want to make it possible to blur images
by default in the media admin view. However, we also need to make it so
individual users can disable blurring (this was a request from folks who do
moderation professionally). We'll use exactly the same approach to blurring as
we do on the frontend (css blur function). To manage the preferences, we'll
subclass the `User` model and add a new column called `preferences`, which will
be a JSON blob. Then we'll create a new model admin for `User` called "My
preferences" that has a single option to toggle a new preference into the
`preferences` JSON, `moderator.blur_images`. When the setting is undefined, it
should be understood as `true`, meaning images will be blurred.

### Access control

Access control is the simplest part of this work, mostly because Django has
excellent tools for this already.

We will use
[Django's user group](https://docs.djangoproject.com/en/5.0/topics/auth/default/#groups)
to create a new "Content Moderator" user group. This user group will have only
the following permissions:

- read and update content reports
- read related models like works, moderation decisions, and the mature and
  deleted models for each media type

Moderator users will not be allowed to delete anything and will only be allowed
to create moderation decisions, though only indirectly through taking actions on
reports. This includes not being able to create reports via the admin. If they
need to do this, they can create the report from the Openverse.org website. We
will leave the general create ability in for the sake of local testing with the
API, so if it turns out moderators need to be able to create reports from the
Django admin, we can easily enable that. In order to minimise clutter and
potential mistakes, it's best to minimise the possible actions.

Openverse maintainers will create new user accounts for moderator users as
needed. The maintainer should assign the new user to the "Content Moderator"
group.

To enable these features, we'll need to register the `django.contrib.auth`
`User` and `Group` models to the provided admin views for each:

```py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group


admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
```

Finally, to enable moderators to get past Cloudflare Access Control, we will
have a new GitHub team, `WordPress/openverse-content-moderators` that will allow
access to Django admin, similar to how `WordPress/openverse-maintainers` allows
access currently. This will require a small change to the Terraform `access`
module to allow dynamically adding additional GitHub teams for a given service.
This can follow a pattern similar to the emails, where we have a "globally
allowed" email list, with individual applications listing one-off access for
specific emails. For example:

```diff
diff --git a/modules/concrete/access/main.tf b/modules/concrete/access/main.tf
index e53c5da..3c2e4fb 100644
--- a/modules/concrete/access/main.tf
+++ b/modules/concrete/access/main.tf
@@ -24,6 +24,7 @@ locals {
     django-admin = {
       domain       = "api.openverse.engineering/admin"
       allow-emails = []
+      allow-teams = ["Openverse Content Moderators"]
     }
     django-admin-production-subdomain = {
       domain       = "api-production.openverse.engineering/admin"
@@ -70,7 +71,7 @@ resource "cloudflare_access_policy" "allow" {
       identity_provider_id = data.cloudflare_access_identity_provider.github_login.id
       name                 = "WordPress"
       # Note that this MUST use the team's "display" name, not the slug!
-      teams = ["Openverse Maintainers"]
+      teams = concat(["Openverse Maintainers"], try(local.applications[each.key].allow-teams, []))
     }
   }
 }
```

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

By the end of this implementation plan's implementation:

- Openverse maintainers will be able to create moderator users and have them
  access Django admin with restricted permissions
- Moderators will be able to make content moderation decisions based on user
  reports via Django admin

## Step-by-step plan

<!--
List the ordered steps of the plan in the form of imperative-tone issue titles.

The goal of this section is to give a high-level view of the order of implementation any relationships like
blockages or other dependencies that exist between steps of the plan. Link each step to the step description
in the following section.

If special deployments are required between steps, explicitly note them here. Additionally, highlight key
milestones like when a feature flag could be made available in a particular environment.
-->

We'll implement this plan in the following order. I've noted which items block
others or are non-blocking.

1. Preliminary access control (somewhat blocking `ModerationDecision`)
2. Add user preferences admin view (non-blocking)
3. Report table view improvements (non-blocking)
4. `ModerationDecision` (blocking media moderation view)
5. Media moderation view
   1. The view itself
   2. The actions
   3. The moderation soft-lock
6. Finalise access control
7. Backfill `ModerationDecision` and drop report `status`

## Step details

<!--
Describe all of the implementation steps listed in the "step-by-step plan" in detail.

For each step description, ensure the heading includes an obvious reference to the step as described in the
"step-by-step plan" section above.
-->

### 1. Preliminary access control

[See "Access control" for rationale](#access-control)

- Add `User` and `Group` admin views
- Create the "Content Moderator" group and add basic preliminary permissions to
  read and update content reports and media items
  - We'll expand these later on in the implementation as needed

### 2. Add user preferences admin view

[See "Moderator preferences" for rationale](#moderator-preferences)

- Sub-class the `User` model to create `OpenverseUser` and add a new binary JSON
  column, `preferences`
- Create a new admin view for `OpenverseUser` called `User preferences` that has
  only a single checkbox control to turn on and off the `moderator.blur_images`
  setting

### 3. Table view improvements

[See "Table view improvements" for rationale](#table-view-improvements)

- Create a new view based on the media object default model view but sort media
  by pending report count and the oldest report's age
- Exclude media items that have no reports
- Filter to only show media with pending reports by default, but allow showing
  all reported media

### 4. `ModerationDecision`

[See "`ModerationDecision`" for rationale](#moderationdecision)

- Create the new `ModerationDecision` models
  - Create an `AbstractModerationDecision` for each media type
- Add new `decision_id` column to report models
- Remove bulk report updates from the report models' `save` methods

### 5. Media moderation view

[See "Media moderation view" for rationale](#media-moderation-view)

This is in three separate issues:

1. Create a new media view to replace the existing view

   - Use the basic model admin but with only "view" settings for all model
     fields
   - We'll need to expand the rendered fields to include things like the
     rendered (interactive) thumbnail and audio player
   - It should display (and not allow editing) the following:
     - title
     - description
     - tags
     - creator with link to creator landing page on source (if applicable)
     - source/provider
     - the work's thumbnail itself, blurred if the moderator has not turned off
       blurring
       - clicking on the thumbnail should un-blur the work
     - if an audio work, show the basic HTML5 audio player
     - links to the foreign landing URL and Openverse.org page of the work
     - whether sensitive text detection matched on the work
       - check if the work is in the filtered index, if not, then it has
         sensitive text
   - Show chronolical lists of all moderation decisions and reports for the work
     - Do this using an
       [`TabularInline`](https://docs.djangoproject.com/en/4.2/ref/contrib/admin/#inlinemodeladmin-objects)
       for each

2. If the user viewing the page has content moderation permissions, add the
   relevant actions for the work based on it

   - See the
     [relevant overview section for described actions](#media-moderation-view)
     and the conditions for when to show them
   - Add an free text form field "explanation" to collect for the moderation
     decision

3. Implement the lock on works to prevent duplicate decisions
   - When loading the moderation view, add the work's identifier to the sorted
     set `in_moderation` with a score of "now + five minutes" as a unix
     timestamp. Additionally, set `currently_moderating:<moderator id>` to the
     work identifier with a TTL of five minutes.
   - When loading the moderation view, check `in_moderation` (before setting
     anything in there) for the work identifier. If it is in there, add a
     message when the page loads to alert the moderator that someone else is
     also looking at the work. No other changes to the page are necessary.
   - When loading the table view, check the `in_moderation` sorted set. Retrieve
     everything with a score higher than the current unix timestamp. Eject
     everything else from the sorted set _in Redis_. This will be our periodic
     cleanup of the list to mimic expiration and prevent it from growing
     indefinitely.
   - For each line of the table view, render the line with a light orange
     background if the work is in the `in_moderation` list.
   - Add copy to the table view to explain what the light orange background
     indicates (either as a message or as a new sidebar element where the
     "filters" typically are).

### 6. Finalise access control

[See "Access control" for rationale](#access-control)

- Create the new GitHub team `WordPress/openverse-content-moderators`
- Add that team to the list of teams allowed access to production Django admin
  in the Terraform access module
  - Preferably, only stage this change for once we're ready to actually give
    people access and test this
- Add the necessary permissions to the "Content Moderator" group in Django admin
  so that content moderators can only view the new report table view, the
  expanded individual work view with the moderation and report chronology, and
  can issue moderation decisions on that page.

### 7. Backfill `ModerationDecision` and drop report `status`

[See "Deprecating and removing report status" for rationale](#deprecating-and-removing-report-status)

- Create the management command to backfill `ModerationDecision`
- Run the management command in production using AWS SSM to trigger the command
  on one of the existing tasks (`just ssm-connect` in the
  `openverse-infrastructure` repository)
  - It would be good not to deploy to production while this runs to avoid
    needing to re-start the command, but the command should be idempotent and
    transactional anyway, so if it crashes or gets restarted, there is no risk
    to our data
- Drop the `status` column from the report tables
  - These tables are very small and rarely written to or read from, so there is
    no concern about locking the table during this migration

## Dependencies

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

Small infrastructure change to add new GitHub team and allow access through
Cloudflare Access.

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

Slightly related to the bulk moderation implementation plan, which will build
off of some of this work, in particular the table view, but also includes other
things.

## Design

<!-- Note any design requirements for this plan. -->

There are no design requirements for this. We'll stick with the basic Django
admin style for everything and try to stay as minimalistic as possible in order
to get this done with the least complexity. We can iterate on the visuals to
help improve the moderator workflow once it's actually possible to effectively
moderate.

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

Nothing here is hard to roll back, aside from adding the new content report
column with an nullable foreign key to the new moderation decision model. This
is fairly low risk. Everything else is either purely in code with no
dependencies or can be easily dropped (the new moderation decision table).

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->

- [Django authentication documentation](https://docs.djangoproject.com/en/5.0/topics/auth/default/#groups)
- [Django admin documentation](https://docs.djangoproject.com/en/4.2/ref/contrib/admin/#inlinemodeladmin-objects)
