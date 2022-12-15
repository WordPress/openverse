# Frontend Deployments

| Environment | Deployment Log                                                                                                                        | URL                                                            | Version Endpoint[^versions]                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Staging     | [Staging Deployment Log](https://github.com/WordPress/openverse-frontend/actions/workflows/ghcr.yml?query=branch%3Amain+event%3Apush) | <https://search-staging.openverse.engineering>                 | [Staging version](https://search-staging.openverse.engineering/version.json)       |
| Production  | [Production Deployment Log](https://github.com/WordPress/openverse-frontend/actions/workflows/ghcr.yml?query=event%3Arelease)         | <https://search-production.openverse.engineering>[^production] | [Production version](https://search-production.openverse.engineering/version.json) |

[^versions]:
    To determine the currently deployed version for any environment, visit the
    `/version.json` of the environment. The `release` property will list the
    relevant image tag for the current deployment.

[^production]:
    Note that production is accessed via the iframe at
    <https://wordpress.org/openverse>, not directly via the `search-production`
    subdomain.

The Openverse frontend is deployed using AWS's Elastic Container Service. The
frontend is encapsulated into a single _ECS service_ per environment. The
overall approach of deployments is to generate a new _task definition_ and to
associate that task definition with the ECS Service. This causes the service to
deploy the new task definition as a newly running _task_. Once the service has
determined the new task to be healthy, it will redirect all traffic to the new
task away from the old task. This is called _draining_. Once the old task is
drained, it is spun down and the only task left running is the new one.

> _**Note:**_ The number of running tasks per active task definition may vary
> per environment but has no bearings on the deployment process. The size of the
> service is handle entirely on the infrastructure side. The process above is
> completely automated and contributors generally do not need to be acutely
> aware of the "behind the scenes" stuff going on, but it can be helpful for
> understanding what is happening during a deployment.

## Deployment Workflow

Deployments for all environments follow the same general workflow. This workflow
is completely automated and auditable via GitHub Workflows.

1. Build the ghcr.io/wordpress/openverse-frontend docker image. Tag it
   appropriately for the deployment.
2. Download the template task definition from AWS for the environment being
   deployed. Update the template with the following:
   1. The new image tag
   2. The reified task definition family name without the `-template` suffix
3. Register the new task definition to the ECS service.
4. Wait for the ECS service to report that it is stable.
   - During this waiting period, the process described in the opening paragraph
     is orchestrated by ECS. This part is _not_ transparent in the GitHub
     Workflows and will simply appear as a waiting step without any further
     information.

This process, from start to finish, generally takes less than 15 minutes. If it
takes longer than 15 then something is probably wrong.

### Failures

Failures are automatically handled and the Openverse maintainers are notified.
The GitHub Workflow log is the canonical source of truth of the record of our
deployment attempts. See the table at the top of this document for links to
these logs per environment.

If any of the steps described above fails, including the new task spin up and
switch over, the deployment is deemed a failure. If the failure occurs while
trying to start a new healthy task, the ECS service will automatically rollback
to the previous task definition revision. Remember that the previous task is not
drained and removed until the new task is determined to be healthy, so this
rollback has zero downtime.

If the docker build fails then there is nothing to rollback. The failure needs
to be investigated and the issue fixed for deployments to be possible again.
However, this is unlikely to happen because we require valid Docker image builds
as part of our CI. Nonetheless, given certain semantic merge conflicts, it is
possible that a PR could pass CI and still cause a build failure when merged, so
it is technically possible for a failure to occur during the first step.

## Staging

Staging is automatically deployed any time code is merged to the `main` branch
of this repository. It follows the process above. Staging images are tagged with
the commit SHA, following the pattern `sha-<commit>`. They are also tagged with
`main`[^staging-tag].

[^staging-tag]:
    Currently the staging task definition gets rendered with the `main` tag
    instead of the commit SHA based one. This may change in the future. If it
    does change, there should be no noticeable difference in the deployment
    process to contributors.

## Production

Production is automatically deployed any time a new release is created in
GitHub. Release images are tagged with the release tag name, for example
`v3.4.3`. The task definition is rendered using this tag.

## Rollbacks

Even if the deployment process described above succeeds, sometimes we may
realise that the deployed code is not behaving as we expected. In these cases it
may be necessary to force an environment to be deployed to a specific version.

The
[Rollback Frontend](https://github.com/WordPress/openverse-frontend/actions/workflows/rollback.yml)
workflow makes this possible. It is a dispatchable workflow. Only members of the
@WordPress/openverse-maintainers GitHub team are able to dispatch the workflow
to completion. Anyone else who tries to dispatch it will have the workflow
automatically fail.

The workflow requires two inputs: `environment` and `tag`. `environment` must be
either `staging` or `production` and the `tag` must be a valid tag that exists
on the ghcr.io/wordpress/openverse-frontend image. The `tag` input is validated
against the available list of tags and the workflow will fail if the tag is
determined not to exist in the image repository.

After validating the tag and that the dispatcher is authorised, the Rollback
workflow follows the deployment process described above, except that it skips
the Docker image build and goes straight to step 2. Because of this difference,
the rollback workflow generally takes less than 10 minutes.

## Environment Variables

To add new environment variables for a given service, you must first update the
task definition template in Terraform with the new variables and then deploy the
code that depends on it. It is generally good practice to have safe defaults for
environment variables so that this ordering does not matter.

If you're adding a new environment variable, be sure to coordinate with someone
on @WordPress/openverse-maintainers who is able to update the task definition
template for you, if you're unable to do so yourself.

After the template is updated, deploy the new code following the usual
procedures and the new template will be used.

When updating existing environment variable values or adding new variables that
do not have dependent code, update the template for the environment that needs
updating and then redeploy the environment using the rollback workflow described
above.

## Future end-to-end test integration

In the future we hope to integrate end-to-end tests into this workflow and to
tighten the staging to production pipeline. Essentially, we would like the
deployment pipeline to go something like this:

1. Merge PR to `main`.
2. Wait for staging to deploy.
3. Playwright tests automatically run against the new staging environment.
4. While Playwright tests are running, the person who merged the PR should
   manually verify that their change behaves as expected.
5. After the Playwright tests are confirmed to have passed, unlock a "deploy to
   production" button somewhere that pushes the image currently deployed to
   staging into the production task definition.

Following this process would mean that production gets deployed every time code
is merged to `main`. It reduces the turn around for new features and bug fixes
because they don't have to wait for a new release to be manually created.

We could more or less follow the process as described today just by creating a
new release every time we've merged to staging and verified our changes, but
there are a couple missing pieces that would need to be implemented to make this
process easy to follow, to varying degrees of difficulty:

1. We need a GitHub workflow that runs the Playwright tests against the staging
   deployment automatically after staging is deployed. This will require some
   Playwright configuration tweaks and increased test timeouts due to network
   latency.
2. We would need to create a queue so that new staging deployments do not occur
   until the current staging deployment is live on production. This could be
   implemented by polling the `/version.json` endpoints of both environments and
   only liberating a new staging deployment for new merges once the endpoints
   both report the same `release` property.
3. We would need to update the production deployment workflow to not create a
   new Docker build and instead just pull the current tag from the staging
   `/version.json` endpoint.

Note that this workflow does make the process of merging a PR heavier than it is
today. This comes with some benefits:

1. PRs will likely be more carefully tested as the consequence of merging them
   is higher and more immediately consequential.
2. Bugs will be fixed in production more quickly.
3. Features can be rolled out with more care using feature flags and likewise
   more quickly.
