from http.client import responses as http_responses
from textwrap import dedent

from drf_spectacular.openapi import AutoSchema, OpenApiResponse
from drf_spectacular.utils import OpenApiExample, extend_schema


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
