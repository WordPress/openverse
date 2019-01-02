# Elasticsearch Syncer

## Introduction
Elasticsearch Syncer is a daemon that automatically replicates data from a database into Elasticsearch. It polls the database and Elasticsearch at a set interval to find the largest primary key ID in each datastore. If the highest primary key in the database is not present in Elasticsearch, a bulk insert is performed to synchronize Elasticsearch. Because parallel calls are made to the bulk insert API, this is a fast operation.

Performance is dependent on the size of the target Elasticsearch cluster and the complexity of the document being indexed. Informal tests indicate that the daemon can index 10,000,000 complex documents per hour on a single node Elasticsearch cluster, where a "complex document" is one with multiple analyzed fields, nested documents, and many non-analyzed fields. Simple documents can be indexed at a higher rate.

![How it works](https://raw.githubusercontent.com/creativecommons/cccatalog-api/syncer_tests_and_docs/es_syncer/howitworks.png)
## Configuration
All configuration is performed via environment variables.

#### Required
* **COPY_TABLES**: A comma-separated list of database tables that should be replicated to Elasticsearch. **Example**: image,text

* ELASTICSEARCH_URL
* ELASTICSEARCH_PORT
* DATABASE_HOST
* DATABASE_USER
* DATABASE_PASSWORD
* DATABASE_NAME
* DATABASE_PORT

#### Optional
* **DB_BUFFER_SIZE**: The number of rows to load from the database at once while replicating. **Default**: 100000

To access a cluster on AWS, define these additional environment variables.
* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY
* AWS_REGION

## Mapping database tables to Elasticsearch
In order to synchronize a given table to Elasticsearch, the following requirements must be met:
* The database table must have an autoincrementing integer primary key named `id`.
* A SyncableDoctype must be defined in `es_syncer/elasticsearch_models`. The SyncableDoctype must implement the function `database_row_to_elasticsearch_model`.
* The table name must be mapped to the corresponding Elasticsearch SyncableDoctype in `database_table_to_elasticsearch_model` map.

Example from `es_syncer/elasticsearch_models.py`:
```
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
            tags=row[schema['tags_list']],
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
