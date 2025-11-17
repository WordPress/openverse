# Docker jobs

## `determine-images`

Determines which images to build and publish as a part of the workflow run. To
speed up the workflow and avoid wasteful resource consumption, only a subset of
all images are built by the workflow and a only subset of those images are
published to GHCR. This job determines those images.

| Change             | `upstream_db` | `catalog` | `ingestion_server` | `api` | `api_nginx` | `frontend` |
| ------------------ | ------------- | --------- | ------------------ | ----- | ----------- | ---------- |
| `catalog`          | 🛠️            | 🚀        |                    |       |             |            |
| `ingestion_server` | 🛠️            |           | 🚀                 | 🛠️    |             |            |
| `api`              | 🛠️            |           | 🛠️                 | 🚀    | 🚀          |            |
| `frontend`         |               |           |                    |       |             | 🚀         |

🚀 denotes that the image is published to GHCR. 🛠️ denotes that the image is
built but not published.

```{note}
The `upstream_db` image is only built here and reused in other workflows for
convenience and speed, it is never published.
```

**Outputs:**

The `build_matrix` and `publish_matrix` conventionally use the name singular
name "image" for the field because inside the steps
[`matrix.image`](https://docs.github.com/en/actions/learn-github-actions/contexts#matrix-context)
can be used to refer to the current matrix entry.

```typescript
interface Output {
  do_build: "true" | "false" // whether one or more images are to be built
  build_matrix: {
    image: (
      | "upstream_db"
      | "catalog"
      | "ingestion_server"
      | "api"
      | "api_nginx"
      | "frontend"
    )[] // the names of the image to be built
    include: (
      | { image: "upstream_db"; context: "docker/upstream_db"; target: "db" }
      | { image: "catalog"; context: "catalog"; target: "cat" }
      | {
          image: "ingestion_server"
          context: "ingestion_server"
          target: "ing"
        }
      | { image: "api"; context: "api"; target: "api" }
      | { image: "api_nginx"; context: "api"; target: "nginx" }
    )[] // additional information about images to be built
  }
  do_publish: "true" | "false" // whether one or more images are to be published
  publish_matrix: {
    image: ("catalog" | "ingestion_server" | "api" | "api_nginx" | "frontend")[] // the name of the image to be published
  }
}
```

## `build-images`

Builds images as dictated by the [`determine-images`](#determine-images) job.
Since the images are built in a matrix, some image-specific steps are
conditionally run using an `if` expression. Since any unused Docker build
arguments have no effect, the job simply populates all build arguments needed by
all images.

Images built by this job are published as `.tar` artifacts and can be loaded
into other jobs that need them using the
[`load-img`](/meta/ci_cd/actions.md#load-img) action.

This job is only run if there is at least one image needed to build, based on
the `do_build` output of the [`determine-images`](#determine-images) job.
