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
1. Add any new analytics events to Plausible:

   1. Visit
      [the "Goals" configuration page](https://plausible.io/openverse.org/settings/goals)
      and add any new events.
   1. If those events have new unique payload property names, those must also be
      added
      [to the "Custom properties" configuration](https://plausible.io/openverse.org/settings/properties).

   ```{warning}
   **Do not click the "click to add all existing properties" button!** This button
   will cause all props to be added and therefore displayed on events, [even ones we've
   explicitly removed](https://github.com/WordPress/openverse/commit/53c2e70171e22593027b184b599c530a47429a03).
   Instead, manually add new custom properties one at a time by entering them into
   the input box on the page. If the event has already been sent once, the property
   names will auto-complete in the box, making it less tedious to add new ones.

   If you accidentally click this button, please manually delete the following
   deprecated properties from the configuration:

   - `timestamp`
   - `language`
   - `ua`
   - `os`
   - `platform`
   - `browser`
   - `version`
   - `origin`
   - `pathname`
   - `referrer`
   ```
