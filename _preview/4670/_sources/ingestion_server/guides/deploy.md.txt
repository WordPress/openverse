# Deployment runbook

## Setup

1. Check [Airflow](https://airflow.openverse.org/home?tags=data_refresh) to make
   sure a data refresh isn't occurring.
1. [Publish the drafted ingestion server release in the GitHub release page of the monorepo](https://github.com/WordPress/openverse/releases?q=ingestion_server-)
   - Here you can preview the changes included in the ingestion server release
     and decide whether a release is necessary and adjust monitoring during the
     deployment accordingly.

## Deployment

1. After the app is built and tagged, deploy staging:
   1. Checkout the
      [infrastructure repository](https://github.com/wordpress/openverse-infrastructure)
      and bump the ingestion server version with the
      `just bump dev ingestion-server` command.
   1. `just apply dev ingestion-server` and verify the plan before deploying.
1. Deploy production:
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
1. In the event of errors or problems, rollback the application by running the
   appropriate deployment workflow from the WordPress/openverse-infrastructure
   repository using the tag of the latest stable version. You can find the
   release version number in the [changelogs](/changelogs/index), and then the
   tag to pass to the action is the version number prefixed with "rel-", for
   example "rel-2023.07.03.17.52.00".
1. If anything else goes wrong or service is disrupted, consider this a
   Production Incident and notify the team.
