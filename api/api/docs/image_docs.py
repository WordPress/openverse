from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    NotFound,
    ValidationError,
)

from drf_spectacular.utils import OpenApiResponse, extend_schema

from api.constants.parameters import COLLECTION, TAG
from api.docs.base_docs import (
    NON_FILTER_FIELDS,
    SEARCH_DESCRIPTION,
    custom_extend_schema,
    fields_to_md,
)
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
from api.serializers.image_serializers import (
    ImageReportRequestSerializer,
    ImageSearchRequestSerializer,
    ImageSerializer,
    OembedRequestSerializer,
    OembedSerializer,
)
from api.serializers.media_serializers import MediaThumbnailRequestSerializer
from api.serializers.source_serializers import SourceSerializer


serializer = ImageSearchRequestSerializer(context={"media_type": "image"})
image_filter_fields = fields_to_md(
    [f for f in serializer.field_names if f not in NON_FILTER_FIELDS]
)


image_search_description = SEARCH_DESCRIPTION.format(
    filter_fields=image_filter_fields,
    media_type="images",
    collection_param=COLLECTION,
    tag_param=TAG,
)

search = custom_extend_schema(
    desc=image_search_description,
    params=serializer,
    res={
        200: (ImageSerializer, image_search_200_example),
        400: (ValidationError, image_search_400_example),
        401: (NotAuthenticated, None),
    },
    eg=[image_search_list_curl],
    external_docs={
        "description": "Openverse Syntax Guide",
        "url": "https://openverse.org/search-help",
    },
)

stats = custom_extend_schema(
    desc=f"""
        Get a list of all content sources and their respective number of
        images in the Openverse catalog.

        By using this endpoint, you can obtain info about content sources such
        as {fields_to_md(SourceSerializer.Meta.fields)}.""",
    res={
        200: (SourceSerializer(many=True), image_stats_200_example),
        401: (AuthenticationFailed, None),
    },
    eg=[image_stats_curl],
)

detail = custom_extend_schema(
    desc=f"""
        Get the details of a specified image.

        By using this endpoint, you can obtain info about images such as
        {fields_to_md(ImageSerializer.Meta.fields)}""",
    res={
        200: (ImageSerializer, image_detail_200_example),
        401: (AuthenticationFailed, None),
        404: (NotFound, image_detail_404_example),
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
        401: (AuthenticationFailed, None),
        404: (NotFound, image_related_404_example),
    },
    eg=[image_related_curl],
)

report = custom_extend_schema(
    res={
        201: (ImageReportRequestSerializer, image_complain_201_example),
        401: (AuthenticationFailed, None),
        400: (ValidationError, None),
    },
    eg=[image_complain_curl],
)

thumbnail = extend_schema(
    parameters=[MediaThumbnailRequestSerializer],
    responses={
        200: OpenApiResponse(description="Thumbnail image"),
        404: NotFound,
        401: AuthenticationFailed,
    },
)

oembed = custom_extend_schema(
    params=OembedRequestSerializer,
    res={
        200: (OembedSerializer, image_oembed_200_example),
        400: (ValidationError, image_oembed_400_example),
        401: (AuthenticationFailed, None),
        404: (NotFound, image_oembed_404_example),
    },
    eg=[image_oembed_curl],
)

watermark = extend_schema(
    deprecated=True,
    responses={
        401: AuthenticationFailed,
        404: NotFound,
    },
)
