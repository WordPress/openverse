from abc import abstractmethod
from elasticsearch_dsl import Date, Text, Integer, Nested, Keyword, DocType


class SyncableDocType(DocType):
    """
    Represents tables in the source-of-truth that will be replicated to
    Elasticsearch.
    """
    # Aggregations can't be performed on the _id meta-column, which necessitates
    # copying it to this column in the doc. Aggregation is used to find the last
    # document inserted into Elasticsearch
    pg_id = Integer()

    @staticmethod
    @abstractmethod
    def database_row_to_elasticsearch_doc(row, schema):
        """
        Children of this class must have a function mapping a Postgres model
        to an Elasticsearch document.

        :param row: A tuple representing a row in Postgres.
        :param schema: A map of each field name to its position in the row.
        :return:
        """
        raise NotImplemented(
            'Model is missing database -> Elasticsearch translation.'
        )


class Image(SyncableDocType):
    title = Text(analyzer="english")
    identifier = Keyword()
    creator = Text()
    creator_url = Keyword()
    tags = Text(multi=True)
    created_on = Date()
    url = Keyword()
    thumbnail = Keyword()
    provider = Text(analyzer="keyword")
    source = Keyword()
    license = Keyword()
    license_version = Keyword()
    foreign_landing_url = Keyword()
    meta_data = Nested()

    class Index:
        name = 'image'

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
