# 2023-12-08 Implementation Plan: Django admin tools and access control for moderators

**Author**: @sarayourfriend

## Reviewers

- [ ] @krysal
- [ ] @stacimc

## Project links

- [Project thread](https://github.com/WordPress/openverse/issues/383)
- [Relevant project proposal section](/projects/proposals/trust_and_safety/content_report_moderation/20230411-project_proposal_content_report_moderation.html#volunteer-moderator-django-admin-tools-and-access-control-requirement-2)

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
  - `deindexed` (deindexed the work from Openverse search)
  - `rejected_report` (marked pending report(s) `no_action` when the work is not
    already marked sensitive)
  - `duplicate` (marked pending report(s) `no_action` when the work is already
    marked sensitive; i.e., a re-report that did not result in deindexing)

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
_idea_ behind the action column. For now we will only implement the four actions listed
in the columns list above.
```

#### Table view improvements

We will scrap the existing report table. Instead of showing a list of reports,
we'll show a list of reported media, sorted by the total number of pending
reports, and then by the age of the oldest pending report. This will have the
effect of sorting re-reported works to the top of the list, under the assumption
that a work with multiple pending reports is probably higher priority, because a
decision to report it was taken multiple times. By default, we will only show
works with "pending" reports, with the option to include other statuses if
moderators choose. This creates a queue to work through progressively, from top
to bottom. Remove any manual sorting options for now. We can add those back if
we get feedback that moderators want them, but for now they just clutter and
confuse the interface, and make the foundational feature more complex.

#### Media moderation view

Clicking on single report should show the following:

- The details of the reported media:
  - title
  - description
  - tags
  - the work itself
  - whether sensitive text detection thought it had sensitive text
  - provider/source
  - links to foreign landing url and Openverse.org page for the work
- A chronological list of all moderation decisions for the work
- A chronological list of all reports for the work regardless of status

The idea here is that the report view is not focused on taking an action for a
single _report_, but rather showing all relevant information for a single work
to make a moderation decision based on all pending reports for a work and
historical moderation decisions for the work (if any).

In the future, we could try to include links that open tables to show all
moderation decisions for works by the same creator, etc, in case there is useful
information, particularly for identifying potential bulk moderation actions.
These kinds of additional views are out of scope for this current project,
however.

The expanded view should have the following context-sensitive actions:

- "Mark sensitive: confirm a sensitive content report and mark the work as
  sensitive"
  - Only available if a work is not already marked sensitive
  - `confirmed_sensitive` action
- "Deindex: entirely exclude the work from Openverse"
  - There are no real conditions for this because deindexing can happen for
    works that are or are not marked sensitive
  - `deindexed` action
- "Reject all pending reports: take no action and mark all pending reports for
  the work as reviewed"
  - Only available if a work is not already marked sensitive
  - `rejected_report` action
- "Mark all pending reports duplicates: take no action and mark all pending
  reports for the work as duplicates"
  - Only available if the work is already marked sensitive
  - `duplicate` action

Each of these actions should create a single `ModerationDecision` with
explanation, action, moderator ID, and so forth populated. The admin view should
bulk update the reports pending at the time of the decision to set the
`decision_id` to point to the new moderation decision. We'll need to make sure
to avoid any kind of race condition where between the moderator loading the
media moderation view and making a decision, a new report is made. We can do
this by adding the list of pending reports as a hidden form field to compare
with the list pulled when the form is saved. In the case that the lists do not
match (in other words, a new report was created between the time the form was
loaded and when it was saved), then reject the submission with a note saying
that a new report exists and should be included in the review.

We could take two approaches for this view: either create a brand new view or
build this into the media view itself. My preference and recommendation is the
latter, because while it creates complexity in the media admin view, that view
doesn't currently have much of a purpose anyway, and if we're making it possible
to view all the metadata for a work, we might as well take advantage of the
existing admin view for media items that already has some of that built into it.
I'll cover more details about how we'll accomplish this in the step-by-step.

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
6. Finalise access control

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

### 5. Media moderation view

[See "Media moderation view" for rationale](#media-moderation-view)

This is in two separate issues:

1. Create a new media view to replace the existing view

- Use the basic model admin but with only "view" settings for all model fields
- We'll need to expand the rendered fields to include things like the rendered
  (interactive) thumbnail and audio player
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
    - check if the work is in the filtered index, if not, then it has sensitive
      text
- Show chronolical lists of all moderation decisions and reports for the work
  - Do this using an
    [`TabularInline`](https://docs.djangoproject.com/en/4.2/ref/contrib/admin/#inlinemodeladmin-objects)
    for each

2. If the user viewing the page has content moderation permissions, add the
   relevant actions for the work based on it

- See the
  [relevant overview section for described actions](#media-moderation-view) and
  the conditions for when to show them
- Add an free text form field "explanation" to collect for the moderation
  decision
- For any action taken, we only need to update/save a single report with the new
  status. The `AbstractMediaReport` class already handles updating any other
  pending reports in it's `save` method without creating duplicate/conflicting
  mature or deleted media objects.
- For each of these actions, set the following new status:
  - `confirmed_sensitive` -> `mature_filtered`
  - `deindexed` -> `deindexed`
  - `rejected_report` or `duplicate` -> `no_action`
- Prevent the race condition described in the rational section for this step by
  setting a hidden form field with the list of pending report IDs at page load.
  Instead of erroring when that list does not match the list of pending reports
  at save, which would slow down the moderation workflow, just make sure that
  only those report IDs _at load_ are the ones that are modified. To do this,
  update the report `save` method to only bulk update reports _older_ than the
  one being saved. Then, in the admin action, only update the oldest report of
  the ones the moderator is known to have seen. The next time moderators come
  past the work they'll have the most recent decision to work off of and can
  action on the new report then.

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
