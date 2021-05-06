# Openverse Scripts

This folder contains files that configure GitHub services for the management of the Openverse project.

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

## Contributing

Pull requests are welcome! Feel free to [join us on Slack](https://make.wordpress.org/chat/) and discuss the project with the engineers and community memebers on #openverse.
