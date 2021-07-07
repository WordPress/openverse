from enum import Enum, auto
from elasticsearch_dsl import Integer, DocType, Field
from ingestion_server.categorize import get_categories
from ingestion_server.authority import get_authority_boost

"""
Provides an ORM-like experience for accessing data in Elasticsearch.

Note the actual schema for Elasticsearch is defined in es_mapping.py; any
low-level changes to the index must be represented there as well.
"""


class RankFeature(Field):
    name = 'rank_feature'


def _verify_rank_feature(value, low, high):
    """
    Rank features must be a positive non-zero float. Our features are scaled
    from 0 to 100 for fair comparison.
    """
    if value is None or value == 0:
        return None
    ceiling = min(value, high)
    floor = max(low, ceiling)
    return floor


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


class Media(SyncableDocType):
    """
    Represents a media object in Elasticsearch. Note that actual mappings are defined
    in `ingestion_server.es_mapping`.
    """

    class Index:
        name = 'media'

    @staticmethod
    def database_row_to_elasticsearch_doc(row, schema):
        raise NotImplemented(
            'Model is missing database row -> Elasticsearch schema translation.'
        )

    @staticmethod
    def parse_description(metadata_field):
        """
        Parse the description field from the metadata if available.

        Limit to the first 2000 characters.
        """
        try:
            if 'description' in metadata_field:
                return metadata_field['description'][:2000]
        except TypeError:
            return None

    @staticmethod
    def get_extension(url):
        extension = url.split('.')[-1].lower()
        if '/' in extension or extension is None:
            return None
        else:
            return extension

    @staticmethod
    def get_license_url(meta_data):
        """
        If the license_url is not provided, we'll try to generate it elsewhere
        from the `license` and `license_version`.
        """
        if meta_data and 'license_url' in meta_data:
            return meta_data['license_url']
        else:
            return None

    @staticmethod
    def get_maturity(meta_data, api_maturity_flag):
        """
        Determine whether a work has been labeled for mature audiences only.
        :param meta_data: The metadata column, which may have a 'mature'
        flag.
        :param api_maturity_flag: An API layer flag that indicates we have
        manually labeled a work as mature ourselves. If it is True,
        we will ignore the meta_data column and mark the work 'mature'.
        :return:
        """
        _mature = False
        if meta_data and 'mature' in meta_data:
            _mature = meta_data['mature']
        if api_maturity_flag:
            _mature = True
        return _mature

    @staticmethod
    def get_authority_boost(meta_data, source):
        authority_boost = None
        if meta_data and 'authority_boost' in meta_data:
            try:
                authority_boost = float(meta_data['authority_boost'])
                authority_boost = _verify_rank_feature(
                    authority_boost, low=0, high=100
                )
            except (ValueError, TypeError):
                pass
        else:
            authority_boost = get_authority_boost(source)
        return authority_boost

    @staticmethod
    def get_popularity(raw):
        if not raw:
            return None
        popularity = raw * 100
        return _verify_rank_feature(popularity, low=0, high=100)

    @staticmethod
    def parse_detailed_tags(json_tags):
        if not json_tags:
            return None
        parsed_tags = []
        for tag in json_tags:
            if 'name' in tag:
                parsed_tag = {'name': tag['name']}
                if 'accuracy' in tag:
                    parsed_tag['accuracy'] = tag['accuracy']
                parsed_tags.append(parsed_tag)
        return parsed_tags


