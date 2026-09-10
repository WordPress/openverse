# API deployment runbook

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
1. Review and Approve the automatically-generated changelog pull request in the
   repository.
1. In the event of errors or problems,
   [roll back the application](/meta/release_and_deployment/index.md#force-a-deployment-to-a-specific-version-roll-back-redeploy-re-run-etc).
1. If anything else goes wrong or service is disrupted, consider this a
   Production Incident and notify the team.
