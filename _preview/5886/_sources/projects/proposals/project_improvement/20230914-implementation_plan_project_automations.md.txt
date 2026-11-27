# 2023-09-14 Implementation plan: Project automations

**Author**: @dhruvkb

## Reviewers

- [x] @AetherUnbound
- [x] @obulat

## Project links

- [Project Thread](https://github.com/WordPress/openverse/issues/1931)
- [Project Proposal](/projects/proposals/project_improvement/20230913-project_proposal_project_improvements.md)

## Overview

This is the implementation plan describing new automations for the project
board. More information about the project board and existing automations can be
found in our [documentation](/meta/project_boards/index.md).

## Historical context

The new project board was created as a successor to our original project boards,
that were "classic" GitHub Projects.

- [Openverse](https://github.com/orgs/WordPress/projects/3)
- [Openverse PRs](https://github.com/orgs/WordPress/projects/8)

```{note}
These classic project boards have been closed. They are no longer updated, nor
referred to in any discussions.
```

These boards were highly automated. A number of automations related to these
boards were deleted ([PR](https://github.com/WordPress/openverse/pull/2338))
when they were closed. Those automations can serve as inspiration for their
reboots for the new project board.

## To-do

The complete work of automating our boards can be broadly classified under three
categories.

### General improvements to boards

1. Normalise emoji usage

   The backlog board uses an emoji for each column. None of the other boards do.
   Personally I appreciate them and would like all boards to use them but
   wouldn't mind dropping them from the backlog board for consistency's sake.

   **For emoji:**

   - @dhruvkb
   - @AetherUnbound
   - &lt;add your name here&gt;

   **Against emoji:**

   - &lt;add your name here&gt;

2. Column changes

   - **Issues**
     - Create new column "🗑️ Discarded" for issues that were closed without
       resolution (like label "⛔️ status: discarded").
   - **PRs**
     - Split "Needs Review" into two columns based on their number of existing
       reviews.
       - 2️⃣ Needs 2 Reviews (no reviews yet)
       - 1️⃣ Needs 1 Review (one approval, near finish line)
     - Create new column "🗑️ Discarded" for PRs that were closed without merge.
     - Rename "Merged" to "✅ Done" for consistency with issues board.

### Improvements to existing automations

1. [Issues/Issue is created](/meta/project_boards/issues.md#issue-is-openedreopened)
   and
   [Issues/Issue is added to the project](/meta/project_boards/issues.md#issue-is-openedreopened)

   The issue should be added to the project board under the appropriate column,
   "📋 Backlog" or "⛔ Blocked" depending on the issue labels.

2. [Issues/Issue is closed](/meta/project_boards/issues.md#issue-is-closed)

   The issue should be moved to the "✅ Done" column only if it was resolved. If
   it was closed as discarded, it should be moved to a new "🗑️ Discarded"
   column.

   The built-in workflow will have to be replaced by a custom one that looks at
   the `state_reason` field inside the issue payload of the `closed` activity of
   the
   [`issues` event](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#issues).

3. [Issues/Issue is closed and inactive](/meta/project_boards/issues.md#issue-is-closed-and-inactive)

   The current system means that issues are archived one by one as they become
   inactive and with an 8 day cadence, this will slowly drift out of sync with
   the weekly development chat.

   Archiving should be performed by a custom scheduled workflow that archives
   all items in the "✅ Done" and "🗑️ Discarded" columns weekly (preferably
   immediately after the chat).

4. [PRs/PR is created](/meta/project_boards/prs.md#pr-is-openedreopened) and
   [PRs/PR is added to project](/meta/project_boards/prs.md#pr-is-openedreopened)

   The PR should be added to the project board under the appropriate column, "In
   Progress" or "Needs &lt;x&gt; Review(s)" depending on the PR's draft or
   ready-for-review state and the number of existing reviews.

5. PRs/PR is [closed](/meta/project_boards/prs.md#pr-is-closed) or
   [merged](/meta/project_boards/prs.md#pr-is-merged)

   The PR should be moved to the "✅ Done" column only if it was merged. If it
   was closed without merge, it should be moved to a new "🗑️ Discarded" column.

   This can be implemented by updating built-in workflows.

### Restoration of previous automations

1. Issues/Issue is connected to PR

   When an issue is
   [connected](https://docs.github.com/en/rest/overview/issue-event-types?apiVersion=2022-11-28#connected)
   to a PR, the issue should move from "📋 Backlog" or "📅 To do" to the "🏗 In
   Progress" column. If the issue is labeled as "⛔ status: blocked", that label
   should be dropped.

   Unfortunately, the `connected` event does not trigger workflows. So this can
   be implemented using a combination of multiple workflows.

   - scheduled workflow
   - [`pull_request` event](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request)
     - created
     - edited

2. Issues/PR linked to issue is closed without merge

   When the PR for an issue in "🏗️ In Progress" is closed without merge, the
   issue should go back to the "📅 To do" column.

   The `closed` activity in the
   [`pull_request` event](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request)
   can trigger workflows to do this.

### Creation of new automations

1. Issues/Issue is relabeled

   When an issue's labels change, it should automatically move to the right
   column.

   - issues labeled as "⛔ status: blocked" ⟹ Move into "⛔ Blocked" column
   - issues unlabeled as "⛔ status: blocked" ⟹ Move into "📋 Backlog" column

   Both `labeled` and `unlabeled` activities in the
   [`issues` event](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#issues)
   can trigger workflows to do this.

   The priority field in the project board issues should also be synced to the
   priority label using the same workflow. Additionally, critical issues can
   directly be added to the "📅 To do" column instead of the "📋 Backlog" column
   to prioritise their resolution.

2. Issues/Issue is assigned

   An assigned issue in "📋 Backlog" must be moved into "📅 To do". The opposite
   event, i.e. moving unassigned issues from "📅 To do" to "📋 Backlog" should
   not happen.

   The `assigned` activity in the
   [`issues` event](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#issues)
   can trigger workflows to do this.

3. PRs/PR state is changed

   When a PR is drafted or made ready for review, it should be relocated to the
   right column.

   - PR is converted to draft ⟹ Move into "In Progress" column
   - PR is ready for review ⟹ Move into the "Needs &lt;x&gt; Review(s)" column

   Both `converted_to_draft` and `ready_for_review` activities in the
   [`pull_request` event](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request)
   can trigger workflows to do this.

## Modifications

Each of these automations performs one of these modifications to the cards.

- add cards
- move cards between columns
- archive cards

## Plan

Here we define workflows based on the above-mentioned improvements. Each
workflow should have multiple steps that are controlled based on two params
`github.event_name` and `github.event.action`.

### Issues ([`issues`](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#issues))

Activity types:

- `opened`

  Add to project board. Perform same label-related steps as the `labeled`
  activity.

- `closed`

  Check `state_reason` field in payload and move to "✅ Done" or "🗑️ Discarded"
  column.

- `assigned`

  If in "📋 Backlog", move to "📅 To do". Else leave as is.

- `labeled`

  If "⛔️ status:blocked" in existing labels, move to “⛔ Blocked” column. Else
  if "🟥 priority: critical" in existing labels, move to "📅 To do" column. Else
  move to "📋 Backlog" column. Sync priority label to priority field.

- `unlabeled`

  If the "⛔️ status:blocked" label is removed, move to "📋 Backlog" column.

### PR ([`pull_request`](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request))

Activity types:

- `opened`

  Add to the project board. Perform the same state related steps as the
  `converted_to_draft` and `ready_for_review` activities.

- `edited`

  When a PR is edited, it can be linked to an issue via the description. If the
  PR is linked to an issue, move the issue to "🏗️ In Progress" column.

- `closed`

  Check `github.event.pull_request.merged` field in payload and move to "✅
  Done" or "🗑️ Discarded" column.

- `converted_to_draft`

  Move to the "🏗 In Progress" column.

- `ready_for_review`

  Perform the same state related steps as the `pull_request_review` event.

### PR review ([`pull_request_review`](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request_review))

Check all submitted reviews. If a PR has at least one "CHANGES_REQUESTED"
review, do nothing (the built-in action will handle this). If the PR has one
approval, move to the "1️⃣ Needs 1 review" column. If the PR has no approvals
yet, move to the "2️⃣ Needs 2 reviews" column.

### Scheduled

Schedules:

- weekly

  Archive "✅ Done" and "🗑️ Discarded" columns.

- daily

  Identify linked issues and move them to "🏗️ In Progress" column.
