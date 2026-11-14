# Ingestion server API

The ingestion server exposes an API at the `/task` endpoint to schedule various
tasks and get updates about their status and progress.

New tasks can be created using the `POST` method and a payload as described
below. The response for this request provides an endpoint (containing a task's
unique ID) that can be used to retrieve the task information using the `GET`
method.

## REINDEX

If a complete data-refresh is not required, a new index can be created using the
`REINDEX` action. This action will create a new index for the given media type
using the data from the API database. A suffix can be provided for the index
otherwise a random UUID will be used.

### Body

```typescript
{
  model: "image" | "audio"
  action: "REINDEX"
  index_suffix: string
}
```

### Example

```console
$ curl \
  -X POST \
  -H 'Content-Type: application/json' \
  -d '{"model": "image", "action": "REINDEX", "index_suffix": "20231106"}' \
  http://localhost:8001/task
```

## CREATE_AND_POPULATE_FILTERED_INDEX

This endpoint creates a filtered index for a media type out of an existing
index. A `REINDEX` job must be followed by this job to ensure that the new index
has an associated filtered index as well before we promote it.

### Body

```typescript
{
  model: "image" | "audio"
  action: "CREATE_AND_POPULATE_FILTERED_INDEX"
  destination_index_suffix: string
}
```

```{caution}
Destination suffix here implies the suffix of the existing unfiltered index.
The filtered index will be created with "-filtered" appended to the destination
suffix.
```

### Example

```console
$ curl \
  -X POST \
  -H 'Content-Type: application/json' \
  -d '{"model": "image", "action": "CREATE_AND_POPULATE_FILTERED_INDEX", "destination_index_suffix": "20231106"}' \
  http://localhost:8001/task
```

## POINT_ALIAS

This endpoint maps the index to a given alias. When an index is aliased to the
name of the media type (`image` or `audio`) or name + "-filtered", it becomes
the default or filtered index for that media type respectively.

### Body

```typescript
{
  model: "image" | "audio"
  action: "POINT_ALIAS"
  index_suffix: string
  alias: string // should be model or model + "-filtered"
}
```

### Example

```console
$ curl \
  -X POST \
  -H 'Content-Type: application/json' \
  -d '{"model": "image", "action": "POINT_ALIAS", "index_suffix": "20231106", "alias": "image-filtered"}' \
  http://localhost:8001/task
```

## DELETE_INDEX

This endpoint deletes the given index for a given media type.

```{danger}
Index deletion is an irreversible destructive operation. Please ensure that you
do not delete an index that is currently in use as the default or filtered index
for a media type.
```

### Body

```typescript
{
  model: "image" | "audio"
  action: "DELETE_INDEX"
  index_suffix: string
}
```

### Example

```console
$ curl \
  -X POST \
  -H 'Content-Type: application/json' \
  -d '{"model": "image", "action": "DELETE_INDEX", "index_suffix": "20231106"}' \
  http://localhost:8001/task
```
