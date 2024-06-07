# Extract-Transform-Load flows

The diagrams below show how data flows through Openverse, and the various
transformation steps that might happen at each stage.

**Guide**:

- **Blue boxes** represent places where data sits at rest.
- **Purple boxes** represent transformation steps. Each box links to a longer
  description below.

## Current flow

```{mermaid}
flowchart TD

%% Graph definitions
    subgraph AF [Airflow]
    P{{Provider}} --> M(MediaStore):::ETL
    M --> T{{TSV}}
    T --> IC1(Index constraints):::ETL
    IC1 --> C[(Catalog DB)]
    C --> B(Batched update):::ETL --> C
    end

    subgraph IS [Ingestion Server]
    C --> ING(Cleanup, filtering, & deleted media removal):::ETL
    ING --> A[(API DB)]
    A --> IC2(Index constraints):::ETL --> A
    A --> ESF(Index creation & deleted media filtering):::ETL
    ESF --> ES[(Elasticsearch)]
    end

    A --> DL(Dead link filtering):::ETL
    DL --> CL[Client]
    CL --> F[Frontend]

%% Style definitions
    style IS fill:#ffc83d
    style AF fill:#00c7d4,margin-left:12em
    classDef ETL fill:#fa7def

%% Reference definitions
    click M "#mediastore-transformations"
    click IC1 "#index-constraints-catalog"
    click B "#batched-update"
    click ING "#cleanup-filtering-deleted-media-removal"
    click IC2 "#index-constraints-api"
    click ESF "#es-index-creation-filtering"
    click DL "#dead-link-filtering"
```

### MediaStore transformations

These transformations occur as part of the provider ingestion scripts as records
are being saved from the provider's API response into a TSV. The exhaustive list
of shared transformations can be found
[in the `MediaStore` definition](https://github.com/WordPress/openverse/tree/main/catalog/dags/common/storage/media.py),
as well as individual transformations for
[images](https://github.com/WordPress/openverse/tree/main/catalog/dags/common/storage/image.py)
and
[audio](https://github.com/WordPress/openverse/tree/main/catalog/dags/common/storage/image.py).

A non-exhaustive list includes:

- Filtering out tags based on licenses or tags which add no useful search
  information
- Removing integer values that would exceed the Postgres integer maximum
- Validating filetype and collapsing common types
- Formatting tags appropriately (see
  [the media properties definition](catalog.md#tags))
- Enriching `meta_data` the license URLs
- Validating URLs
- Determining `source` is not explicitly provided

### Index constraints (catalog)

As the data from a saved provider TSV gets inserted into the database, it also
must be compliant with the existing indices. The indices for each primary media
table can be found here:
[image](https://github.com/WordPress/openverse/tree/main/docker/upstream_db/0003_openledger_image_schema.sql),
[audio](https://github.com/WordPress/openverse/tree/main/docker/upstream_db/0006_openledger_audio_schema.sql).
In general, these include:

- Uniqueness on `provider` + `foreign_identifier` combination
- Uniqueness on `identifier`
- Uniqueness on `url`

### Batched update

Updates against the catalog database may also be initiated using the
[batched update DAG](/catalog/reference/DAGs.md#batched-update-dag). These
updates may be automated (such as the popularity refresh process) or manual
(such as data correction).

### Cleanup, filtering, & deleted media removal

During the ingestion server's data refresh process, a series of cleanup and
filtering steps occur. These steps happen in two places:

1. During the copy from the upstream database into the temporary table within
   the API database.
2. After the copy is complete by processing chunks of records in the temporary
   table and updating values that were changed during the process.

#### During the copy

Presently, we
[filter out deleted media from each of the primary media tables](https://github.com/WordPress/openverse/blob/b4ab20cdb220f442949d9c06a99ced5e80c1e1e1/ingestion_server/ingestion_server/queries.py#L173-L182)
while the `SELECT {columns} FROM {upstream_table}` query is being run.

#### After the copy

We also iterate through the copied data in batches and update the values in the
new table based on several cleaning/filtering steps (all of which can be seen in
the ingestion server's
[cleanup definitions](https://github.com/WordPress/openverse/tree/main/ingestion_server/ingestion_server/cleanup.py)).
At present, these operations include:

- Ensuring URLs have a scheme
- Filtering tags out (similar to
  [the `MediaStore` transformations](#mediastore-transformations))
- Filtering machine-generated tags below a certain confidence value

### Index constraints (API)

Once the ingestion server data is copied and cleaned/filtered, the API indices
are applied to the new table. There are several more indices on the API than on
the catalog database, many of which are for query optimization. These include
(all are `btree` unless specified):

- Category
- Foreign identifier
- Last synced with source
- Provider
- Source

### ES index creation & filtering

An additional filtering step happens when the records are indexed from the API
database into Elasticsearch. In addition to the
[filtering of sensitive terms using two separate indices](/catalog/reference/DAGs.md#create_filtered_media_type_index),
there are also transformations that occur when constructing the ES documents.
The
[exhaustive list can be seen in the `elasticsearch_models` module](https://github.com/WordPress/openverse/tree/main/ingestion_server/ingestion_server/elasticsearch_models.py),
which includes:

#### Common

- Computing the authority boost
- Computing the popularity
- Parsing a description from the media, if available
- Parsing tags
- Determining the `mature` field

#### Images

- Computing the aspect ratio
- Computing the size

#### Audio

- Computing the duration

### Dead link filtering

When records are retrieved from Elasticsearch, they also go through a process
called "dead link filtering". This operation attempts to remove links to media
which the API may have trouble accessing in order to prevent dead or invalid
links from being surfaced in API results. The full set of dead link logic can be
found in the
[`check_dead_link` module](https://github.com/WordPress/openverse/tree/main/api/api/utils/check_dead_links/__init__.py).