class Image(SyncableDocType):
    """
    Represents an image in Elasticsearch. Note that actual mappings are defined
    in `ingestion_server.es_mapping`.
    """

    class AspectRatios(Enum):
        TALL = auto()
        WIDE = auto()
        SQUARE = auto()

    class ImageSizes(Enum):
        """
        Maximum threshold for each image size band
        """
        SMALL = 640 * 480
        MEDIUM = 1600 * 900
        LARGE = float("inf")

    class Index:
        name = 'image'

    @staticmethod
    def database_row_to_elasticsearch_doc(row, schema):
        provider = row[schema['provider']]
        source = row[schema['source']]
        extension = Image.get_extension(row[schema['url']])
        height = row[schema['height']]
        width = row[schema['width']]
        meta = row[schema['meta_data']]
        if 'standardized_popularity' in schema:
            popularity = Image.get_popularity(
                row[schema['standardized_popularity']]
            )
        else:
            popularity = None
        authority_boost = Image.get_authority_boost(meta, provider)
        return Image(
            _id=row[schema['id']],
            id=row[schema['id']],
            title=row[schema['title']],
            identifier=row[schema['identifier']],
            creator=row[schema['creator']],
            creator_url=row[schema['creator_url']],
            tags=Image.parse_detailed_tags(row[schema['tags']]),
            created_on=row[schema['created_on']],
            url=row[schema['url']],
            thumbnail=row[schema['thumbnail']],
            provider=provider,
            source=row[schema['source']],
            license=row[schema['license']].lower(),
            license_version=row[schema['license_version']],
            foreign_landing_url=row[schema['foreign_landing_url']],
            description=Image.parse_description(meta),
            extension=Image.get_extension(row[schema['url']]),
            categories=get_categories(extension, source),
            aspect_ratio=Image.get_aspect_ratio(height, width),
            size=Image.get_size(height, width),
            license_url=Image.get_license_url(meta),
            mature=Image.get_maturity(meta, row[schema['mature']]),
            standardized_popularity=popularity,
            authority_boost=authority_boost,
            max_boost=max(popularity or 1, authority_boost or 1),
            min_boost=min(popularity or 1, authority_boost or 1)
        )

    @staticmethod
    def get_aspect_ratio(height, width):
        if height is None or width is None:
            return None
        elif height > width:
            aspect_ratio = Image.AspectRatios.TALL.name
        elif height < width:
            aspect_ratio = Image.AspectRatios.WIDE.name
        else:
            aspect_ratio = Image.AspectRatios.SQUARE.name
        return aspect_ratio.lower()

    @staticmethod
    def get_size(height, width):
        if height is None or width is None:
            return None
        resolution = height * width
        for size in Image.ImageSizes:
            if resolution < size.value:
                return size.name.lower()


class Audio(SyncableDocType):
    """
    Represents an audio in Elasticsearch. Note that actual mappings are defined
    in `ingestion_server.es_mapping`.
    """

    class Index:
        name = 'audio'

    @staticmethod
    def database_row_to_elasticsearch_doc(row, schema):
        provider = row[schema['provider']]
        meta = row[schema['meta_data']]
        if 'standardized_popularity' in schema:
            popularity = Audio.get_popularity(
                row[schema['standardized_popularity']]
            )
        else:
            popularity = None
        authority_boost = Audio.get_authority_boost(meta, provider)
        return Audio(
            _id=row[schema['id']],
            id=row[schema['id']],
            title=row[schema['title']],
            identifier=row[schema['identifier']],
            creator=row[schema['creator']],
            creator_url=row[schema['creator_url']],
            tags=Audio.parse_detailed_tags(row[schema['tags']]),
            created_on=row[schema['created_on']],
            url=row[schema['url']],
            thumbnail=row[schema['thumbnail']],
            provider=provider,
            source=row[schema['source']],
            license=row[schema['license']].lower(),
            license_version=row[schema['license_version']],
            foreign_landing_url=row[schema['foreign_landing_url']],
            description=Audio.parse_description(meta),
            extension=Audio.get_extension(row[schema['url']]),
            categories=row[schema['category']],
            license_url=Audio.get_license_url(meta),
            mature=Audio.get_maturity(meta, row[schema['mature']]),
            standardized_popularity=popularity,
            authority_boost=authority_boost,
            max_boost=max(popularity or 1, authority_boost or 1),
            min_boost=min(popularity or 1, authority_boost or 1)
        )


# Table name -> Elasticsearch model
database_table_to_elasticsearch_model = {
    'image': Image,
    'audio': Audio,
}
