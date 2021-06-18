from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.api.controllers import search_controller
from catalog.api.utils.exceptions import input_error_response

FOREIGN_LANDING_URL = 'foreign_landing_url'
CREATOR_URL = 'creator_url'
RESULTS = 'results'
PAGE = 'page'
PAGESIZE = 'page_size'
FILTER_DEAD = 'filter_dead'
QA = 'qa'
SUGGESTIONS = 'suggestions'
RESULT_COUNT = 'result_count'
PAGE_COUNT = 'page_count'
PAGE_SIZE = 'page_size'


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


class SearchMedia(APIView):
    search_description = """
Although there may be millions of relevant records, only the most 
relevant several thousand records can be viewed. This is by design: 
the search endpoint should be used to find the top 10,000 most relevant 
results, not for exhaustive search or bulk download of every barely 
relevant result. As such, the caller should not try to access pages 
beyond `page_count`, or else the server will reject the query.

For more precise results, you can go to the 
[CC Search Syntax Guide](https://search.creativecommons.org/search-help) 
for information about creating queries and 
[Apache Lucene Syntax Guide](https://lucene.apache.org/core/2_9_4/queryparsersyntax.html)
for information on structuring advanced searches.

You can refer to the cURL request samples for examples on how to consume this
endpoint.
    """  # noqa

    def _get(self,
             request,
             default_index, qa_index,
             query_serializer, media_serializer, result_serializer):
        params = query_serializer(data=request.query_params)
        if not params.is_valid():
            return input_error_response(params.errors)

        hashed_ip = hash(_get_user_ip(request))
        page_param = params.data[PAGE]
        page_size = params.data[PAGESIZE]
        qa = params.data[QA]
        filter_dead = params.data[FILTER_DEAD]

        search_index = qa_index if qa else default_index
        try:
            results, num_pages, num_results = search_controller.search(
                params,
                search_index,
                page_size,
                hashed_ip,
                request,
                filter_dead,
                page=page_param
            )
        except ValueError as value_error:
            return input_error_response(value_error)

        context = {'request': request}
        serialized_results = media_serializer(
            results,
            many=True,
            context=context
        ).data

        if len(results) < page_size and num_pages == 0:
            num_results = len(results)
        response_data = {
            RESULT_COUNT: num_results,
            PAGE_COUNT: num_pages,
            PAGE_SIZE: len(results),
            RESULTS: serialized_results
        }
        serialized_response = result_serializer(data=response_data)
        return Response(status=200, data=serialized_response.initial_data)


class RelatedMedia(APIView):
    swagger_schema = CustomAutoSchema
    recommendations_read_description = """
You can refer to the cURL request samples for examples on how to consume this
endpoint.
""" # noqa
