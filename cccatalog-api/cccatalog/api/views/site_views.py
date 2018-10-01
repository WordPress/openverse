from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from cccatalog.api.controllers.search_controller import get_providers
from drf_yasg.utils import swagger_auto_schema


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
        providers = get_providers('image')
        response = []
        for provider in providers:
            response.append(
                {
                    'provider_name': provider,
                    'image_count': providers[provider],
                }
            )
        return Response(status=200, data=response)
