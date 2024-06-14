"""
Provides an ORM-like experience for accessing data in Elasticsearch.

Note the any low-level changes to the index here, such as changing the order
of fields, must be reflected in the actual schema defined in the catalog.
"""

from enum import Enum, auto

from elasticsearch_dsl import Document, Field, Integer

from indexer_worker.authority import get_authority_boost


class RankFeature(Field):
    name = "rank_feature"


def _verify_rank_feature(value, low, high):
    """
    Rank features must be a positive non-zero float.

    Our features are scaled from 0 to 100 for fair comparison.
    """
    if value is None or value == 0:
        return None
    ceiling = min(value, high)
    floor = max(low, ceiling)
    return floor


class SyncableDocType(Document):
    """Represents tables in the source-of-truth that will be replicated to ES."""

    # Aggregations can't be performed on the _id meta-column, which
    # necessitates copying it to this column in the doc. Aggregation is
    # used to find the last document inserted into Elasticsearch
    id = Integer()

    @staticmethod
    def database_row_to_elasticsearch_doc(row, schema):
        """
        Children of this class must have a function mapping a PSQL model to an ES doc.

        :param row: A tuple representing a row in Postgres.
        :param schema: A map of each field name to its position in the row.
        :return:
        """
        raise NotImplementedError(
            "Model is missing database -> Elasticsearch translation."
        )


class Media(SyncableDocType):
    """Represents a media object in Elasticsearch."""

    class Index:
        name = "media"

    @staticmethod
    def database_row_to_elasticsearch_doc(row: tuple, schema: dict[str, int]):
        """
        Map the DB row to a Python dictionary that represents a doc in the ES index.

        :param row: the database row as a tuple obtained by the psycopg2 cursor
        :param schema: the mapping of database column names to the tuple index
        :return: a dictionary mapping the row tuple to an ES doc
        """

        raise NotImplementedError(
            "Missing database row -> Elasticsearch schema translation."
        )

    @staticmethod
    def get_instance_attrs(row, schema):
        """
        Map the common columns in the DB row to a Python dictionary.

        This dictionary is a smaller part of the document indexed by Elasticsearch.

        :param row: the database row as a tuple obtained by the psycopg2 cursor
        :param schema: the mapping of database column names to the tuple index
        :return: the ES sub-document holding the common cols of the row tuple
        """

        meta = row[schema["meta_data"]]

        if "standardized_popularity" in schema:
            popularity = Media.get_popularity(row[schema["standardized_popularity"]])
        else:
            popularity = None
        # Extracted for compatibility with the old image schema to pass the
        # cleanup tests in CI: test/unit_tests/test_cleanup.py
        category = row[schema["category"]] if "category" in schema else None

        provider = row[schema["provider"]]
        authority_boost = Media.get_authority_boost(meta, provider)

        # This matches the order of fields defined in the schema.
        return {
            "_id": row[schema["id"]],
            "id": row[schema["id"]],
            "created_on": row[schema["created_on"]],
            "mature": Media.get_maturity(meta, row[schema["mature"]]),
            # Keyword fields
            "identifier": row[schema["identifier"]],
            "license": row[schema["license"]].lower(),
            "provider": provider,
            "source": row[schema["source"]],
            "category": category,
            # Text-based fields
            "title": row[schema["title"]],
            "description": Media.parse_description(meta),
            "creator": row[schema["creator"]],
            # Rank feature fields
            "standardized_popularity": popularity,
            "authority_boost": authority_boost,
            "max_boost": max(popularity or 1, authority_boost or 1),
            "min_boost": min(popularity or 1, authority_boost or 1),
            # Nested fields
            "tags": Media.parse_detailed_tags(row[schema["tags"]]),
            # Extra fields, not indexed
            "url": row[schema["url"]],
        }

    @staticmethod
    def parse_description(metadata_field):
        """
        Parse the description field from the metadata if available.

        Limit to the first 2000 characters.
        """
        try:
            if "description" in metadata_field:
                return metadata_field["description"][:2000]
        except TypeError:
            return None

    @staticmethod
    def get_license_url(meta_data):
        """
        Get license URL from the metadata.

        If the license_url is not provided, we'll try to generate it elsewhere
        from the `license` and `license_version`.
        """
        if meta_data and "license_url" in meta_data:
            return meta_data["license_url"]
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
        if meta_data and "mature" in meta_data:
            _mature = meta_data["mature"]
        if api_maturity_flag:
            _mature = True
        return _mature

    @staticmethod
    def get_authority_boost(meta_data, source):
        authority_boost = None
        if meta_data and "authority_boost" in meta_data:
            try:
                authority_boost = float(meta_data["authority_boost"])
                authority_boost = _verify_rank_feature(authority_boost, low=0, high=100)
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
            return []
        parsed_tags = []
        for tag in json_tags:
            if "name" in tag:
                parsed_tag = {"name": tag["name"]}
                if "accuracy" in tag:
                    parsed_tag["accuracy"] = tag["accuracy"]
                parsed_tags.append(parsed_tag)
        return parsed_tags


