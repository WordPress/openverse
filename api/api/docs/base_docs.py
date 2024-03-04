from http.client import responses as http_responses
from textwrap import dedent

from django.conf import settings
from rest_framework.exceptions import (
    NotFound,
)

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from api.constants.media_types import MediaType


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
