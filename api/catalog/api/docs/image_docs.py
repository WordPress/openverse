from catalog.api.docs.media_docs import (
    MediaComplain,
    MediaDetail,
    MediaRelated,
    MediaSearch,
    MediaStats,
    fields_to_md,
    refer_sample,
)
from catalog.api.examples import (
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
from catalog.api.serializers.error_serializers import (
    InputErrorSerializer,
    NotFoundErrorSerializer,
)
from catalog.api.serializers.image_serializers import (
    ImageReportSerializer,
    ImageSearchRequestSerializer,
    ImageSearchSerializer,
    ImageSerializer,
    OembedRequestSerializer,
    OembedSerializer,
)
from catalog.api.serializers.media_serializers import MediaThumbnailRequestSerializer
from catalog.api.serializers.provider_serializers import ProviderSerializer
from drf_yasg import openapi


class ImageSearch(MediaSearch):
    desc = f"""
image_search is an API endpoint to search images using a query string.

By using this endpoint, you can obtain search results based on specified query and
optionally filter results by
{fields_to_md(ImageSearchRequestSerializer.fields_names)}.

{MediaSearch.desc}"""

    responses = {
        "200": openapi.Response(
            description="OK",
            examples=image_search_200_example,
            schema=ImageSearchSerializer,
        ),
        "400": openapi.Response(
            description="Bad Request",
            examples=image_search_400_example,
            schema=InputErrorSerializer,
        ),
    }

    code_examples = [
        {
            "lang": "Bash",
            "source": image_search_list_curl,
        },
    ]

    swagger_setup = {
        "operation_id": "image_search",
        "operation_description": desc,
        "query_serializer": ImageSearchRequestSerializer,
        "responses": responses,
        "code_examples": code_examples,
    }


class ImageStats(MediaStats):
    desc = f"""
image_stats is an API endpoint to get a list of all content providers and their
respective number of images in the Openverse catalog.

{MediaStats.desc}"""

    responses = {
        "200": openapi.Response(
            description="OK",
            examples=image_stats_200_example,
            schema=ProviderSerializer(many=True),
        )
    }

    code_examples = [
        {
            "lang": "Bash",
            "source": image_stats_curl,
        }
    ]

    swagger_setup = {
        "operation_id": "image_stats",
        "operation_description": desc,
        "responses": responses,
        "code_examples": code_examples,
    }


class ImageDetail(MediaDetail):
    desc = f"""
image_detail is an API endpoint to get the details of a specified image ID.

By using this endpoint, you can image details such as
{fields_to_md(ImageSerializer.fields_names)}.

{MediaDetail.desc}"""

    responses = {
        "200": openapi.Response(
            description="OK", examples=image_detail_200_example, schema=ImageSerializer
        ),
        "404": openapi.Response(
            description="Not Found",
            examples=image_detail_404_example,
            schema=NotFoundErrorSerializer,
        ),
    }

    code_examples = [{"lang": "Bash", "source": image_detail_curl}]

    swagger_setup = {
        "operation_id": "image_detail",
        "operation_description": desc,
        "responses": responses,
        "code_examples": code_examples,
    }


class ImageRelated(MediaRelated):
    desc = f"""
recommendations_images_read is an API endpoint to get related images for a specified
image ID.

By using this endpoint, you can get the details of related images such as
{fields_to_md(ImageSerializer.fields_names)}.

{MediaRelated.desc}"""

    responses = {
        "200": openapi.Response(
            description="OK", examples=image_related_200_example, schema=ImageSerializer
        ),
        "404": openapi.Response(
            description="Not Found",
            examples=image_related_404_example,
            schema=NotFoundErrorSerializer,
        ),
    }

    code_examples = [{"lang": "Bash", "source": image_related_curl}]

    swagger_setup = {
        "operation_id": "image_related",
        "operation_description": desc,
        "responses": responses,
        "code_examples": code_examples,
    }


class ImageComplain(MediaComplain):
    desc = f"""
images_report_create is an API endpoint to report an issue about a specified image ID to
Openverse.

By using this endpoint, you can report an image if it infringes copyright, contains
mature or sensitive content and others.

{MediaComplain.desc}"""

    responses = {
        "201": openapi.Response(
            description="OK",
            examples=image_complain_201_example,
            schema=ImageReportSerializer,
        )
    }

    code_examples = [
        {
            "lang": "Bash",
            "source": image_complain_curl,
        }
    ]

    swagger_setup = {
        "operation_id": "image_report",
        "operation_description": desc,
        "responses": responses,
        "code_examples": code_examples,
    }


class ImageOembed:
    desc = f"""
oembed_list is an API endpoint to retrieve embedded content from a specified image URL.

By using this endpoint, you can retrieve embedded content such as `version`, `type`,
`width`, `height`, `title`, `author_name`, `author_url` and `license_url`.

{refer_sample}"""

    responses = {
        "200": openapi.Response(
            description="OK", examples=image_oembed_200_example, schema=OembedSerializer
        ),
        "404": openapi.Response(
            description="Not Found",
            examples=image_oembed_404_example,
            schema=NotFoundErrorSerializer,
        ),
    }

    code_examples = [
        {
            "lang": "Bash",
            "source": image_oembed_curl,
        },
    ]

    swagger_setup = {
        "operation_id": "image_oembed",
        "operation_description": desc,
        "query_serializer": OembedRequestSerializer,
        "responses": responses,
        "code_examples": code_examples,
    }


class ImageThumbnail:
    desc = f"""
thumbnail is an API endpoint to retrieve the scaled down and compressed thumbnail
of an image.

{refer_sample}"""

    swagger_setup = {
        "operation_id": "image_thumbnail",
        "operation_description": desc,
        "query_serializer": MediaThumbnailRequestSerializer,
    }
