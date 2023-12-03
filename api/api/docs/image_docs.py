from drf_spectacular.utils import OpenApiResponse, extend_schema

from api.docs.base_docs import collection_schema, custom_extend_schema, fields_to_md
from api.examples import (
    image_complain_201_example,
    image_complain_curl,
    image_detail_200_example,
    image_detail_404_example,
    image_detail_curl,
    image_oembed_200_example,
    image_oembed_404_example,
    image_oembed_curl,
    image_related_200_example,
    image_related_404_example,
    image_related_curl,
    image_search_200_example,
    image_search_400_example,
    image_search_list_curl,
    image_stats_200_example,
    image_stats_curl,
)
from api.examples.image_responses import image_oembed_400_example
from api.serializers.error_serializers import (
    InputErrorSerializer,
    NotFoundErrorSerializer,
)
from api.serializers.image_serializers import (
    ImageReportRequestSerializer,
    ImageSearchRequestSerializer,
    ImageSerializer,
    OembedRequestSerializer,
    OembedSerializer,
)
from api.serializers.media_serializers import MediaThumbnailRequestSerializer
from api.serializers.provider_serializers import ProviderSerializer


search = custom_extend_schema(
    desc=f"""
        Search images using a query string.

        By using this endpoint, you can obtain search results based on specified
        query and optionally filter results by
        {fields_to_md(ImageSearchRequestSerializer.field_names)}.

        Results are ranked in order of relevance and paginated on the basis of the
        `page` param. The `page_size` param controls the total number of pages.

        Although there may be millions of relevant records, only the most relevant
        several thousand records can be viewed. This is by design: the search
        endpoint should be used to find the top 10,000 most relevant results, not
        for exhaustive search or bulk download of every barely relevant result. As
        such, the caller should not try to access pages beyond `page_count`, or else
        the server will reject the query.""",
    params=ImageSearchRequestSerializer,
    res={
        200: (ImageSerializer, image_search_200_example),
        400: (InputErrorSerializer, image_search_400_example),
    },
    eg=[image_search_list_curl],
    external_docs={
        "description": "Openverse Syntax Guide",
        "url": "https://openverse.org/search-help",
    },
)

stats = custom_extend_schema(
    desc=f"""
        Get a list of all content providers and their respective number of
        images in the Openverse catalog.

        By using this endpoint, you can obtain info about content providers such
        as {fields_to_md(ProviderSerializer.Meta.fields)}.""",
    res={200: (ProviderSerializer, image_stats_200_example)},
    eg=[image_stats_curl],
)

detail = custom_extend_schema(
    desc=f"""
        Get the details of a specified image.

        By using this endpoint, you can obtain info about images such as
        {fields_to_md(ImageSerializer.Meta.fields)}""",
    res={
        200: (ImageSerializer, image_detail_200_example),
        404: (NotFoundErrorSerializer, image_detail_404_example),
    },
    eg=[image_detail_curl],
)

related = custom_extend_schema(
    desc=f"""
        Get related images for a specified image.

        By using this endpoint, you can get the details of related images such as
        {fields_to_md(ImageSerializer.Meta.fields)}.""",
    res={
        200: (ImageSerializer, image_related_200_example),
        404: (NotFoundErrorSerializer, image_related_404_example),
    },
    eg=[image_related_curl],
)

report = custom_extend_schema(
    res={201: (ImageReportRequestSerializer, image_complain_201_example)},
    eg=[image_complain_curl],
)

thumbnail = extend_schema(
    parameters=[MediaThumbnailRequestSerializer],
    responses={200: OpenApiResponse(description="Thumbnail image")},
)

oembed = custom_extend_schema(
    params=OembedRequestSerializer,
    res={
        200: (OembedSerializer, image_oembed_200_example),
        404: (NotFoundErrorSerializer, image_oembed_404_example),
        400: (InputErrorSerializer, image_oembed_400_example),
    },
    eg=[image_oembed_curl],
)

watermark = custom_extend_schema(
    deprecated=True,
)

source_collection = collection_schema(
    media_type="images",
    collection="source",
)
creator_collection = collection_schema(
    media_type="images",
    collection="creator",
)
tag_collection = collection_schema(
    media_type="images",
    collection="tag",
)
