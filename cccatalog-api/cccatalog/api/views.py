from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework_social_oauth2.authentication import SocialAuthentication
from rest_framework.renderers import JSONRenderer
import cccatalog.api.search_controller as search_controller


class SearchImages(APIView):
    renderer_classes = (JSONRenderer,)

    def get(self, request, format=None):
        search_params, parsing_errors = \
            search_controller.parse_search_query(request.query_params)
        if parsing_errors:
            return Response(
                status=400,
                data={
                    "validation_errors": ' '.join(parsing_errors)
                }
            )
        search_results = search_controller.search(search_params, index='image')
        return Response(status=200, data={'status':'success'})


class ProtectedView(APIView):
    authentication_classes = (SocialAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        msg = 'You have access!'
        return Response(msg)


class PublicView(APIView):

    def get(self, request, format=None):
        return Response('Public view without login')


class HealthCheck(APIView):

    def get(self, request, format=None):
        return Response('', status=200)
