# Frontend deployment runbook

```{tip}
For more information on how deployments work, please see the [general deployment guide](/meta/release_and_deployment/index.md).
```

## Publish the release

[Publish the drafted frontend release in the GitHub release page of the monorepo](/meta/release_and_deployment/index.md#how-to-publish-a-release).

## Deployment

Publishing the release will automatically trigger a deployment. You can monitor
the deployment in the maintainers `#openverse-notifications` channel and in the
[infrastructure repository's workflow listing](https://github.com/WordPress/openverse-infrastructure/actions).

## Post-deployment steps

1. Check for any Sentry errors in the maintainer's `#openverse-alerts` channel,
   or in the Sentry UI.
1. Visit
   [https://openverse.org/version.json](https://openverse.org/version.json) and
   verify the SHA is the same as the value you deployed.
1. Review and Approve the automatically-generated changelog pull request in the
   repository.
1. In the event of errors or problems,
   [roll back the application](/meta/release_and_deployment/index.md#force-a-deployment-to-a-specific-version-roll-back-redeploy-re-run-etc).
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
