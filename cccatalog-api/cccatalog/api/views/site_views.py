from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from cccatalog.api.controllers.search_controller import get_providers
from drf_yasg.utils import swagger_auto_schema
from cccatalog.api.models import ContentProvider

IDENTIFIER = 'provider_identifier'
NAME = 'provider_name'


class HealthCheck(APIView):
    """
    Returns a `200 OK` response if the server is running.

    This endpoint is used in production to ensure that the server should receive
    traffic. If no response is provided, the server is deregistered from the
    load balancer and destroyed.
    """
    swagger_schema = None
    def get(self, request, format=None):
        return Response('', status=200)


class AboutImageResponse(serializers.Serializer):
    """ The full image search response. """
    provider_name = serializers.CharField()
    image_count = serializers.IntegerField()
    display_name = serializers.CharField()

class ImageStats(APIView):
    """
    List all providers in the Creative Commons image catalog, in addition to the
    number of images from each data source.
    """
    @swagger_auto_schema(operation_id='image_stats',
                         responses={
                             200: AboutImageResponse(many=True)
                         })
    def get(self, request, format=None):
        provider_data = ContentProvider \
            .objects \
            .values(IDENTIFIER, NAME)
        id_to_display_name = {
            rec[IDENTIFIER]: rec[NAME] for rec in provider_data
        }
        providers = get_providers('image')
        response = []
        for provider in providers:
            response.append(
                {
                    'provider_name': provider,
                    'image_count': providers[provider],
                    'display_name': id_to_display_name[provider]
                }
            )
        return Response(status=200, data=response)
