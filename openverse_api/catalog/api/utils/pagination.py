from catalog.api.utils.exceptions import get_api_exception
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    page_query_param = "page"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result_count = None  # populated later
        self.page_count = None  # populated later

        self._page_size = 20
        self._page = None

    @property
    def page_size(self):
        """the number of results to show in one page"""
        return self._page_size

    @page_size.setter
    def page_size(self, value):
        if value is None:
            return
        value = int(value)  # convert str params to int
        if value <= 0 or value > 500:
            raise get_api_exception("Page size must be between 0 & 500.", 400)
        self._page_size = value

    @property
    def page(self):
        """the current page number being served"""
        return self._page

    @page.setter
    def page(self, value):
        if value is None:
            value = 1
        value = int(value)  # convert str params to int
        if value <= 0:
            raise get_api_exception("Page must be greater than 0.", 400)
        self._page = value

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
