# Deployment runbook

## Setup

1. Check [airflow](https://airflow.openverse.engineering/home?tags=data_refresh)
   to make sure a data refresh isn't occurring.
2. Release the app via
   [GitHub workflow](https://github.com/WordPress/openverse/actions/workflows/release-app.yml).
   Click the "Run workflow" button, choose "ingestion server" from the dropdown,
   and supply the SHA identified in step 1.

## Deployment

1. After the app is built and tagged, deploy staging:
   1. Checkout the
      [infrastructure repository](https://github.com/wordpress/openverse-infrastructure)
      and bump the ingestion server version with the
      `just bump dev ingestion-server` command.
   1. `just apply dev ingestion-server` and verify the plan before deploying.
2. Deploy production:
   1. Update the value of `data_refresh_cleared` to `true` in the
      [production module declaration](https://github.com/WordPress/openverse-infrastructure/blob/main/environments/prod/ingestion-server.tf#L9).
   1. `just bump prod ingestion-server` command.
   1. `just apply prod ingestion-server` and verify the plan before deploying.
   1. Restore the value of `data_refresh_cleared` back to `false`.

## Post-deployment steps

1. Check for any Sentry errors in the maintainer's `#openverse-alerts` channel,
   or in the Sentry UI.
1. Review and Approve the automatically-generated changelog pull request in the
   repository.
1. Push up a PR to the infrastructure repository with the Terraform changes you
   pushed (the version bump for the relevant module). Be sure to restore the
   value of `data_refresh_cleared` back to `false`.
1. In the event of errors or problems, repeat the deployment process using the
   latest stable version of the application. You can find this tag in the
   [changelogs](/changelogs/index).
1. If anything else goes wrong or service is disrupted, consider this a
   Production Incident and notify the team.
