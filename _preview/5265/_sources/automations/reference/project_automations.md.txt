# Project Automations

This project contains automations for moving cards related to issues and PRs
across columns of the GitHub Project boards.

The automations are contained in `automations/js` Node.js project and defined in
the following files.

- `src/project_automation/issues.mjs`

  This file defines the rules for moving cards related to issues in the columns
  of the [Openverse Backlog](https://github.com/orgs/WordPress/projects/75/)
  project.

- `src/project_automation/prs.mjs`

  This file defines the rules for moving cards related to PRs in the columns of
  the [Openverse PRs](https://github.com/orgs/WordPress/projects/98/) project.
