# Deployment runbook

```{tip}
For more information on how deployments work, please see the [general deployment guide](/general/deployment.md).
```

1. Visit
   [https://staging.openverse.org/version.json](https://staging.openverse.org/version.json)
   and
   [the frontend Docker image](https://github.com/wordpress/openverse/pkgs/container/openverse-frontend).
   Verify that the commit SHA live on the staging site is also tagged with
   `latest` in the Docker image.
   ![GitHub package directory screenshot](/_static/package_directory_example.png)
1. Release the app via
   [GitHub workflow](https://github.com/WordPress/openverse/actions/workflows/release-app.yml).
   Click the "Run workflow" button, choose "frontend" from the dropdown, and
   supply the SHA identified in step 1.
1. That's it. The frontend will be deployed. You can monitor the deployment in
   the maintainers `#openverse-notifications` channel and in the
   [infrastructure repository's workflow listing](https://github.com/WordPress/openverse-infrastructure/actions).

## Post-deployment steps

1. Check for any Sentry errors in the maintainer's `#openverse-alerts` channel,
   or in the Sentry UI.
1. Visit
   [https://openverse.org/version.json](https://openverse.org/version.json) and
   verify the SHA is the same as the value you deployed.
1. Review and Approve the automatically-generated changelog pull request in the
   repository.
1. In the event of errors or problems, repeat the deployment process using the
   latest stable version of the application. You can find the release version
   number in the [changelogs](/changelogs/index), and then the tag to pass to
   the action is the version number prefixed with "rel-", for example
   "rel-2023.07.03.17.52.00".
