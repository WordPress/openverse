# Flow

Since the CI + CD workflow is very complex, to simplify and understand it, we
can assume it to take place across several stages.

```{mermaid}
flowchart TD
  preparation[Preparation] --- a[&nbsp]
  %% a is a fork
  a --> frontend_tests[Frontend tests] & docker_preparation[Docker preparation] & documentation_tests[Documentation tests]
  docker_preparation --> dockerised_tests[Dockerised tests]
  frontend_tests --- e[&nbsp]
  %% e is a fork
  dockerised_tests --- f[&nbsp]
  %% f is a fork
  e & f --- b[&nbsp]
  %% b is a join
  b --> docker_publishing[Docker publishing] --> deployment[Deployment]
  documentation_tests ---- c[&nbsp]
  e & f --- c
  %% c is a join
  c --> documentation_emit[Documentation emit]
  documentation_emit & deployment --- d[&nbsp]
  d --> notification[Notification]

  style a height:0,width:0
  style b height:0,width:0
  style c height:0,width:0
  style d height:0,width:0
  style e height:0,width:0
  style f height:0,width:0
```

```{caution}
The stages are a learning tool, not a true representation of how CI works. In
reality, there is no clear lines between stages. Jobs in a later stage will
start as soon as their dependencies are satisfied, without waiting for the full
previous stage to complete first.

For example, the [Docker publishing](#docker-publishing) stage starts as soon as
the tests it depends on have passed, even if there are other jobs still running
in the previous stages (like `playwright` from the
[frontend tests](#frontend-tests) stage).
```

Read on to know more about these stages and the jobs that constitute them. Each
section is also accompanied by a flowchart to help visualise the jobs that
comprise a stage and their relationship with job in prior stages on which this
stage depends.

## Preparation

This is the stage of jobs which have no dependencies, so they get executed at
the very start of the workflow. Since they are depended upon by other jobs, once
this stage is complete, we can use their resulting state and outputs wherever
needed.

```{mermaid}
flowchart TD
  subgraph preparation[Preparation]
    get-changes
    get-image-tag
    lint
  end
```

**Jobs:**

