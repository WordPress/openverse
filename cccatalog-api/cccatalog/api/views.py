from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework_social_oauth2.authentication import SocialAuthentication
from rest_framework.renderers import JSONRenderer
import cccatalog.api.search_controller as search_controller


class SearchImages(APIView):
    renderer_classes = (JSONRenderer,)

    def get(self, request, format=None):
        # Read search query string. Ensure search query is valid.
        search_params, parsing_errors = \
            search_controller.parse_search_query(request.query_params)
        if parsing_errors:
            return Response(
                status=400,
                data={
                    "validation_errors": ' '.join(parsing_errors)
                }
            )

        # Validate and clean up pagination parameters
        page = request.query_params.get('page')
        if not page or int(page) < 1:
            page = 1
        else:
            page = int(page)

        page_size = request.query_params.get('pagesize')
        if not page_size or int(page_size) > 1000 or int(page_size) < 1:
            page_size = 100
        else:
            page_size = int(page_size)

        search_results = search_controller.search(search_params,
                                                  index='image',
                                                  page_size=page_size,
                                                  page=page)

        results = [hit.to_dict() for hit in search_results]

        response_data = {
            'count': search_results.hits.total,
            'results': results,
        }
        return Response(status=200, data=response_data)


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
