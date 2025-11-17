# Releasing and deploying code

<!--
A note to maintainers on the purpose of this document and motivations behind
its method of organising the relevant information:

This document covers the code release and deployment processes for each service
and environment. Colocating all information related to release and deployment
(as opposed to separating them into the app-specific directories) allows us to
more easily point out similarities and difference to keep in mind between each
application, as these details tend to be where confusion happens the most.
-->

```{tip}
This documentation section is targeted at Openverse maintainers. As such, some
information or links may be inaccessible to general contributors.
```

## Runbooks

If you are actively releasing and deploying an application, refer to the
runbooks for the app you wish to release and deploy:

```{toctree}
:maxdepth: 1
:glob:

runbooks/*
```

## Tangled web of ambiguous terminology

The [terminology defined in the next section](#glossary) must be understood and
referred to with absolute clarity in order to prevent confusion when thinking
about, discussing, or modifying the release and deployment processes. Of
particular difficulty are:

- That **release** and **tag** are both nouns and verbs, and can individually
  refer to multiple different distinct concepts.
- That **workflow** and **process** may refer to the same things, but that
  **workflow** is also the name of a specific GitHub feature used to perform
  either a part of or a whole process. As such, the phrase "**the workflow**" is
  ambiguous and may be interpreted as either "**the process**" or a specific
  GitHub Workflow.
- That **release** (as a verb) and **deploy** are often used to denote either
  part of or the entire process of both releasing and deploying code for a
  service. This can make communicating about a particular step of the overall
  release-and-deploy process confusing. The glossary below treats release and
  deploy as distinct, non-overlapping, but related processes.
  - _This is a critical distinction, and can be especially meaningful in the
    context of fixing a live environment, when deciding between and
    communicating specific corrective actions like a roll back, the release of a
    new version with fixes, or a revert_.

## Glossary

Refer to the following definitions for unambiguous descriptions of each term.

- **Application** or **app** (noun)

  - One of the Openverse **apps**, frontend, API, catalog (Airflow), ingestion
    server.

- **Service** (noun):

  - Used interchangeably with **application**.

- **Docker image** (noun):

  - A binary blob containing information used to run an application in a
    containerised environment. Openverse uses Docker images to distribute and
    run its services. A new Docker image is created for each app for every push
    to main that included modifications of code related to the app.
  - Docker images have one or more **Docker image tags** (see below).

- **Process** (noun):

  - A series of steps followed to achieve an outcome.

- **Workflow** (noun):

  - An alternative name for **process**. Because it is too easy to confuse this
    with **GitHub Workflow**, it is clearer to use **process** to refer to any
    set of steps to achieve an outcome, and the full name **GitHub Workflow** to
    refer to the GitHub feature.

- **GitHub Workflow** (noun):

  - A collection of GitHub Actions and jobs to complete a process.

- **GitHub Release** (noun):

  - [A GitHub feature for creating **releases** of a codebase](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository),
    typically representing a group of build artefacts associated with a specific
    commit in the git history. Openverse uses GitHub Releases to gather release
    notes for build artefacts we intend to deploy to production. See the next
    definition for another Openverse use of GitHub releases.

- **Publish (GitHub) release** (verb):

  - Literally clicking the **publish** button on a GitHub Release's page. This
    **publishes** the GitHub Release, which in turn triggers Openverse's "tag
    docker image and trigger deployment" GitHub Workflow. Sometimes **cut a
    release** is used to refer to this, but should be avoided due to being
    jargon.

- **Tag docker image and trigger deployment GitHub Workflow** (noun):

  - The GitHub Workflow triggered after a GitHub Release is published.
    Responsible for tagging the `latest` docker image of the app with the
    release tag using the date string from the published release's git tag. It
    also triggers a deployment by dispatching the relevant GitHub Workflow in
    the `openverse-infrastructure` repository.

- **Tag** (verb):

  - The action of applying a tag (of any sort) to a thing. e.g.:
    - "Tag the release"
    - "Tag the Docker image"
    - "Add a tag to the Docker image"
    - "Tag the git commit"

- **Release** (verb):

  - The process of applying a release tag to build artefacts.

- **Deploy** (verb):

  - The process of updating a live environment with new code or configuration.

- **Rollback/Roll back** (verb):

  - The process of deploying a live environment to a previous version of code or
    configuration.

- **Docker image tag** or sometimes just **image tag** (noun):

  - The identifier of a specific **version** of a Docker image. The part that
    comes after the `:` in a qualified docker image reference. In
    `openverse-frontend:latest`, **latest** is the image tag. Openverse uses
    tags in the pattern `rel-{date}` to denote Docker image versions
    corresponding to a published release. All Openverse Docker images are also
    tagged with the git commit SHA from which the image was built.
  - Any given tag refers only to a single image at one time. However, tags may
    refer to more than one image at different times by changing the image
    referenced by the tag in the Docker image repository. This is called "moving
    the tag" between the images.

- **Git tag** (noun):

  - A name given to a commit in the git history. Openverse uses git tags in the
    pattern `{app}-{date}` to indicate a commit used as the **release** point
    for a particular app.

- **Release tag** (noun):
  - Both a **git tag** and **docker image tag**, each using a separate format as
    described above.

## How to publish a release

To publish a release for an app,
[find the drafted release in the GitHub release page of the monorepo](https://github.com/WordPress/openverse/releases).
Here you can preview the changes included in the release for each app and decide
whether a release is necessary, as well as adjust monitoring during the
deployment accordingly.

| Releases filtered by app                                                                |
| --------------------------------------------------------------------------------------- |
| [API](https://github.com/WordPress/openverse/releases?q=api-)                           |
| [Frontend](https://github.com/WordPress/openverse/releases?q=frontend-)                 |
| [Catalog](https://github.com/WordPress/openverse/releases?q=catalog-)                   |
| [Ingestion server](https://github.com/WordPress/openverse/releases?q=ingestion-server-) |

The indexer worker does not use releases (because they always run the Docker
image tagged `latest`).

Upon publishing the GitHub Release, the Openverse bot will automatically open a
PR with a new changelog entry. You should review and approve (or modify and
approve) this PR after publishing the release.

## The flow of code from main to production for each app

The flow charts below describe the flow of code from `main` all the way to
"production" for each application in a single flow chart. Not all apps have
fully automated deployments, and only staging releases are automated. Production
releases are never automated, but production deployments may be automated as a
result of a production release. Some applications do not have a clear separation
between staging and production (catalog, indexer worker, and ingestion server).

Steps that require manual human intervention are designated with squared boxes,
whereas rounded boxes indicate a step that occurs as a direct and automatic
result of the previous step.

The dotted lines from the automated catalog, API, and frontend deployment denote
the flow of code to the production release event, rather than a specific action.
These lines are meant to indicate a continuation of the lifecycle of the code
for each of these apps through the entire flowchart, from the initial staging
release to the final production deployment.

Build artefacts are generated for every Openverse application any time a push to
main includes changes relevant to the code base for the app. This is always the
Docker image tagged `latest` for each app and constitutes the whole of a staging
release. Only the staging API and staging frontend are automatically deployed as
a result of these releases. The catalog has an automatic DAG sync process that
pulls code from `main` without intervention, and so has something of a "partial"
staging deployment process, despite not rely on the `latest` image to do so. On
the other hand, the indexer workers pull and run the `latest` docker image each
time they execute. As such, they do not have a formal "deployment" process, nor
a distinct staging/production release.

The API, frontend, catalog, and ingestion server all experience "true"
production releases and deployments that are distinct from the release and
deployment of the `latest` docker image or repository code. The API and frontend
are automatically deployed whenever a maintainer creates a production release,
following the same deployment process as their staging counterparts (despite
having different release processes). Neither the "staging" or "production"
ingestion servers run the `latest` code in most circumstances, and are usually
deployed together as a result of a production release. While the catalog always
runs the latest DAG code (via the DAG sync operation on merges to main), it only
receives updates to dependencies (including Airflow itself), after a production
release and subsequent manual deployment.

### API and Frontend

The API and frontend follow identical processes to move code from `main` to
production.

```{note}
The API automatically runs database migrations when deploying to each environment.
No human intervention is required to facilitate this process.
```

```{mermaid}
flowchart TD
    Merge["Merge to <code>main</code>"]
    Build("<u>CI/CD</u>\nVerify code, build/upload docker images\ntagged with <code>latest</code> and the commit hash")
    StagingDispatch("<u>Deployment workflow</u>\nRender & push task definition\nwith commit hash tag")
    RevertRollback[Roll back by merging a revert\nof the broken code to main] ---> Build

    Merge ---> Build

    Build -->|"(Dispatches staging deployment workflow)"| StagingDispatch o--o RevertRollback

    StagingDispatch -..-> Publish

    Publish[Publish GitHub Release]
    Tag("Tag the <code>latest</code> docker image for the\nreleased app with the 'release tag' based\non the GitHub Release title and associated git tag")
    ProductionDispatch("<u>Deployment workflow</u>\nRender & push task definition with release tag")
    TriggerRollback[Trigger the production deployment\nworkflow with the last known\nworking production image tag]

    Publish --> Tag
    Tag -->|"(Dispatches production deployment workflow)"| ProductionDispatch o--o|Rollback| TriggerRollback
```

#### Force a deployment to a specific version (roll back, redeploy, re-run, etc.)

```{tip} Quick Tips for Performing a Rollback

To perform a rollback, manually trigger the appropriate deployment workflow from the [WordPress/openverse-infrastructure repository](https://github.com/WordPress/openverse-infrastructure/actions) using the tag of the latest stable version. You can find the release version number in the [changelogs](/changelogs/index); the tag to pass to the action is the version number prefixed with "rel-", for example "rel-2023.07.03.17.52.00".
```

Because we have the ability to force a deployment of the app to any specific
version, the same process can be used to deploy to a completely new version, the
version currently running, or a past version. This same process works to perform
rollbacks or retry a failed deployment.

To force a deployment of the API or frontend (of either environment) to any
specific version, manually trigger the appropriate deployment workflow for the
desired app and environment (see table below), using the docker image tag that
you want to deploy.

To find historically deployed production image tags, refer to the title of the
workflow runs for the app (linked in the table below). The `rel-*` image tags in
the titles of the production deployment workflow runs is the image tag deployed
for that run.

To find the currently deployed tag of any environment, visit the `/version`
endpoint of the API or frontend environment you wish to redeploy:

| App version endpoint                                                 | Deployment workflow                                                                                                           |
| -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| [Frontend staging `/version`](https://staging.openverse.org/version) | [Deployment workflow](https://github.com/WordPress/openverse-infrastructure/actions/workflows/deploy-staging-frontend.yml)    |
| [Frontend production `/version`](https://openverse.org/version)      | [Deployment workflow](https://github.com/WordPress/openverse-infrastructure/actions/workflows/deploy-production-frontend.yml) |
| [API staging `/version`](https://api-staging.openverse.org/version)  | [Deployment workflow](https://github.com/WordPress/openverse-infrastructure/actions/workflows/deploy-staging-api.yml)         |
| [API production `/version`](https://api.openverse.org/version)       | [Deployment workflow](https://github.com/WordPress/openverse-infrastructure/actions/workflows/deploy-production-api.yml)      |

Click the "Run workflow" button on the deployment workflow page in GitHub to
open the manual workflow trigger dialogue.

```{figure} ./manually-trigger-workflow.png
:alt: Deployment workflow manual trigger dialogue
:height: 400
```

Enter the tag found from the `/version` endpoint as the "Image tag to deploy" in
the manual workflow run dialogue, add a reason for the manual deployment as the
"name of the workflow run", and then click the dialogue's "Run workflow" button.

```{admonition} Production tag details
:class: warning

The production release and deployment process uses the <code>rel-\*</code> pattern image tags when dispatching
the deployment workflow for each app. However, the <code>rel-\*</code> image tags are merely aliases for the
git commit hash based image tags that are returned by the <code>/version</code> endpoints linked above. There
is no difference between running the deployment workflow with the tag returned by the <code>/version</code> endpoint
or the <code>rel-\*</code> tag. Use whichever method you find most convenient.
```

```{note}
The recommended approach for rolling back the staging API or frontend is (if possible)
to revert the broken code out of `main` and follow the regular staging deployment process.

This is preferred because it ensures `main` is never unhealthy for longer than it needs
to be, while also acknowledging that the staging API and frontend are non-critical
services that do not require rapid responses to fix. It's more important for the code in
`main` to be operational and healthy than for the staging API or frontend to be
operational. This is because `main` is always used as the basis for production
deployments, including emergency "hot fixes" when a production rollback isn't possible
(e.g., a security patch in a dependency). In these cases, we want to make sure as
much as possible that `main` is healthy, so that we can rapidly apply changes to
production when needed.

**That being said**, the same manual triggering of the staging deployment workflows also
works to force a deployment of either staging application to a specific image tag. It's just
that in practice it isn't usually necessary.
```

#### Debugging ECS failures

```{tip}
Please refer to the [general ECS logging documentation](/meta/monitoring/cloudwatch_logs/index.md)
for details about how to find logs for individual tasks.

The ECS events list for a service may also be helpful for debugging a failed deployment. You can find that under the "Events" tab of the ECS service's page:

![Example ECS events tab for the production API](/_static/ecs_events_tab.png)

This tab shows a chronological list of the 100 most recent "events".
[Refer to the AWS ECS documentation for information on what each of these events mean](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_cwe_events.html).
```

### Catalog

The catalog has a unique process built around a single live environment that
receives automatic updates to code, but not to the runtime environment of the
code.

```{note}
New DAGs are not automatically enabled and will need to be turned on
after the DAG sync script pulls the new code.
```

```{admonition} When to release and deploy the catalog
:class: tip

Releasing and deploying the catalog is only necessary in the following conditions:

- The Docker image has been modified
- An environment variable needs to be added/removed/changed
```

```{mermaid}
flowchart TD
    Merge["Merge to <code>main</code>"]
    DagSync("<u>DAG Sync</u>\nPulls latest code from git repository which is\nautomatically parsed by Airflow\nand used for new runs")
    RevertRollback[Roll back by merging a revert\nof the broken code to main] ---> DagSync

    Merge --> DagSync o--o RevertRollback

    DagSync -..-> Publish

    Publish[Publish GitHub Release]
    Tag("Tag the <code>latest</code> docker image for the\nreleased app with the 'release tag' based\non the GitHub Release title and associated git tag")
    ManCat["<u>Infrastructure repository</u>\nSet the release tag in the catalog's\nAnsible variables and run the catalog's\nAnsible playbook</u>"]
    ApplyRollback[Redo the previous step, but with the last\nknown working production image tag]

    Publish --> Tag
    Tag --> ManCat o--o|Rollback| ApplyRollback
```

#### Migrations

Any migration to the Catalog database must either be performed by hand or as
part of a DAG's normal operation (see:
[iNaturalist](https://github.com/WordPress/openverse/blob/main/catalog/dags/providers/provider_api_scripts/inaturalist.py)).

### Indexer worker

The indexer worker has by far the simplest release and deployment process of any
Openverse application, requiring no manual intervention at any step.

```{mermaid}
flowchart TD
    Merge["Merge to <code>main</code>"]
    Build("<u>CI/CD</u>\nVerify code, build/upload docker images\ntagged with <code>latest</code> and the commit hash")
    IdxWorker("<u>Indexer worker</u>\nNew EC2 instances pull\nthe <code>latest</code> tagged\nimage next time they run")
    RevertRollback[Roll back by merging a revert\nof the broken code to main] ---> Build

    Merge ---> Build

    Build --> IdxWorker o--o RevertRollback
```

### Ingestion server

As noted above, while there are separate ingestion server instances named
"staging" and "production", they are rarely configured to run separate code.

```{mermaid}
flowchart TD
    Merge["Merge to <code>main</code>"]
    Build("<u>CI/CD</u>\nVerify code, build/upload docker images\ntagged with <code>latest</code> and the commit hash")
    Publish[Publish GitHub Release]
    Tag("Tag the <code>latest</code> ingestion server\n docker image with the release tag based\non the GitHub Release title")
    Deploy["<u>Infrastructure repository</u>\nAdd the release tag to the ingestion servers's\nTerraform variables and run terraform apply"]
    ApplyRollback[Redo the previous step, but with the last\nknown working production image tag]

    Merge --> Build --> Publish --> Tag --> Deploy o--o|Rollback| ApplyRollback
```

## Environment variables

Without exception, the specific environment variable configuration for each
application's live environment is stored and managed in the
`openverse-infrastructure` repository, as either Ansible or Terraform
configuration code.

When deploying code that depends on a new or updated environment variable, you
must follow the process below _before_ that code is deployed. This is the only
way to make the new or updated variable available for the code the depends on
it. This applies to all applications. Please see the
[zero-downtime deployments document's section on environment variables for an in-depth explanation of the rationale behind this process](/general/zero_downtime_database_management.md#environment-variables).

First, add or update the environment variables in the Terraform or Ansible
configuration for the application.

If an existing variable is just being updated with a new value, redeploy the
current version of the application.

If you are adding a new environment variable, follow the regular release and
deployment process for the application.
