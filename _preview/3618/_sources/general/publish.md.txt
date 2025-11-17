# Publish

The production API and ingestion server Docker images are published to
[Github Container Registry](https://ghcr.io). They can be found here:

- API:
  [ghcr.io/wordpress/openverse-api](https://ghcr.io/wordpress/openverse-api)
- Ingestion server:
  [ghcr.io/wordpress/openverse-ingestion_server](https://ghcr.io/wordpress/openverse-ingestion_server)

These images are published under two conditions: on release, or manually.

## On release

When a new release is cut, the
[CI/CD action will run](https://github.com/WordPress/openverse-api/actions/workflows/ci_cd.yml?query=event%3Arelease).
The final step of this action uploads the Docker images to their respective
registries with the following tags:

- Release reference name, typically the git tag (e.g. `v2.4.2`)
- `latest`
- The commit SHA of the tagged commit (e.g.
  `b25879b84ec9d7b650be689c03384937a93eb06d`)

In some cases, releases may not alter the Docker image. For instance, in a
release where only the API was changed, the ingestion server image would have
the same Docker image hash. In these instances, the new tags are added to the
existing image.

## Manually

The Docker image for a particular service can also be published manually. This
process is initiated by the
[Publish Docker images on-demand](https://github.com/WordPress/openverse-api/actions/workflows/push_docker_image.yml)
action. The workflow file for this action can be found here:
[`push_docker_image.yml`](https://github.com/WordPress/openverse-api/blob/main/.github/workflows/push_docker_image.yml).

This action **will only publish & tag a service's image with the commit SHA**
(i.e. it will not tag with `latest` or the git reference name). This is useful
for cases where one or more Docker images need to be tested on a staging
environment before being merged and cut with a release. This action also
**requires that the CI/CD workflow has previously run on the specified commit**.
This typically requires a PR in order to initiate.

Note that this action can only run on commits that had successful CI/CD runs in
the last 90 days
[due to GitHub's default artifact retention policy](https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization).

### Steps

_Note:
[GitHub's documentation provides screenshots for the various steps](https://github.blog/changelog/2020-07-06-github-actions-manual-triggers-with-workflow_dispatch)_

1. Navigate to the `openverse` "Actions" tab in GitHub:
   [github.com/WordPress/openverse/actions](https://github.com/WordPress/openverse/actions).
2. Select the "Publish Docker images on-demand" workflow.
3. Click the "Run workflow" button.
   1. (Optional) change the branch _that the workflow is running from_ (this
      does not change anything about the target commit)
   2. For the `image` parameter, specify either `api` or `ingestion_server`.
   3. For the `commit` parameter, specify the commit that the built Docker image
      artifact should be pulled from.
4. Click the green "Run workflow" button.

The newest run should appear in the Action list, and its status can be tracked
from there.

![Example Screenshot](/_static/publish_action_example.png)
