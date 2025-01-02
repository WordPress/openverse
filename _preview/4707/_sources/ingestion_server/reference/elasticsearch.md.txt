# Elasticsearch and Indexing

There is a multi-step process for copying data from an upstream source and
loading it into the Openverse API using ingestion server:

1. The data is copied from the upstream catalog database and into the downstream
   API database into new tables.
2. Data from the downstream API database gets indexed in Elasticsearch in new
   indexes.
3. Aliases in the API database and Elasticsearch are updated to point to the new
   tables and indexes. We refer to this as "promotion".
4. The previous API tables and Elasticsearch indexes are deleted.

Performance depends on the size of the target Elasticsearch cluster, database
throughput, and bandwidth available to the ingestion server. The primary
bottleneck is indexing to Elasticsearch.

## How indexing works

![How indexing works](./howitworks.png)
