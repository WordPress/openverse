# Deployment runbook

## Setup

1. Check
   [Airflow](https://href.li/?https://airflow.openverse.engineering/home?tags=data_refresh)
   to make sure a data refresh isn't occurring.
2. Record and verify the latest commit SHA of
   [the Catalog Docker image](https://github.com/wordpress/openverse/pkgs/container/openverse-catalog).
3. Release the app via
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
2. Deploy production:
   1. `just bump prod catalog` command.
   2. `just apply prod catalog` and verify the plan before deploying.

## Post-deployment steps

1. Check for any Sentry errors in the maintainer's `#openverse-alerts` channel,
   or in the Sentry UI.
1. Review and Approve the automatically-generated changelog pull request in the
   repository.
1. Push up a PR to the infrastructure repository with the Terraform changes you
   pushed (the version bump for the relevant module).
1. In the event of errors or problems, repeat the deployment process with the
   previous production SHA identified in Step 1 of this guide.
1. If anything else goes wrong or service is disrupted, consider this a
   Production Incident and notify the team.
