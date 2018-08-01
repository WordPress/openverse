from django.http import HttpResponsePermanentRedirect
from rest_framework.views import APIView
from rest_framework.decorators import throttle_classes
from cccatalog.api.utils.throttle import PostRequestThrottler
from cccatalog.api.serializers.link_serializers import ShortenedLinkSerializer
from cccatalog.api.models import ShortenedLink
from rest_framework.response import Response
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema


class _LinkCreatedResponse(serializers.Serializer):
    shortened_url=serializers.URLField()


class CreateShortenedLink(APIView):

    @swagger_auto_schema(operation_id="link_create",
                         responses={
                             201: _LinkCreatedResponse,
                             400: "Bad Request"
                         })
    @throttle_classes([PostRequestThrottler])
    def post(self, request, format=None):
        """ Create a shortened URL. Only domains within the CC Catalog platform
         will be accepted."""
        serialized = ShortenedLinkSerializer(data=request.data)
        if not serialized.is_valid():
            return Response(
                status=400,
                data=serialized.errors
            )

        shortened_path = serialized.save()
        shortened_url = "shares.cc" + shortened_path
        return Response(
            status=200,
            data={
                'shortened_url': shortened_url
            }
        )


class ResolveShortenedLink(APIView):
    @swagger_auto_schema(operation_id="link_resolve",
                         responses={
                             200: None,
                             301: HttpResponsePermanentRedirect,
                             404: 'Not Found'
                         })
    def get(self, request, path, format=None):
        """
        Given a shortened URL path, such as 'zb3k0', resolve the full URL
        and redirect the caller.
        """
        pass
