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

%% DBs
A[(API DB)]
ES[(Elasticsearch)]

%% Graph definitions
    subgraph AF [Airflow]
    P{{Provider}} --> M(MediaStore):::ETL
    M --> T{{TSV}}
    T --> IC1(Index constraints):::ETL
    IC1 --> C[(Catalog DB)]
    C --> B(Batched update):::ETL --> C
    end

    subgraph IS [Ingestion Server]
    %% ETLs
    ING(Deleted media removal):::ETL
    IC2(Index constraints):::ETL
    ESF(Index creation & deleted media filtering):::ETL

    C --> ING
    ING --> TT[(Temp Table)]
    TT --> CF(Cleaning & filtering):::ETL --> TT
    end

    TT --> A
    ESF --> ES
    A --> IC2 --> A
    A --> ESF
    subgraph DJA [Django API]
    %% ETLs
    DL(Dead link filtering):::ETL
    AS(API seralizers):::ETL
    R[(Redis)] --> DL --> R
    end

    %% Connections for the API
    ES --> DL
    DL --> A
    A --> AS

    subgraph F [Frontend]
    ATG(Attribution generation):::ETL
    end

    %% External connections
    AS --> ATG
    AS --> CL[External Client]
    ATG --> CL

%% Style definitions
    style AF fill:#00c7d4
    style IS fill:#ffc83d
    style DJA fill:orange
    style F fill:lightgreen
    classDef ETL fill:#fa7def


%% Reference definitions
    click M "#mediastore-transformations"
    click IC1 "#index-constraints-catalog"
    click B "#batched-update"
    click ING "#deleted-media-removal"
    click CF "#cleaning-filtering"
    click IC2 "#index-constraints-api"
    click ESF "#es-index-creation-filtering"
    click DL "#dead-link-filtering"
    click AS "#api-serializers"
    click ATG "#attribution-generation"
```

```{note}
The `Temp Table` referenced above is actually a table within the API database that
gets swapped for the live production table once the processing steps on it are
complete. This prevents us from having to operate on live data.
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

### Deleted media removal

Presently, we
[filter out deleted media from each of the primary media tables](https://github.com/WordPress/openverse/blob/b4ab20cdb220f442949d9c06a99ced5e80c1e1e1/ingestion_server/ingestion_server/queries.py#L173-L182)
while the `SELECT {columns} FROM {upstream_table}` query is being run.

### Cleaning & filtering

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
database into Elasticsearch. In addition to the filtering of
[sensitive terms using two separate indices](/catalog/reference/DAGs.md#create_filtered_media_type_index)
and
[deleted media](https://github.com/WordPress/openverse/blob/b1a1f6eb711a3d6999b2d2bbe4b8cc1d1435c3fa/ingestion_server/ingestion_server/indexer.py#L121),
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
links from being surfaced in API results. This process both reads from and
writes to Redis, where information about valid/invalid URLs is cached.

The full set of dead link logic can be found in the
[`check_dead_link` module](https://github.com/WordPress/openverse/tree/main/api/api/utils/check_dead_links/__init__.py).

### API serializers

An additional transformation occurs after a record is retrieved from the
database (and once it has been validated by the dead link filtering). This step
includes any transformations that required in hydrating the database record and
converting it into a JSON object which is sent to the requester.

Serializations can be found
[in the codebase under `api/api/serializers`](https://github.com/WordPress/openverse/tree/main/api/api/serializers).

### Attribution generation

The frontend also modifies results before displaying them to a user. This
includes generating attributions in multiple formats. The full attribution
generation code
[can be found in `attribution-html.ts`](https://github.com/WordPress/openverse/tree/main/frontend/src/utils/attribution-html.ts).

## Proposed

The projects #430, #431, and #3925 all intend to modify the above process. Below
is the diagram of what this process might look like after all steps are taken.
Most blocks reference the same sections above, with the exception being
[Deleted media & tag filtering](#deleted-media--tag-filtering).

```{mermaid}
flowchart TD

%% DBs
A[(API DB)]
ES[(Elasticsearch)]

%% Graph definitions
    subgraph AF [Airflow]
    %% ETLs
    M(MediaStore):::ETL
    IC1(Index constraints):::ETL
    B(Batched update):::ETL
    ING(Deleted media & tag filtering):::ETL
    IC2(Index constraints):::ETL
    ESF(Index creation & deleted media filtering):::ETL

    P{{Provider}} --> M
    M --> T{{TSV}}
    T --> IC1
    IC1 --> C[(Catalog DB)]
    C --> B --> C
    C --> ING
    end

    %% Connections for the data refresh
    ESF --> ES
    ING --> A
    A --> IC2 --> A
    A --> ESF

    subgraph DJA [Django API]
    %% ETLs
    DL(Dead link filtering):::ETL
    AS(API seralizers):::ETL
    R[(Redis)] --> DL --> R
    end

    %% Connections for the API
    ES --> DL
    DL --> A
    A --> AS

    subgraph F [Frontend]
    ATG(Attribution generation):::ETL
    end

    %% External connections
    AS --> ATG
    AS --> CL[External Client]
    ATG --> CL

%% Style definitions
    style AF fill:#00c7d4,margin-left:12em
    style DJA fill:orange
    style F fill:lightgreen
    classDef ETL fill:#fa7def

%% Reference definitions
    click M "#mediastore-transformations"
    click IC1 "#index-constraints-catalog"
    click B "#batched-update"
    click ING "#deleted-media-tag-filtering"
    click IC2 "#index-constraints-api"
    click ESF "#es-index-creation-filtering"
    click DL "#dead-link-filtering"
    click AS "#api-serializers"
    click ATG "#attribution-generation"
```

### Deleted media & tag filtering

The data normalization project (#430) intends to remove the
[cleanup steps](#cleaning--filtering) from the ingestion server. Subsequent
ingestion server removal project (#3925) will remove the ingestion server
entirely. This will be fleshed out more as part of #4456, but the _filtering_
steps (e.g. demographic tags, tags below a confidence level, etc.) will be
present within the pipeline prior to the API indexing values into Elasticsearch.
