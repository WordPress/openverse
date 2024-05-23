from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    page_query_param = "page"

    result_count: int | None
    page_count: int | None
    page: int
    warnings: list[dict]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result_count = None  # populated later
        self.page_count = None  # populated later
        self.page = 1  # default, gets updated when necessary
        self.warnings = []  # populated later as needed

    def get_paginated_response(self, data):
        response = {
            "result_count": self.result_count,
            "page_count": self.page_count,
            "page_size": self.page_size,
            "page": self.page,
            "results": data,
        }
        return Response(
            (
                {
                    # Put ``warnings`` first so it is as visible as possible.
                    "warnings": list(self.warnings),
                }
                if self.warnings
                else {}
            )
            | response
        )

    def get_paginated_response_schema(self, schema):
        """
        Get the schema of the paginated response, used by `drf-spectacular` to
        generate the documentation of the paginated search results response.
        """

        field_descriptions = {
            "result_count": (
                "The total number of items returned by search result.",
                10000,
            ),
            "page_count": ("The total number of pages returned by search result.", 20),
            "page_size": ("The number of items per page.", 20),
            "page": ("The current page number returned in the response.", 1),
        }

        properties = {
            field: {
                "type": "integer",
                "description": description,
                "example": example,
            }
            for field, (description, example) in field_descriptions.items()
        } | {
            "results": schema,
            "warnings": {
                "type": "array",
                "items": {
                    "type": "object",
                },
                "description": (
                    "Warnings pertinent to the request. "
                    "If there are no warnings, this property will not be present on the response. "
                    "Warnings are non-critical problems with the request. "
                    "Responses with warnings should be treated as unstable. "
                    "Warning descriptions must not be treated as machine readable "
                    "and their schema can change at any time."
                ),
                "example": [
                    {
                        "code": "partially invalid request parameter",
                        "message": (
                            "Some of the request parameters were bad, "
                            "but we processed the request anywhere. "
                            "Here's some information that might help you "
                            "fix the problem for future requests."
                        ),
                    }
                ],
            },
        }

        return {
            "type": "object",
            "properties": properties,
            "required": list(set(properties.keys()) - {"warnings"}),
        }
