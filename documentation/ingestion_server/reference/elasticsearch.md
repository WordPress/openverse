# Elasticsearch and Indexing

There is a two-step process for copying data from an upstream source
and loading it into the Openverse API using ingestion server:

1. The data is copied from the upstream catalog database and into the downstream
   API database.
2. Data from the downstream API database gets indexed in Elasticsearch.

Performance is dependent on the size of the target Elasticsearch cluster,
database throughput, and bandwidth available to the ingestion server. The
primary bottleneck is indexing to Elasticsearch.

## How indexing works

![How indexing works](./howitworks.png)