import logging as log
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from cccatalog.api.controllers.search_controller import get_providers
from cccatalog.api.serializers.registration_serializers import\
    OAuth2RegistrationSerializer, OAuth2RegistrationSuccessful
from drf_yasg.utils import swagger_auto_schema
from cccatalog.api.models import ContentProvider
from oauth2_provider.models import AbstractApplication, Application
from cccatalog.api.utils.throttle import ThreePerDay

IDENTIFIER = 'provider_identifier'
NAME = 'provider_name'
FILTER = 'filter_content'
URL = 'domain_name'


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
    provider_url = serializers.CharField()


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
            .values(IDENTIFIER, NAME, FILTER, URL)
        provider_table = {
            rec[IDENTIFIER]:
                (rec[NAME], rec[FILTER], rec[URL]) for rec in provider_data
        }
        providers = get_providers('image')
        response = []
        for provider in providers:
            if provider in provider_table:
                display_name, _filter, provider_url = provider_table[provider]
                if not _filter:
                    response.append(
                        {
                            'provider_name': provider,
                            'image_count': providers[provider],
                            'display_name': display_name,
                            'provider_url': provider_url
                        }
                    )
            else:
                msg = 'provider_identifier missing from content_provider' \
                      ' table: {}. Check for typos/omissions.'.format(provider)
                log.error(msg)
        return Response(status=200, data=response)


class Register(APIView):
    """
    Allow a user to register their application for OAuth2 Client Credentials
    authorization flow.
    """
    throttle_classes = (ThreePerDay,)

    @swagger_auto_schema(operation_id='register_api_oauth2',
                         responses={
                             200: OAuth2RegistrationSuccessful
                         })
    def post(self, request, format=None):
        # Store the registration information the developer gave us.
        serialized = OAuth2RegistrationSerializer(data=request.data)
        if not serialized.is_valid():
            return Response(
                status=400,
                data=serialized.errors
            )
        else:
            serialized.save()
        # Authorize the developer's application in our backend.
        new_application = Application(
            name=serialized.validated_data['name'],
            skip_authorization=False,
            client_type="Confidential",
            authorization_grant_type=AbstractApplication.GRANT_CLIENT_CREDENTIALS
        )
        new_application.save()
        # Give the user their newly created credentials.
        return Response(
            status=200,
            data={
                'client_id': new_application.client_id,
                'client_secret': new_application.client_secret,
                'name': new_application.name
            }
        )
