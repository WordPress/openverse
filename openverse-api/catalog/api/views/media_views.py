from urllib.error import HTTPError
from urllib.request import urlopen

from django.conf import settings
from django.http.response import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from catalog.api.controllers import search_controller
from catalog.api.controllers.search_controller import get_sources
from catalog.api.models import ContentProvider
from catalog.api.serializers.provider_serializers import ProviderSerializer
from catalog.api.utils.exceptions import get_api_exception
from catalog.api.utils.pagination import StandardPagination
from catalog.custom_auto_schema import CustomAutoSchema


class MediaViewSet(ReadOnlyModelViewSet):
    swagger_schema = CustomAutoSchema

    lookup_field = 'identifier'
    # TODO: https://github.com/encode/django-rest-framework/pull/6789
    lookup_value_regex = r'[0-9a-f\-]{36}'  # highly simplified approximation

    pagination_class = StandardPagination

    # Populate these in the corresponding subclass
    model_class = None
    query_serializer_class = None
    default_index = None
    qa_index = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = [
            self.model_class,
            self.query_serializer_class,
            self.default_index,
            self.qa_index,
        ]
        if any(val is None for val in required_fields):
            msg = 'Viewset fields are not completely populated.'
            raise ValueError(msg)

    def get_queryset(self):
        return self.model_class.objects.all()

    # Standard actions

    def list(self, request, *_, **__):
        self.paginator.page_size = request.query_params.get('page_size')
        page_size = self.paginator.page_size
        self.paginator.page = request.query_params.get('page')
        page = self.paginator.page

        params = self.query_serializer_class(data=request.query_params)
        params.is_valid(raise_exception=True)

        hashed_ip = hash(self._get_user_ip(request))
        qa = params.validated_data['qa']
        filter_dead = params.validated_data['filter_dead']

        search_index = self.qa_index if qa else self.default_index
        try:
            results, num_pages, num_results = search_controller.search(
                params,
                search_index,
                page_size,
                hashed_ip,
                request,
                filter_dead,
                page,
            )
            self.paginator.page_count = num_pages
            self.paginator.result_count = num_results
        except ValueError as e:
            raise get_api_exception(getattr(e, 'message', str(e)))

        serializer = self.get_serializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    # Extra actions

    @action(detail=False,
            serializer_class=ProviderSerializer)
    def stats(self, *_, **__):
        source_counts = get_sources(self.default_index)
        context = self.get_serializer_context() | {
            'source_counts': source_counts,
        }

        providers = ContentProvider \
            .objects \
            .filter(media_type=self.default_index, filter_content=False)
        serializer = self.get_serializer(providers, many=True, context=context)
        return Response(serializer.data)

    @action(detail=True)
    def related(self, request, identifier=None, *_, **__):
        try:
            results, num_results = search_controller.related_media(
                uuid=identifier,
                index=self.default_index,
                request=request,
                filter_dead=True
            )
            self.paginator.result_count = num_results
            self.paginator.page_count = 1
            self.paginator.page_size = num_results
        except ValueError as e:
            raise get_api_exception(getattr(e, 'message', str(e)))

        serializer = self.get_serializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def report(self, request, *_, **__):
        media = self.get_object()
        identifier = media.identifier
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise get_api_exception('Invalid input.', 400)
        report = serializer.save(identifier=identifier)

        serializer = self.get_serializer(report)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    # Helper functions

    @staticmethod
    def _get_user_ip(request):
        """
        Read request headers to find the correct IP address.
        It is assumed that X-Forwarded-For has been sanitized by the load balancer
        and thus cannot be rewritten by malicious users.
        :param request: A Django request object.
        :return: An IP address.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def _get_proxied_image(image_url, width=settings.THUMBNAIL_WIDTH_PX):
        if width is None:  # full size
            proxy_upstream = f'{settings.THUMBNAIL_PROXY_URL}/{image_url}'
        else:
            proxy_upstream = f'{settings.THUMBNAIL_PROXY_URL}/' \
                             f'{settings.THUMBNAIL_WIDTH_PX},fit/' \
                             f'{image_url}'
        try:
            upstream_response = urlopen(proxy_upstream)
            status = upstream_response.status
            content_type = upstream_response.headers.get('Content-Type')
        except HTTPError:
            raise get_api_exception('Failed to render thumbnail.')

        response = HttpResponse(
            upstream_response.read(),
            status=status,
            content_type=content_type
        )

        return response
