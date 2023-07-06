# Deployment runbook

```{tip}
For more information on how deployments work, please see the [general deployment guide](/general/deployment.md).
```

1. Record and verify the commit `sha` of the production site at
   [https://openverse.org/version.json](https://openverse.org/version.json).
1. Visit
   [https://staging.openverse.org/version.json](https://staging.openverse.org/version.json)
   and
   [the frontend package directory](https://github.com/wordpress/openverse/pkgs/container/openverse-frontend).
   Verify that the commit `sha` live on the staging site is also tagged with
   `latest` in the package directory.

   ```{figure} /_static/package_directory_example.png
   ---
   class: with-border
   ---
   ```

1. Release the app via
   [GitHub workflow](https://github.com/WordPress/openverse/actions/workflows/release-app.yml).
   Click the "Run workflow" button, choose "frontend" from the dropdown, and
   supply the `sha` identified in step 1.
1. That's it. The frontend will be deployed. You can monitor the deployment in
   the maintainers `#openverse-notifications` channel and in the
   [infrastructure repository's workflow listing](https://github.com/WordPress/openverse-infrastructure/actions).

## Post-deployment steps

1. Check for any Sentry errors in the maintainer's `#openverse-alerts` channel,
   or in the Sentry UI.
1. Visit
   [https://openverse.org/version.json](https://openverse.org/version.json) and
   verify the `sha` is the same as the value you deployed.
1. Review and Approve the automatically-generated changelog pull request in the
   repository.
1. In the event of errors or problems, repeat the deployment process with the
   previous production `sha` identified in Step 1 of this guide.
