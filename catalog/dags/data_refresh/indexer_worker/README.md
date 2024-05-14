# Indexer Worker

An indexer worker serves a small Falcon API which can be used to perform a chunk
of a "reindexing task", whereby records from a downstream table are converted
into ES documents and uploaded to an Elasticsearch index in bulk. The data
refresh orchestrates multiple indexer workers, each of which performs a portion
of the total reindexing.

Further reading:

- [[IP] Removal of the ingestion server](https://docs.openverse.org/projects/proposals/ingestion_server_removal/20240328-implementation_plan_ingestion_server_removal.html)
