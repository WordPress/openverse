# .github

This folder contains files that configure GitHub services.

### Workflows

#### Project automation

This workflow supplements the built-in automations of GitHub Projects for moving
issue and PR cards across columns.

**Cron:** [at every 15th minute](https://crontab.guru/#*/15_*_*_*_*)

**Purposes:**

- Add new issues to the "Backlog" column.
- Add new PRs to the "Needs review" column.
- Move issues with linked PRs from the columns "Backlog" and "To do" to 
  the "In progress" column.
