from abc import abstractmethod
from elasticsearch_dsl import DocType, Date, Boolean, Text, Integer, Nested


class SyncableDocType(DocType):
    # Aggregations can't be performed on the _id meta-column, which necessitates
    # copying it to this column in the doc. Aggregation is used to find the last
    # document inserted into Elasticsearch
    pg_id = Integer()

    @staticmethod
    @abstractmethod
    def postgres_to_elasticsearch(row, schema):
        """
        Children of this class must have a function mapping a Postgres model
        to an Elasticsearch document.

        :param row: A tuple representing a row in Postgres.
        :param schema: A map of each field name to its position in the row.
        :return:
        """
        raise NotImplemented(
            'Model is missing Postgres -> Elasticsearch translation.'
        )


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
    license_version = Text()
    foreign_landing_url = Text(index="not_analyzed")
    removed_from_source = Boolean()
    meta_data = Nested()

    class Meta:
        index = 'image'

    @staticmethod
    def postgres_to_elasticsearch(row, schema):
        return Image(
            _id=row[schema['id']],
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
            removed_from_source=row[schema['removed_from_source']],
            meta_data=row[schema['meta_data']],
        )


# Table name -> Elasticsearch model
postgres_table_to_elasticsearch_model = {
    'image': Image
}
