from rest_framework.views import APIView
from rest_framework.response import Response
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
                    "validation_error": ' '.join(parsing_errors)
                }
            )

        # Validate and clean up pagination parameters
        page = request.query_params.get('page')
        if not page or int(page) < 1:
            page = 1
        else:
            page = int(page)
        page_size = request.query_params.get('pagesize')
        if not page_size or int(page_size) > 500 or int(page_size) < 1:
            page_size = 20
        else:
            page_size = int(page_size)

        try:
            search_results = search_controller.search(search_params,
                                                      index='image',
                                                      page_size=page_size,
                                                      page=page)
        except ValueError:
            return Response(
                status=400,
                data={
                    'validation_error': 'Deep pagination is not allowed.'
                }
            )

        results = [hit.to_dict() for hit in search_results]

        # Elasticsearch does not allow deep pagination of ranked queries.
        # Adjust returned page count to reflect this.
        natural_page_count = int(search_results.hits.total/page_size)
        last_allowed_page = int((5000 + page_size / 2) / page_size)
        page_count = min(natural_page_count, last_allowed_page)

        response_data = {
            'result_count': search_results.hits.total,
            'page_count': page_count,
            'results': results
        }
        return Response(status=200, data=response_data)


class HealthCheck(APIView):

    def get(self, request, format=None):
        return Response('', status=200)
