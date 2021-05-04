# Ingestion Server

## Introduction
Ingestion Server is a small private API for copying data from an upstream source and loading it into the CC Catalog API. This is a two step process:
1. The data is copied from the upstream CC Catalog database and into the downstream API database.
2. Data from the downstream API database gets indexed in Elasticsearch.

For example, let's say that I want to download and index all new images.
`http POST ingestion.private:8001/task <<<'{"model": "image", "action": "INGEST_UPSTREAM"}'`

Performance is dependent on the size of the target Elasticsearch cluster, database throughput, and bandwidth available to the ingestion server. The primary bottleneck is indexing to Elasticsearch.

## How Indexing Works
![How indexing works](https://github.com/wordpress/openverse-api/blob/master/ingestion_server/howitworks.png)

## Safety and security considerations
The server has been designed to fail gracefully in the event of network interruptions, full disks, etc. If a task fails to complete successfully, the whole process is rolled back with zero impact to production.

The server is designed to be run in a private network only. You must not expose the private Ingestion Server API to the public internet.

## Running the tests
This runs a simulated environment in Docker containers and ensures that ingestion is working properly.
```
mkvirtualenv venv
source venv/bin/activate
python test/integration_tests.py
```
Set `ENABLE_DETAILED_LOGS` to `True` if more information is needed about the failing test.

## Configuration
All configuration is performed through environment variables.

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
