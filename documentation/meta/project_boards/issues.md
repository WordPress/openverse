# Issues project: Openverse Backlog

The [Openverse Backlog](https://github.com/orgs/WordPress/projects/75) project
board tracks all issues through their lifecycle, as they move from creation to
completion. This board does not track any pull requests, so all workflows for
this board are tied to events occurring for issues.

## Event automations

### Issue is created

If a new issue is created in the
[`WordPress/openverse`](https://github.com/WordPress/openverse/) repository, it
is automatically added to the project board provided it does not contain any
label with the text "project".

```{note}
This workflow also sets the Priority custom field in the issue so that we can
create a kanban-board view based on priority.
```

- [Custom workflow](https://github.com/WordPress/openverse/blob/main/.github/workflows/new_issues.yml)

### Issue is closed

If an issue is closed, it moves into the "✅ Done" column. This is not affected
by whether it was closed as resolved or as discarded.

- [Built-in workflow](https://github.com/orgs/WordPress/projects/75/workflows/6899392)

### Issue is reopened

If a previously closed issue is reopened, it goes back to the "📋 Backlog"
column. That is because it will need to be re-prioritized alongside other
ongoing work and moved to "📅 To do" when it can be worked on again.

- [Built-in workflow](https://github.com/orgs/WordPress/projects/75/workflows/8193212)

### Issue is added to the project

The status of this issue will be set to "📋 Backlog" and thus, it will be
included under the "📋 Backlog" column.

- [Built-in workflow](https://github.com/orgs/WordPress/projects/75/workflows/6899490)

### Issue is closed and inactive

If an issue is closed, and has not been updated in 8 days, it will automatically
be archived from the project board. This ensures that the board is cleared in
time for the weekly development chat.

- [Built-in workflow](https://github.com/orgs/WordPress/projects/75/workflows/8222891)
