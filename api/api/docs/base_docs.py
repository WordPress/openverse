from http.client import responses as http_responses
from textwrap import dedent
from typing import Literal

from django.conf import settings
from rest_framework.exceptions import (
    NotAuthenticated,
    NotFound,
    ValidationError,
)

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from api.constants.media_types import MediaType
from api.serializers.audio_serializers import (
    AudioCollectionRequestSerializer,
    AudioSerializer,
)
from api.serializers.image_serializers import ImageSerializer
from api.serializers.media_serializers import PaginatedRequestSerializer


def fields_to_md(field_names):
    """
    Create a Markdown representation of the given list of names to use in Swagger docs.

    :param field_names: the list of field names to convert to Markdown
    :return: the names as a Markdown string
    """

    *all_but_last, last = field_names
    all_but_last = ", ".join([f"`{name}`" for name in all_but_last])
    return f"{all_but_last} and `{last}`"


def custom_extend_schema(**kwargs):
    extend_args = {}

    description = kwargs.pop("desc", None)
    if description:
        description = dedent(description)
        extend_args["description"] = f"{description}"

    parameters = kwargs.pop("params", [])
    if not isinstance(parameters, list):
        parameters = [parameters]
    if parameters:
        extend_args["parameters"] = parameters

    responses = kwargs.pop("res", {})
    if responses:
        responses = {
            code: OpenApiResponse(
                serializer,
                description=http_responses[code],
                examples=[
                    OpenApiExample(
                        http_responses[code], value=example["application/json"]
                    )
                ]
                if example
                else [],
            )
            for code, (serializer, example) in responses.items()
        }
        extend_args["responses"] = responses

    eg = kwargs.pop("eg", [])
    if eg:
        # Docs: https://redocly.com/docs/api-reference-docs/specification-extensions/x-code-samples/
        extend_args["extensions"] = {
            "x-codeSamples": [{"lang": "cURL", "source": example} for example in eg]
        }

    return extend_schema(**extend_args, **kwargs)


class MediaSchema(AutoSchema):
    """
    Overrides the default schema generator provided by drf-spectacular to adapt
    to the conventions of the Openverse API documentation.
    """

    def get_description(self) -> str:
        return f"""{super().get_description()}"""

    def get_operation_id(self) -> str:
        operation_tokens = super().get_operation_id().split("_")[0:-1]
        if self.method == "GET" and len(operation_tokens) == 1:
            if self._is_list_view():
                operation_tokens.append("search")
            else:
                operation_tokens.append("detail")
        return "_".join(operation_tokens)


source_404_message = "Invalid source 'name'. Valid sources are ..."
source_404_response = OpenApiResponse(
    NotFound,
    examples=[
        OpenApiExample(
            name="404",
            value={"detail": source_404_message},
        )
    ],
)


def build_source_path_parameter(media_type: MediaType):
    valid_description = (
        f"Valid values are source_names from the stats endpoint: "
        f"{settings.CANONICAL_ORIGIN}/v1/{media_type}/stats/."
    )

    return OpenApiParameter(
        name="source",
        type={
            "type": "string",
            "pattern": "^[^/.]+?$",
        },
        location=OpenApiParameter.PATH,
        description=f"The source of {media_type}. {valid_description}",
    )


creator_path_parameter = OpenApiParameter(
    name="creator",
    type={
        "type": "string",
        "pattern": "^.+$",
    },
    location=OpenApiParameter.PATH,
    description="The name of the media creator. This parameter "
    "is case-sensitive, and matches exactly.",
)
tag_path_parameter = OpenApiParameter(
    name="tag",
    type={
        "type": "string",
        "pattern": "^[^/.]+?$",
    },
    location=OpenApiParameter.PATH,
    description="The tag of the media. Not case-sensitive, matches exactly.",
)


def get_collection_description(media_type, collection):
    if collection == "tag":
        return f"""
Get a collection of {media_type} with a specific tag.

This endpoint matches a single tag, exactly and entirely.

Differences that will cause tags to not match are:
- upper and lower case letters
- diacritical marks
- hyphenation
- spacing
- multi-word tags where the query is only one of the words in the tag
- multi-word tags where the words are in a different order

Examples of tags that **do not** match:
- "Low-Quality" and "low-quality"
- "jalapeño" and "jalapeno"
- "Saint Pierre des Champs" and "Saint-Pierre-des-Champs"
- "dog walking" and "dog  walking" (where the latter has two spaces between the
last two words, as in a typographical error)
- "runner" and "marathon runner"
- "exclaiming loudly" and "loudly exclaiming"

For non-exact or multi-tag matching, using the `search` endpoint's `tags` query
parameter.

The returned results are ordered based on the time when they were added to Openverse.
    """
    elif collection == "source":
        return f"""
Get a collection of {media_type} from a specific source.

This endpoint returns only the exact matches. To search within the source value,
use the `search` endpoint with `source` query parameter.

The results in the collection will be sorted by the order in which they
were added to Openverse.
    """
    elif collection == "creator":
        return f"""
Get a collection of {media_type} by a specific creator from the specified source.

This endpoint returns only the exact matches both on the creator and the source.
Notice that a single creator's media items can be found on several sources, but
this endpoint only returns the items from the specified source. To search within
the creator value, use the `search` endpoint with `source` query parameter
instead of `q`.

The items will be sorted by the date when they were added to Openverse.
    """


COLLECTION_TO_OPERATION_ID = {
    ("images", "source"): "images_by_source",
    ("images", "creator"): "images_by_source_and_creator",
    ("images", "tag"): "images_by_tag",
    ("audio", "source"): "audio_by_source",
    ("audio", "creator"): "audio_by_source_and_creator",
    ("audio", "tag"): "audio_by_tag",
}


def collection_schema(
    media_type: Literal["images", "audio"],
    collection: Literal["source", "creator", "tag"],
):
    if media_type == "images":
        request_serializer = PaginatedRequestSerializer
        serializer = ImageSerializer
    else:
        request_serializer = AudioCollectionRequestSerializer
        serializer = AudioSerializer

    if collection == "tag":
        responses = {
            200: serializer(many=True),
            404: NotFound,
            400: ValidationError,
            401: (NotAuthenticated, None),
        }
        path_parameters = [tag_path_parameter]
    else:
        responses = {
            200: serializer(many=True),
            404: source_404_response,
            400: ValidationError,
            401: (NotAuthenticated, None),
        }
        path_parameters = [build_source_path_parameter(media_type)]
        if collection == "creator":
            path_parameters.append(creator_path_parameter)
    operation_id = COLLECTION_TO_OPERATION_ID[(media_type, collection)]
    description = get_collection_description(media_type, collection)
    return extend_schema(
        operation_id=operation_id,
        summary=operation_id,
        auth=[],
        description=description,
        responses=responses,
        parameters=[
            request_serializer,
            *path_parameters,
        ],
    )
