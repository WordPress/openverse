from django.http import HttpResponsePermanentRedirect
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.decorators import throttle_classes
from cccatalog.api.utils.throttle import PostRequestThrottler
from cccatalog.api.serializers.link_serializers import ShortenedLinkSerializer
from cccatalog.api.models import ShortenedLink
from cccatalog import settings
from rest_framework.response import Response
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema


class _LinkCreatedResponse(serializers.Serializer):
    shortened_url = serializers.URLField()


class CreateShortenedLink(GenericAPIView):
    serializer_class = ShortenedLinkSerializer

    @swagger_auto_schema(operation_id="link_create",
                         responses={
                             201: _LinkCreatedResponse,
                             400: "Bad Request"
                         })
    @throttle_classes([PostRequestThrottler])
    def post(self, request, format=None):
        """ Create a shortened URL. Only domains within the CC Catalog platform
         will be accepted. The `full_url` must be a whitelisted endpoint."""
        full_url = request.data['full_url']
        serialized = ShortenedLinkSerializer(data={'full_url': full_url})
        if not serialized.is_valid():
            return Response(
                status=400,
                data=serialized.errors
            )

        shortened_path = serialized.save()
        shortened_url = settings.ROOT_SHORTENING_URL + '/' + shortened_path
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
                             301: 'Moved Permanently',
                             404: 'Not Found'
                         })
    def get(self, request, path, format=None):
        """
        Given a shortened URL path, such as 'zb3k0', resolve the full URL
        and redirect the caller.
        """
        try:
            link_instance = ShortenedLink.objects.get(shortened_path=path)
        except ShortenedLink.DoesNotExist:
            return Response(
                status=404,
                data='Not Found'
            )
        full_url = link_instance.full_url
        return HttpResponsePermanentRedirect(full_url)
