# .github

This folder contains files that configure GitHub services for the management of
the Openverse project.

## Workflows

### Project automation

This workflow supplements the built-in automations of GitHub Projects for moving
issue and PR cards across columns.

**Cron:** [at every 15th minute](https://crontab.guru/#*/15_*_*_*_*)

**Purposes:**

- Add new issues to the "Backlog" column.
- Add new PRs to the "Needs review" column.
- Move issues with linked PRs from the columns "Backlog" and "To do" to 
  the "In progress" column.

### Label sync

This workflow ensures that all repos associated with the project have the
minimum set of consistent labels.

**Cron:** [at 00:00](https://crontab.guru/#0_0_*_*_*)

**Purpose:**
Creates the standard list of labels in all repos, updating the color and 
description where they do not match the standard values.