class Image(Media):
    """
    Represents an image in Elasticsearch.

    Note that actual mappings are defined in the schema.
    """

    class AspectRatios(Enum):
        """Also defined in ``api/catalog/api/constants/field_values.py``."""

        TALL = auto()
        WIDE = auto()
        SQUARE = auto()

    class ImageSizes(Enum):
        """
        Maximum threshold for each image size band.

        These sizes are also defined in
        ``api/catalog/api/constants/field_values.py.``
        """

        SMALL = 640 * 480
        MEDIUM = 1600 * 900
        LARGE = float("inf")

    class Index:
        name = "image"

    @staticmethod
    def database_row_to_elasticsearch_doc(row, schema):
        extension = Image.get_extension(row[schema["url"]])
        height = row[schema["height"]]
        width = row[schema["width"]]
        aspect_ratio = Image.get_aspect_ratio(height, width)
        size = Image.get_size(height, width)
        attrs = Image.get_instance_attrs(row, schema)

        return Image(
            aspect_ratio=aspect_ratio,
            extension=extension,
            size=size,
            **attrs,
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
    def get_extension(url):
        """
        Get the extension from the last segment of the URL separated by a dot.

        TODO: Use the `filetype` field once the following issue is completed:
        https://github.com/WordPress/openverse-catalog/issues/536
        """
        extension = url.split(".")[-1].lower()
        if not extension or "/" in extension:
            return None
        else:
            return extension

    @staticmethod
    def get_size(height, width):
        if height is None or width is None:
            return None
        resolution = height * width
        for size in Image.ImageSizes:
            if resolution < size.value:
                return size.name.lower()


class Audio(Media):
    """
    Represents an audio in Elasticsearch.

    Note that actual mappings are defined in the schema.
    """

    class Durations(Enum):
        """
        Maximum threshold for each audio duration band.

        These durations are also defined in
        ``api/catalog/api/constants/field_values.py.``
        """

        SHORTEST = 30 * 1e3  # under 30 seconds
        SHORT = 2 * 60 * 1e3  # 30 seconds - 2 minutes
        MEDIUM = 10 * 60 * 1e3  # 2 - 10 minutes
        LONG = float("inf")  # longer than 10 minutes

    class Index:
        name = "audio"

    @staticmethod
    def database_row_to_elasticsearch_doc(row, schema):
        alt_files = row[schema["alt_files"]]
        filetype = row[schema["filetype"]]
        extension = Audio.get_extensions(filetype, alt_files)
        attrs = Audio.get_instance_attrs(row, schema)
        length = Audio.get_length(row[schema["duration"]])

        return Audio(
            length=length,
            filetype=filetype,
            extension=extension,
            **attrs,
        )

    @staticmethod
    def get_extensions(filetype, alt_files):
        if not alt_files:
            return filetype

        return [file["filetype"] for file in alt_files]

    @staticmethod
    def get_length(duration):
        if not duration:
            return None
        for length in Audio.Durations:
            if duration < length.value:
                return length.name.lower()


# Table name -> Elasticsearch model
media_type_to_elasticsearch_model = {
    "image": Image,
    "audio": Audio,
}
