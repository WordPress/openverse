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

### Index constraints (catalog)

### Batched update

### Cleanup, filtering, & deleted media removal

### Index constraints (API)

### ES index creation & filtering

### Dead link filtering
