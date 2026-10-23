# Mapping database tables to Elasticsearch

In order to synchronize a given table to Elasticsearch, the following
requirements must be met:

- The database table must have an autoincrementing integer primary key named
  `id`.
- A SyncableDoctype must be defined in `ingestion_server/elasticsearch_models`.
  Refer to `SyncableDocType`'s doc string for required subclass implementation
  details.
- The table name must be mapped to the corresponding Elasticsearch
  SyncableDoctype in `media_type_to_elasticsearch_model` map.

See existing media type definitions in `ingestion_server/elasticsearch_models`
for examples.
