# Mapping database tables to Elasticsearch

In order to synchronize a given table to Elasticsearch, the following
requirements must be met:

- The database table must have an autoincrementing integer primary key named
  `id`.
- A SyncableDoctype must be defined in `es_syncer/elasticsearch_models`. The
  SyncableDoctype must implement the function
  `database_row_to_elasticsearch_model`.
- The table name must be mapped to the corresponding Elasticsearch
  SyncableDoctype in `database_table_to_elasticsearch_model` map.

Example from `es_syncer/elasticsearch_models.py`:

```python
class Image(SyncableDocType):
    title = Text(analyzer="english")
    identifier = Text(index="not_analyzed")
    creator = Text()
    creator_url = Text(index="not_analyzed")
    tags = Text(multi=True)
    created_on = Date()
    url = Text(index="not_analyzed")
    thumbnail = Text(index="not_analyzed")
    provider = Text(index="not_analyzed")
    source = Text(index="not_analyzed")
    license = Text(index="not_analyzed")
    license_version = Text("not_analyzed")
    foreign_landing_url = Text(index="not_analyzed")
    meta_data = Nested()

    class Meta:
        index = 'image'

    @staticmethod
    def database_row_to_elasticsearch_doc(row, schema):
        return Image(
            pg_id=row[schema['id']],
            title=row[schema['title']],
            identifier=row[schema['identifier']],
            creator=row[schema['creator']],
            creator_url=row[schema['creator_url']],
            created_on=row[schema['created_on']],
            url=row[schema['url']],
            thumbnail=row[schema['thumbnail']],
            provider=row[schema['provider']],
            source=row[schema['source']],
            license=row[schema['license']],
            license_version=row[schema['license_version']],
            foreign_landing_url=row[schema['foreign_landing_url']],
            meta_data=row[schema['meta_data']],
        )


# Table name -> Elasticsearch model
database_table_to_elasticsearch_model = {
    'image': Image
}
```