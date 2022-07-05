from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    page_query_param = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result_count = None  # populated later
        self.page_count = None  # populated later

        self.page_size = 20
        self.page = 1

    def get_paginated_response(self, data):
        return Response(
            {
                "result_count": self.result_count,
                "page_count": self.page_count,
                "page_size": self.page_size,
                "page": self.page,
                "results": data,
            }
        )
