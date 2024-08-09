# Deployment runbook

```{tip}
For more information on how deployments work, please see the [general deployment guide](/general/deployment.md).
```

1. [Publish the drafted API release in the GitHub release page of the monorepo](https://github.com/WordPress/openverse/releases?q=api-)
   - Here you can preview the changes included in the API release and decide
     whether a release is necessary and adjust monitoring during the deployment
     accordingly.
1. That's it! The API will be deployed. You can monitor the deployment in the
   maintainers `#openverse-notifications` channel and in the
   [infrastructure repository's workflow listing](https://github.com/WordPress/openverse-infrastructure/actions).

## Post-deployment steps

1. Check for any Sentry errors in the maintainer's `#openverse-alerts` channel,
   or in the Sentry UI.
1. Visit
   [https://api.openverse.engineering/v1](https://api.openverse.engineering/v1)
   and verify the SHA is the same as the value you deployed.
1. Review and Approve the automatically-generated changelog pull request in the
   repository.
1. In the event of errors or problems, rollback the application by running the
   appropriate deployment workflow from the WordPress/openverse-infrastructure
   repository using the tag of the latest stable version. You can find the
   release version number in the [changelogs](/changelogs/index), and then the
   tag to pass to the workflow is the version number prefixed with "rel-", for
   example "rel-2023.07.03.17.52.00".
1. If anything else goes wrong or service is disrupted, consider this a
   Production Incident and notify the team.
