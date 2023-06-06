# Deployment

This codebase is deployed as a Docker image to the GitHub Container Registry
[ghcr.io](https://ghcr.io). The deployed image is then pulled in the production
environment. See the [`ci_cd.yml`](../.github/workflows/ci_cd.yml) workflow for
deploying to GHCR.

The published image can be deployed using the minimal
[`docker-compose.yml`](docker-compose.yml) file defined in this folder (do not
forget to update the `.env` file for production). The repository `justfile` can
be used, but the environment variable `IS_PROD` must be set to `true` in order
for it to reference the production `docker-compose.yml` file here. The version
of the image to use can also be explicitly defined using the `IMAGE_TAG`
environment variable (e.g. `IMAGE_TAG=v2.1.1`).