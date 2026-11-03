# Issues project: Openverse Backlog

The [Openverse Backlog](https://github.com/orgs/WordPress/projects/75) project
board tracks all issues through their lifecycle, as they move from creation to
completion. This board does not track any pull requests, so all workflows for
this board are tied to events occurring for issues.

## Event automations

```{note}
For all below events, "custom workflow" refers to
[`issue_automations.yml`](https://github.com/WordPress/openverse/blob/main/.github/workflows/issue_automations.yml)
which is also
[synced to the `WordPress/openverse-infrastructure` repo](https://github.com/WordPress/openverse-infrastructure/blob/main/.github/workflows/issue_automations.yml).
```

### Issue is opened/reopened

If a new issue is created in the
[`WordPress/openverse`](https://github.com/WordPress/openverse/) and
[`WordPress/openverse-infrastructure`](https://github.com/WordPress/openverse-infrastructure/)
repositories, it is automatically added to the project board provided it does
not contain the label "🧭 project: thread".

- If an issue has the "🟥 priority: critical" label, it is automatically added
  to the "📅 To Do" column.
- Else if an issue has the "⛔ status: blocked" label, it is automatically added
  to the "⛔ Blocked" column.
- Else it is automatically added to the "📋 Backlog" column.

When multiple conditions apply, the automation calculates the final destination
before moving the card, so critical priority takes precedence over blocked
status without an intermediate move.

```{note}
This workflow also sets the Priority custom field in the issue so that we can
create a kanban-board view based on priority.
```

This is handled by a custom workflow. The following built-in workflows for this
task have been deactivated:

- Auto-add to project (won't trigger our workflow, also does not set the
  "Priority" custom field)
- Item added to project (does not differentiate blocked vs unblocked issues)
- Item reopened (does not differentiate blocked vs unblocked issues)

### Issue is closed

If an issue is closed, it moves into the "✅ Done" column or the "🗑️ Discarded"
column based on whether it was completed or rejected.

This is handled by a custom workflow. The following built-in workflows for this
task have been deactivated:

- Item closed (does not differentiate completed vs rejected issues)

### Issue is assigned

When an issue is assigned to someone, it is automatically moved into the "🏗️ In
Progress" column.

This is handled by a custom workflow.

### Issue is labeled/unlabeled

If an issue is added the "⛔ status: blocked" label, it is automatically moved
into the "⛔ Blocked" column. If an issue is removed from the "⛔ status:
blocked" label, it is automatically moved into the "📋 Backlog" column.

This is handled by a custom workflow.

### Issue is closed and inactive

If an issue is closed, and has not been updated in 8 days, it will automatically
be archived from the project board. This ensures that the board is cleared in
time for the weekly development chat.

This is handled by a
[built-in workflow](https://github.com/orgs/WordPress/projects/75/workflows/8222891).
