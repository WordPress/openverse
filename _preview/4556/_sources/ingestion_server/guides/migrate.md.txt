# Index migration runbook

From time to time, we will need to update our Elasticsearch indices. These
modifications can be classified into two broad-strokes categories, depending on
whether the changes affect the main consumer of the indices, the API.

## Migration types

### API-free

These changes are safe modifications to the ES schema that do not affect the
API. As such they do not need any migration process. Examples:

- addition of new fields or subfields
- removal of fields that are not referenced or used by the API
- changing the type to another compatible type (like `text` &harr; `keyword` )

For API-free changes, we deploy the ingestion server and perform one of the two:

- standard data-refresh (either triggered manually or as scheduled)
- [manual index upgrade](/ingestion_server/guides/upgrade.md)

The indices will be updated to the new schema and will be made available to the
API.

### API-involved

These changes are modifications to fields that already are in use by the API and
involve code changes in both the ingestion server and the API. Examples:

- removal of a field
- changing the type to an incompatible type
- renaming of a field

Such kinds of changes need us to precisely deploy the API in coordination with
the promotion of new index because of these reasons:

- If the API deployment lags behind index promotion, the old field that the API
  uses will disappear.
- If the API deployment leads ahead of index promotion, the new field the API
  uses will not be present.

This runbook documents guidelines and processes for API-involved migrations.

Our goal is to break down an API-involved change into multiple small, atomic
changes with each step affecting at most one of the ingestion server or the API
and ensuring that the API and ES remain compatible throughout the process.

## Pull request guidelines

A change that involves modification to the ES index as well as its usage in the
API requires at least three steps, each associated with exactly one PR that
modifies exactly one of the ingestion server or the API to allow them to be
deployed independently.

1. Change the ES index mapping in the ingestion server. Ensure that the change
   is purely additive, keeping the old fields unchanged and creating new fields
   that contain the data the API will need.

   This PR should make changes only within the `ingestion_server/` directory,
   more specifically the following two files concerned with ES mappings and
   document schemas:

   - [`es_mappings.py`](https://github.com/WordPress/openverse/tree/main/ingestion_server/ingestion_server/es_mapping.py)
   - [`elasticsearch_models.py`](https://github.com/WordPress/openverse/tree/main/ingestion_server/ingestion_server/elasticsearch_models.py)

2. Update the API code to reference and use the new ES fields added in the
   previous step. Ensure that the old fields become unreferenced.

   The PR should make changes only within the `api/` directory.

3. Change the ES index mapping in the ingestion server to remove the old,
   now-unreferenced fields.

   Like PR number 1, this PR should also make changes only within the
   `ingestion_server/` directory.

```{tip}
Get the PRs reviewed in advance so that the entire process has been vetted by
the team and there are no surprises or delays when the plans have been set into
motion.
```

```{caution}
Each PR in the chain should branch from, and point to, its predecessor in the
chain so that CI continues to pass for each PR.
```

### Example

Assume we have a field `foo` with type `text` in the index. It has a subfield
`keyword` with type `keyword`. The API uses `foo.keyword` for all purposes. We
want the `foo` field to have type `keyword` and for the API to use `foo` instead
of `foo.keyword`. To accomplish this without downtime, we need three PRs:

1. Changing `foo` to type `keyword` would be an API-free change because it is a
   type change between two compatible types and does not affect the nested field
   `foo.keyword` that is in use by the API. Technically the outer field can be
   assumed to be "new" because it was not being used at all.

2. Then we make an API change to use `foo` directly instead of `foo.keyword`.
   Any other accommodations to make use of `foo` can be made in this step. In
   this case `foo` will be the same as `foo.keyword` so no other changes will be
   needed.

3. Removal of the `foo.keyword` field would now also be an API-free change
   because the field would no longer be in use.

## Migration process

The entire migration process can be classified into 3 phases.

```{mermaid}
flowchart TD
  subgraph api[API]
    API
  end

  subgraph elasticsearch[Elasticsearch]
    image --> image-old
    image-filtered --> image-old-filtered
    audio --> audio-old
    audio-filtered --> audio-old-filtered
  end

  API --> image
  API --> image-filtered
  API --> audio
  API --> audio-filtered
```

### Create the new fields

1. Merge [PR number 1](#pull-request-guidelines).
2. Perform a [manual index upgrade](/ingestion_server/guides/upgrade.md).

At the close of this phase we have all the new information for the API to use.

```{mermaid}
flowchart TD
  subgraph api[API]
    API
  end

  subgraph elasticsearch[Elasticsearch]
    image -.-> image-old
    image-filtered -.-> image-old-filtered
    audio -.-> audio-old
    audio-filtered -.-> audio-old-filtered
    image --> image-mid
    image-filtered --> image-mid-filtered
    audio --> audio-mid
    audio-filtered --> audio-mid-filtered
  end

  API --> image
  API --> image-filtered
  API --> audio
  API --> audio-filtered

  style image-old opacity:0.3
  style image-old-filtered opacity:0.3
  style audio-old opacity:0.3
  style audio-old-filtered opacity:0.3
```

### Use the new fields instead of the old

1. Merge [PR number 2](#pull-request-guidelines). This will automatically deploy
   the API to staging.
2. Verify that the staging API continues to work.
3. [Deploy the API](/api/guides/deploy.md) to production.
4. Verify that the production API continues to work.

At the close of this phase the API is exclusively using the new fields and the
old ones have become unreferenced.

```{mermaid}
flowchart TD
  subgraph api[API]
    old[API]
    new[New API]
  end

  subgraph elasticsearch[Elasticsearch]
    image --> image-mid
    image-filtered --> image-mid-filtered
    audio --> audio-mid
    audio-filtered --> audio-mid-filtered
  end

  old -.-> image
  old -.-> image-filtered
  old -.-> audio
  old -.-> audio-filtered
  new --> image
  new --> image-filtered
  new --> audio
  new --> audio-filtered

  style old opacity:0.3
```

### Remove the old fields

1. Merge [PR number 3](#pull-request-guidelines).
2. Perform a [manual index upgrade](/ingestion_server/guides/upgrade.md).

```{mermaid}
flowchart TD
  subgraph api[API]
    new[New API]
  end

  subgraph elasticsearch[Elasticsearch]
    image -.-> image-mid
    image-filtered -.-> image-mid-filtered
    audio -.-> audio-mid
    audio-filtered -.-> audio-mid-filtered
    image --> image-final
    image-filtered --> image-final-filtered
    audio --> audio-final
    audio-filtered --> audio-final-filtered
  end

  new --> image
  new --> image-filtered
  new --> audio
  new --> audio-filtered

  style image-mid opacity:0.3
  style image-mid-filtered opacity:0.3
  style audio-mid opacity:0.3
  style audio-mid-filtered opacity:0.3
```

You're done!

```{mermaid}
flowchart TD
  subgraph api[API]
    new[New API]
  end

  subgraph elasticsearch[Elasticsearch]
    image --> image-final
    image-filtered --> image-final-filtered
    audio --> audio-final
    audio-filtered --> audio-final-filtered
  end

  new --> image
  new --> image-filtered
  new --> audio
  new --> audio-filtered
```
