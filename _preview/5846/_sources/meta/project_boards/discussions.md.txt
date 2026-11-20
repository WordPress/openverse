# Discussion project: Openverse Discussions

The [Openverse Discussions](https://github.com/orgs/WordPress/projects/79)
project board tracks project proposals and implementation plans through their
lifecycle, as they move from pending to accepted. This board tracks issues and
pull requests so it has workflows for both kinds of events.

## Event automations

### PR is created

If a new PR is created with either of the following labels, it is automatically
added to the project board.

- 🧭 project: implementation plan
- 🧭 project: proposal

- [Built-in workflow](https://github.com/orgs/WordPress/projects/79/workflows/8235206)

### Issue/PR is added to the project

The status of this issue/PR will be set to "Pending proposal" and thus, it will
be included under the "Pending proposal" column.

- [Built-in workflow](https://github.com/orgs/WordPress/projects/79/workflows/7503192)

### Issue/PR is closed/merged

If an issue/PR is closed, it moves into the "Accepted" column. This is not
affected by whether the issue was closed as resolved or as discarded or if the
PR was merged or closed without merge.

- [Built-in workflow (closed)](https://github.com/orgs/WordPress/projects/79/workflows/7304449)
- [Built-in workflow (merged)](https://github.com/orgs/WordPress/projects/79/workflows/7304450)
