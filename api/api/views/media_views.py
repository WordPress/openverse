import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.controllers import search_controller
from api.models import ContentProvider
from api.models.media import AbstractMedia
from api.serializers.provider_serializers import ProviderSerializer
from api.utils import image_proxy
from api.utils.pagination import StandardPagination
from api.utils.search_context import SearchContext


logger = logging.getLogger(__name__)


class MediaViewSet(ReadOnlyModelViewSet):
    lookup_field = "identifier"
    # TODO: https://github.com/encode/django-rest-framework/pull/6789
    lookup_value_regex = (
        r"[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}"
    )

    pagination_class = StandardPagination

    # Populate these in the corresponding subclass
    model_class: type[AbstractMedia] = None
    query_serializer_class = None
    default_index = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = [
            self.model_class,
            self.query_serializer_class,
            self.default_index,
        ]
        if any(val is None for val in required_fields):
            msg = "Viewset fields are not completely populated."
            raise ValueError(msg)

    def get_queryset(self):
        # The alternative to a sub-query would be using `extra` to do a join
        # to the content provider table and filtering `filter_content`. However,
        # that assumes that a content provider entry exists, which is not necessarily
        # the case. We often don't add a content provider until after works from
        # new providers are available in the API, and sometimes not even then.
        # Search returns results with providers that do not have a ContentProvider
        # table entry. Therefore, to maintain that assumption, a subquery is the only
        # workable approach, as Django's `extra` does not provide any facility for
        # handling null relations on the join.
        return self.model_class.objects.exclude(
            provider__in=ContentProvider.objects.filter(
                filter_content=True
            ).values_list("provider_identifier")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        req_serializer = self._get_request_serializer(self.request)
        context.update({"validated_data": req_serializer.validated_data})
        return context

    def _get_request_serializer(self, request):
        req_serializer = self.query_serializer_class(
            data=request.query_params, context={"request": request}
        )
        req_serializer.is_valid(raise_exception=True)
        return req_serializer

    def get_db_results(self, results):
        identifiers = []
        hits = []
        for hit in results:
            identifiers.append(hit.identifier)
            hits.append(hit)

        results = list(self.get_queryset().filter(identifier__in=identifiers))
        results.sort(key=lambda x: identifiers.index(str(x.identifier)))
        for result, hit in zip(results, hits):
            result.fields_matched = getattr(hit, "fields_matched", None)

        return results

    # Standard actions

    def retrieve(self, request, *_, **__):
        instance = self.get_object()
        search_context = SearchContext.build(
            [str(instance.identifier)], self.default_index
        ).asdict()
        serializer_context = search_context | self.get_serializer_context()
        serializer = self.get_serializer(instance, context=serializer_context)

        return Response(serializer.data)

    def list(self, request, *_, **__):
        params = self._get_request_serializer(request)

        page_size = self.paginator.page_size = params.data["page_size"]
        page = self.paginator.page = params.data["page"]

        hashed_ip = hash(self._get_user_ip(request))
        filter_dead = params.validated_data["filter_dead"]

        if pref_index := params.validated_data.get("index"):
            logger.info(f"Using preferred index {pref_index} for media.")
            search_index = pref_index
            exact_index = True
        else:
            logger.info("Using default index for media.")
            search_index = self.default_index
            exact_index = False

        try:
            results, num_pages, num_results, search_context = search_controller.search(
                params,
                search_index,
                exact_index,
                page_size,
                hashed_ip,
                filter_dead,
                page,
            )
            self.paginator.page_count = num_pages
            self.paginator.result_count = num_results
        except ValueError as e:
            raise APIException(getattr(e, "message", str(e)))

        serializer_context = search_context | self.get_serializer_context()

        serializer_class = self.get_serializer()
        if params.needs_db or serializer_class.needs_db:
            results = self.get_db_results(results)

        serializer = self.get_serializer(results, many=True, context=serializer_context)
        return self.get_paginated_response(serializer.data)

    # Extra actions

    @action(detail=False, serializer_class=ProviderSerializer, pagination_class=None)
    def stats(self, *_, **__):
        source_counts = search_controller.get_sources(self.default_index)
        context = self.get_serializer_context() | {
            "source_counts": source_counts,
        }

        providers = ContentProvider.objects.filter(
            media_type=self.default_index, filter_content=False
        )
        serializer = self.get_serializer(providers, many=True, context=context)
        return Response(serializer.data)

    @action(detail=True)
    def related(self, request, identifier=None, *_, **__):
        try:
            results = search_controller.related_media(
                uuid=identifier,
                index=self.default_index,
                filter_dead=True,
            )
            self.paginator.page_count = 1
            # `page_size` refers to the maximum number of related images to return.
            self.paginator.page_size = 10
            # `result_count` is hard-coded and is equal to the page size.
            self.paginator.result_count = 10
        except ValueError as e:
            raise APIException(getattr(e, "message", str(e)))
        # If there are no hits in the search controller
        except IndexError:
            raise APIException("Could not find items.", 404)

        serializer_context = self.get_serializer_context()

        serializer = self.get_serializer(results, many=True, context=serializer_context)
        return self.get_paginated_response(serializer.data)

    def report(self, request, identifier):
        serializer = self.get_serializer(data=request.data | {"identifier": identifier})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def thumbnail(self, request, media_obj, image_url):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        return image_proxy.get(
            image_url,
            media_obj.identifier,
            media_obj.provider,
            accept_header=request.headers.get("Accept", "image/*"),
            **serializer.validated_data,
        )

    # Helper functions

    @staticmethod
    def _get_user_ip(request):
        """
        Read request headers to find the correct IP address.

        It is assumed that X-Forwarded-For has been sanitized by the load balancer and
        thus cannot be rewritten by malicious users.

        :param request: a Django request object
        :return: an IP address
        """

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
