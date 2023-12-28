# Project project: Openverse Project Tracker

The [Openverse Project Tracker](https://github.com/orgs/WordPress/projects/70)
project board tracks project tickets through their lifecycle, as they move from
not being started to being successful.

Project threads are issues, so all workflows for this board are tied to events
occurring for issues, however the issue status has slightly different
interpretation when the issue is a project thread.

## Event automations

### Thread is created

If a new issue is created with the label "🧭 project: thread", it is
automatically added to the project tracker project board.

- [Built-in workflow](https://github.com/orgs/WordPress/projects/70/workflows/6730708)

### Thread is closed

If a project thread is closed, it moves into the "Shipped" column. These
projects are considered shipped but not successful (yet).

- [Built-in workflow](https://github.com/orgs/WordPress/projects/70/workflows/6373102)

### Thread is added to the project

The status of the project thread will be "Not Started" and thus, it will be
included under the "Not Started" column.

- [Built-in workflow](https://github.com/orgs/WordPress/projects/70/workflows/6730724)
