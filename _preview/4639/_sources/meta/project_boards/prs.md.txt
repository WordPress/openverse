# PR project: Openverse PRs

The [Openverse PRs](https://github.com/orgs/WordPress/projects/98) project board
tracks all PRs through their lifecycle, as they move from creation to merge (or
closure). This board does not track any issues, so all workflows for this board
are tied to events occurring for pull requests.

```{note}
GitHub treats PRs as a subcategory of issues, all issue related automations have
PR counterparts but not vice versa.
```

```{caution}
The PRs board is currently private. It may be made public in the future.
```

## Event automations

```{note}
For all below events, "custom workflow" refers to
[`pr_automations.yml`](https://github.com/WordPress/openverse/blob/main/.github/workflows/pr_automations.yml)
which is also
[synced to the `WordPress/openverse-infrastructure` repo](https://github.com/WordPress/openverse-infrastructure/blob/main/.github/workflows/pr_automations.yml).
```

### PR is opened/reopened

If a new PR is created in the
[`WordPress/openverse`](https://github.com/WordPress/openverse/) and
[`WordPress/openverse-infrastructure`](https://github.com/WordPress/openverse-infrastructure/)
repositories, it is automatically added to the project board.

- If the PR is a draft, it is automatically added to the "🚧 Draft" column.
- Else if the PR requires changes, it is automatically added to the "🔁 Changes
  Requested" column.
- Else if the PR has the requisite approvals, it is automatically added to the
  "✅ Approved" column.
- If the PR has one approval, it is automatically added to the "1️⃣ Needs 1
  Review" column.
- Else it is automatically added to the "2️⃣ Needs 2 Reviews" column.

If the PR is linked to an issue, the linked issue moves to the "🏗️ In Progress"
column.

This is handled by a custom workflow. The following built-in workflows for this
task have been deactivated:

- Auto-add to project (won't trigger our workflow)
- Item added to project (cannot classify PRs by state and reviews)
- Item reopened (cannot classify PRs by state and reviews)

### PR is edited

If the PR is linked to an issue, the linked issue moves to the "🏗️ In Progress"
column.

This is handled by a custom workflow.

### PR is converted to draft

When the PR is converted to draft, it is automatically moved to the "🚧 Draft"
column.

This is handled by a custom workflow.

### PR is ready for review

When the PR is ready for review, it is automatically moved to the appropriate
column out of "1️⃣ Needs 1 Review", "2️⃣ Needs 2 Reviews", "✅ Approved", or "🔁
Changes Requested".

This is handled by a custom workflow.

### PR has requested changes

If the PR has requested changes, it is automatically added to the "🔁 Changes
Requested" column.

This is handled by a custom workflow.

### PR has required approvals

If the PR has required approvals, it is automatically added to the "✅ Approved"
column.

This is handled by a custom workflow.

### PR is merged

If a PR is merged, it moves into the "🤝 Merged" column.

This is handled by a
[built-in workflow](https://github.com/orgs/WordPress/projects/98/workflows/8656665).

### PR is closed

If a PR is closed without being merged, it moves into the "🚫 Closed" column. If
the PR was linked to an issue, the linked issue moves back to the "📋 Backlog"
column.

This is handled by a combination of a
[built-in workflow](https://github.com/orgs/WordPress/projects/98/workflows/8656664)
and a custom workflow.

### PR is closed and inactive

If a PR is closed (includes merged) and has not been updated in two weeks, it
will automatically be archived from the project board. This is different from
the archival threshold of the issues board (8 days).

- [Built-in workflow](https://github.com/orgs/WordPress/projects/98/workflows/8674454)