- [`get-changes`](./jobs/preparation.md#get-changes)
- [`get-image-tag`](./jobs/preparation.md#get-image-tag)
- `lint`

## Documentation tests

The documentation tests run outside the Docker containers, so they don't need to
wait for the Docker containers to be build. This stage happens in parallel with
the [frontend tests](#frontend-tests) and the
[Docker preparation](#docker-preparation) stages.

These tests are only executed if the documentation has changed. Else they will
be skipped.

```{mermaid}
flowchart TD
  subgraph preparation[Preparation]
    lint
    get-changes
  end

  get-changes -- documentation == true &#124&#124 frontend == true --- x
  lint --- x
  x[&nbsp] --> build-docs

  subgraph documentation_tests[Documentation tests]
    build-docs
  end

  style x height:0
  style preparation opacity:0.3
```

**Jobs:**

- [`build-docs`](./jobs/documentation.md#build-docs)

## Frontend tests

The frontend tests run outside the Docker containers, so they don't need to wait
for Docker containers to be built. This stage happens in parallel with the
[Docker preparation](#docker-preparation) stage. The Playwright tests are very
time-consuming so this stage extends long enough to be contemporary with the
[Dockerised tests](#dockerised-tests) stage.

These tests are only executed if the frontend has changed. Else they will be
skipped and bypass jobs for `nuxt-build` and `playwright` will run instead.

```{mermaid}
flowchart TD
  subgraph preparation[Preparation]
    lint
    get-changes
  end

  get-changes -- frontend == true --- x
  lint --- x
  x[&nbsp] --> nuxt-checks & nuxt-build & playwright

  subgraph frontend_tests[Frontend tests]
    nuxt-checks
    nuxt-build
    playwright
  end

  subgraph bypass_jobs[Bypass jobs]
    bypass-nuxt-checks
    bypass-playwright
  end

  nuxt-checks -- skipped --> bypass-nuxt-checks
  playwright -- skipped --> bypass-playwright

  style x height:0
  style preparation opacity:0.3
```

**Jobs:**

- [`nuxt-checks`](./jobs/frontend.md#nuxt-checks)
- [`nuxt-build`](./jobs/frontend.md#nuxt-build)
- [`playwright`](./jobs/frontend.md#playwright)
- [`bypass-nuxt-checks`](#bypass-jobs)
- [`bypass-playwright`](#bypass-jobs)

## Docker preparation

A number of our jobs test the services running inside Docker containers, so
before we can run those jobs in [Dockerised tests](#dockerised-tests), we must
prepare the Docker images for these services.

The `determine-images` job determines the images to build (and also publish, see
section on [Docker publishing](#docker-publishing) below) based on the changes
observed by `get-changes`. This information is passed to the `build-images` job,
which builds the images.

If `determine-images` finds no images to build, which can happen if there are no
changes to the catalog, ingestion server, API or frontend, the `build-images`
job will be skipped.

```{mermaid}
flowchart TD
  subgraph preparation[Preparation]
    get-changes
    get-image-tag
    lint
  end

  subgraph docker_preparation[Docker preparation]
    determine-images
    build-images
  end

  get-changes -- changes --> determine-images -- do_build,build_matrix --> build-images
  get-image-tag -- image_tag --> build-images
  lint --> build-images

  style preparation opacity:0.3
```

**Jobs:**

- [`determine-images`](./jobs/docker.md#determine-images)
- [`build-images`](./jobs/docker.md#build-images)

## Dockerised tests

The tests for the catalog, ingestion server and API all use Docker containers of
their services in the tests. Thus, this stage of testing occurs after the
[Docker preparation](#docker-preparation) stage. Unlike the frontend tests, they
do not depend on the `lint` job, as that is already present as a dependency of
the `build-images` job.

```{mermaid}
flowchart TD
  subgraph preparation[Preparation]
    get-changes
  end

  subgraph docker_preparation[Docker preparation]
    build-images
  end

  get-changes -- catalog == true --- x
  x[&nbsp] --> test-cat & catalog-checks

  get-changes -- ingestion_server == true --- y
  y[&nbsp] --> test-ing

  get-changes -- api == true --- z
  z[&nbsp] --> test-api & django-checks

  build-images -- success --- x & y & z

  subgraph dockerised_tests[Dockerised tests]
    test-cat
    catalog-checks

    test-ing

    test-api
    django-checks
  end

  subgraph bypass_jobs[Bypass jobs]
    bypass-django-checks
  end

  django-checks -- skipped --> bypass-django-checks

  style x height:0
  style y height:0
  style z height:0
  style preparation opacity:0.3
  style docker_preparation opacity:0.3
```

**Jobs:**

- [`test-cat`](./jobs/catalog.md#test-cat)
- [`catalog-checks`](./jobs/catalog.md#catalog-checks)
- [`test-ing`](./jobs/ingestion_server.md#test-ing)
- [`test-api`](./jobs/api.md#test-api)
- [`django-checks`](./jobs/api.md#django-checks)
- [`bypass-django-checks`](#bypass-jobs)

## Documentation emit

After all the [proof-of-functionality](./proof_of_functionality.md) tests have
concluded, we can initiate the stage of publishing the new documentation. The
documentation is published to the [docs site](https://docs.openverse.org)
side-by-side with the [publishing of the Docker images](#docker-publishing).

```{mermaid}
flowchart TD
  subgraph preparation[Preparation]
    get-changes
  end

  subgraph documentation_tests[Documentation tests]
    build-docs
  end

  subgraph frontend_tests[Frontend tests]
    nuxt-build
  end

  subgraph dockerised_tests[Dockerised tests]
    test-cat
    test-ing
    test-api
  end

  subgraph documentation[Documentation]
    emit-docs
  end

  get-changes -- documentation == true &#124&#124 frontend == true  --> emit-docs
  build-docs -- success --> emit-docs
  test-cat & test-ing & test-api & nuxt-build -. success/skipped .-> emit-docs

  style preparation opacity:0.3
  style frontend_tests opacity:0.3
  style dockerised_tests opacity:0.3
  style documentation_tests opacity:0.3
```

**Jobs:**

- [`emit-docs`](./jobs/documentation.md#emit-docs)

## Docker publishing

In this stage we publish the Docker images that have passed the
[proof-of-functionality](./proof_of_functionality.md) tests to
[GHCR](https://github.com/orgs/WordPress/packages?repo_name=openverse). We
[publish the new developer docs](#documentation-emit) alongside these images.

The `determine-images` job determines the images to publish (and also build, see
section on [Docker preparation](#docker-preparation) above) based on the changes
observed by `get-changes`. This information is passed to the `publish-images`
job, which publishes the images.

If `determine-images` finds no images to publish, which can happen if there are
no changes to the catalog, ingestion server, API or frontend, the
`publish-images` job will be skipped.

```{mermaid}
flowchart TD
  subgraph preparation[Preparation]
    get-image-tag
  end

  subgraph frontend_tests[Frontend tests]
    nuxt-build
  end

  subgraph docker_preparation[Docker preparation]
    determine-images
    build-images
  end

  subgraph dockerised_tests[Dockerised tests]
    test-cat
    test-ing
    test-api
  end

  subgraph docker_publishing[Docker publishing]
    publish-images
  end

  get-image-tag -- image_tag --> publish-images
  determine-images -- do_publish,publish_matrix --> publish-images
  build-images -- success --> publish-images
  test-cat & test-ing & test-api & nuxt-build -. success/skipped .-> publish-images

  style preparation opacity:0.3
  style docker_preparation opacity:0.3
  style frontend_tests opacity:0.3
  style dockerised_tests opacity:0.3
```

**Jobs:**

- [`publish-images`](./jobs/docker.md#publish-images)

## Deployment

This stage is specifically for the services running on ECS, namely the API and
the frontend. If either of these services have been updated, the workflow also
updates their staging environments to use the Docker images published in the
[Docker publishing](#docker-publishing) stage.

```{mermaid}
flowchart TD
  subgraph preparation[Preparation]
    get-changes
    get-image-tag
  end

  subgraph deployment[Deployment]
    deploy-api
    deploy-frontend
  end

  subgraph docker_publishing[Docker publishing]
    publish-images
  end

  subgraph frontend_tests[Frontend tests]
    playwright
  end

  get-image-tag -- image_tag --> deploy-api & deploy-frontend

  get-changes -- api == true --> deploy-api
  get-changes -- frontend == true --> deploy-frontend

  publish-images -- success --> deploy-api
  publish-images -- success --> deploy-frontend

  playwright -- success --> deploy-frontend

  style preparation opacity:0.3
  style docker_publishing opacity:0.3
  style frontend_tests opacity:0.3
```

**Jobs:**

- [`deploy-api`](./jobs/deployment.md#deploy-api)
- [`deploy-frontend`](./jobs/deployment.md#deploy-frontend)

## Notification

At this stage, the workflow should have completed all its objectives and
delivered on all four of its key outcomes. In this stage we compare our
expectations set by the `get-changes` job with the actual results of the
workflow and report any discrepancies via Slack.

```{mermaid}
flowchart TD
  subgraph preparation[Preparation]
    get-changes
  end

  subgraph docker_preparation[Docker preparation]
    determine-images
  end

  subgraph documentation_publishing[Documentation publishing]
    emit-docs
  end

  subgraph docker_publishing[Docker publishing]
    publish-images
  end

  subgraph deployment[Deployment]
    deploy-api
    deploy-frontend
  end

  subgraph notification[Notification]
    send-report
  end

  get-changes -- frontend,documentation,api --> send-report
  determine-images -- do_publish --> send-report
  emit-docs -- !success --> send-report
  publish-images -- !success --> send-report
  deploy-api & deploy-frontend -- !success --> send-report

  style preparation opacity:0.3
  style docker_preparation opacity:0.3
  style documentation_publishing opacity:0.3
  style docker_publishing opacity:0.3
  style deployment opacity:0.3
```

**Jobs:**

- [`send-report`](./jobs/notification.md#send-report)

## Bypass jobs

If a job is marked as a required check in GitHub it must
[either pass or be skipped](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/troubleshooting-required-status-checks#handling-skipped-but-required-checks)
to allow the PR to be merged. This is different for matrix jobs because if a
matrix is skipped due to an `if` condition, it is not expanded into individual
jobs but skipped as a whole, leaving the checks associated with that matrix in a
pending state, preventing PRs from being merged.

For such jobs, we use a bypass job, conventionally named `bypass-<job name>`,
that is run on the opposite of the condition of the original job `<job name>`.
This bypass job is an identical matrix, except it always succeeds, and satisfies
the required checks by having the same job names as the original.
