# .github

This folder contains files that configure GitHub services for the management of
the Openverse project.

## Workflows

### Project automation

This workflow move issues with linked PRs from the "Backlog" and "To do" columns
to the "In progress" column.

**Cron:** [at every 15th minute](https://crontab.guru/#*/15_*_*_*_*)  
**Dispatch:** enabled

### PR project automation

This workflow archives PRs in the "Merged!" and "Closed" columns of the PR
project board, 15 minutes after the commencement of the weekly developer chat
at 15:00 UTC every Tuesday.

**Cron:** [at 15:15 on Tuesday](https://crontab.guru/#15_15_*_*_2)

### Label sync

This workflow ensures that all repos associated with the project have the
minimum set of consistent labels. It creates missing labels, and updates the
color and description where they do not match the standard values.

**Cron:** [at 00:00](https://crontab.guru/#0_0_*_*_*)  
**Dispatch:** enabled

### Weekly updates

This workflow creates and publishes a post on the Make Openverse site once a
week, outlining the closed issues and merged PRs of the preceding week.

**Cron:** [at 00:01 on Monday](https://crontab.guru/#1_0_*_*_1)  
**Dispatch:** enabled

### New discussion notification

This workflow makes a `POST` request to the Slack webhook when a new
discussion is created, sending a notification message to the
`#openverse-notifications` channel.

**Discussion:** created

### Meta file sync

This workflow ensures that the files specified in [`sync.yml`](sync.yml) are
synchronised across all Openverse repos. Treating this repo as the source of
truth, it creates PRs to resolve any differences.

**Cron:** [at 00:00](https://crontab.guru/#0_0_*_*_*)  
**Push:** Branch `main`  
**Dispatch:** enabled

## Synced workflows

### New issue automation

This workflow adds issues to the "Backlog" column in the Openverse project as
soon as they are created.

**Issue:** opened  
**Dispatch:** disabled

### New PR automation

This workflow adds PRs to the "In progress" or "Needs review" columns in the
Openverse PRs project, based on whether they are marked as draft or ready.

**PR:** opened, converted_to_draft, ready_for_review  
**Dispatch:** disabled

### PR label check

This workflow ensures that all PRs have one label from each of the groups
'aspect', 'goal' and 'priority' applied on them.

**PR:** opened, edited, labeled, unlabeled, synchronize  
**Dispatch:** disabled

### New PR notification

This workflow makes a `POST` request to the Slack webhook when a new PR is
created, sending a notification message to the `#openverse-notifications`
channel. This ping is not sent for PRs made by Dependabot and downstream sync
action.

**PR:** opened

## Downstream workflows

These workflows run only in the downstream synced repos and not in `openverse`.

### Draft release

This workflow updates the draft release message when new commits are added to
`main` so that there is a ready-to-go changelog when publishing a new release.

**Push:** Branch `main`
