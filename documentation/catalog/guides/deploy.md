# Deployment runbook

## Setup

1. Check [Airflow](https://airflow.openverse.engineering/home?tags=data_refresh)
   to make sure a data refresh isn't occurring.
1. Release the app via
   [GitHub workflow](https://github.com/WordPress/openverse/actions/workflows/release-app.yml).
   Click the "Run workflow" button, choose "catalog" from the dropdown, and
   supply the SHA identified in step 1.

## Deployment

1. After the app is built and tagged, deploy staging:
   1. Checkout the
      [infrastructure repository](https://github.com/wordpress/openverse-infrastructure)
      and bump the ingestion server version with the `just bump dev catalog`
      command.
   1. `just apply dev catalog` and verify the plan before deploying.
1. Deploy production:
   1. `just bump prod catalog` command.
   1. `just apply prod catalog` and verify the plan before deploying.

## Post-deployment steps

1. Check for any Sentry errors in the maintainer's `#openverse-alerts` channel,
   or in the Sentry UI.
1. Review and Approve the automatically-generated changelog pull request in the
   repository.
1. Push up a PR to the infrastructure repository with the Terraform changes you
   pushed (the version bump for the relevant module).
1. In the event of errors or problems, repeat the deployment process using the
   latest stable version of the application. You can find the release version
   number in the [changelogs](/changelogs/index), and then the tag to pass to
   the action is the version number prefixed with "rel-", for example
   "rel-2023.07.03.17.52.00".
1. If anything else goes wrong or service is disrupted, consider this a
   Production Incident and notify the team.
