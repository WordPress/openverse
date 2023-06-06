# Notification jobs

## `send-report`

Sends a Slack report if the workflow did not do everything it was expected to
do. It lists the outcome for the 4 key outputs of the workflow for a push to
`main`.

This report is only sent if all the following conditions are met.

- the event is a push to `main`
- the repo is `WordPress/openverse` and not a fork
- one or more of the following expectations was not delivered
  - the documentation or frontend had changes, but new docs were not published
  - there were images meant to be published, but they were not published
  - the frontend codebase changed, but it was not deployed to staging
  - the API codebase changed, but it was not deployed to staging

The workflow sends a Slack message, listing the outcome of four jobs

- [`emit-docs`](/meta/ci_cd/jobs/documentation.md#emit-docs)
- [`publish-images`](/meta/ci_cd/jobs/docker.md#publish-images)
- [`deploy-frontend`](/meta/ci_cd/jobs/deployment.md#deploy-frontend)
- [`deploy-api`](/meta/ci_cd/jobs/deployment.md#deploy-api)

Receiving this report in Slack is an indicator that the workflow did not
complete successfully. It is up to the MSR to investigate the cause of the
failure and take appropriate action.
