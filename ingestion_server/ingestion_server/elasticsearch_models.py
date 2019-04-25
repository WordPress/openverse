from elasticsearch_dsl import Date, Text, Integer, Nested, Keyword, DocType


"""
Provides an ORM-like experience for accessing data in Elasticsearch.

Note the actual schema for Elasticsearch is defined in es_mapping.py; any
low-level changes to the index must be represented there as well.
"""


class SyncableDocType(DocType):
    """
    Represents tables in the source-of-truth that will be replicated to
    Elasticsearch.
    """
    # Aggregations can't be performed on the _id meta-column, which necessitates
    # copying it to this column in the doc. Aggregation is used to find the last
    # document inserted into Elasticsearch
    id = Integer()

    @staticmethod
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
    view_count = Integer()

    class Index:
        name = 'image'

    @staticmethod
    def database_row_to_elasticsearch_doc(row, schema):
        def _parse_detailed_tags(json_tags):
            if json_tags:
                parsed_tags = []
                for tag in json_tags:
                    if 'name' in tag:
                        parsed_tag = {'name': tag['name']}
                        if 'accuracy' in tag:
                            parsed_tag['accuracy'] = tag['accuracy']
                        parsed_tags.append(parsed_tag)
                return parsed_tags
            else:
                return None

        return Image(
            _id=row[schema['id']],
            id=row[schema['id']],
            title=row[schema['title']],
            identifier=row[schema['identifier']],
            creator=row[schema['creator']],
            creator_url=row[schema['creator_url']],
            tags=_parse_detailed_tags(row[schema['tags']]),
            created_on=row[schema['created_on']],
            url=row[schema['url']],
            thumbnail=row[schema['thumbnail']],
            provider=row[schema['provider']],
            source=row[schema['source']],
            license=row[schema['license']],
            license_version=row[schema['license_version']],
            foreign_landing_url=row[schema['foreign_landing_url']],
            meta_data=None,
            view_count=row[schema['view_count']],
        )


# Table name -> Elasticsearch model
database_table_to_elasticsearch_model = {
    'image': Image
}
