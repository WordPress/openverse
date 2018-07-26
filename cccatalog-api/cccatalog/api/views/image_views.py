from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from cccatalog.api.models import Image
from cccatalog.api.utils.view_count import track_model_views
from cccatalog.api.serializers.search_serializers import\
    ImageSearchResultsSerializer, ImageSerializer,\
    ValidationErrorSerializer, ImageSearchQueryStringSerializer
from cccatalog.api.serializers.image_serializers import ImageDetailSerializer
import cccatalog.api.controllers.search_controller as search_controller


class SearchImages(APIView):
    """
    Search for images by keyword. Optionally, filter the results by specific
    licenses, or license "types" (commercial use allowed, modification allowed,
    etc). Results are ranked in order of relevance.

    Although there may be millions of relevant records, only the most relevant
    several thousand records can be viewed. This is by design: the search
    endpoint should be used to find the top N most relevant results, not for
    exhaustive search or bulk download of every barely relevant result. As such,
    the caller should not try to access pages beyond `page_count`, or else the
    server will reject the query.
    """

    @swagger_auto_schema(operation_id='image_search',
                         query_serializer=ImageSearchQueryStringSerializer,
                         responses={
                             200: ImageSearchResultsSerializer(many=True),
                             400: ValidationErrorSerializer,
                         })
    def get(self, request, format=None):
        # Parse and validate query parameters
        params = ImageSearchQueryStringSerializer(data=request.query_params)
        if not params.is_valid():
            return Response(
                status=400,
                data={
                    "validation_error": params.errors
                }
            )
        page = params.data['page']
        page_size = params.data['pagesize']
        try:
            search_results = search_controller.search(params,
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

        results = [result for result in search_results]
        serialized_results =\
            ImageSerializer(results, many=True).data

        # Elasticsearch does not allow deep pagination of ranked queries.
        # Adjust returned page count to reflect this.
        natural_page_count = int(search_results.hits.total/page_size)
        last_allowed_page = int((5000 + page_size / 2) / page_size)
        page_count = min(natural_page_count, last_allowed_page)

        response_data = {
            'result_count': search_results.hits.total,
            'page_count': page_count,
            'results': serialized_results
        }
        serialized_response = ImageSearchResultsSerializer(data=response_data)

        return Response(status=200, data=serialized_response.initial_data)


class ImageDetail(GenericAPIView, RetrieveModelMixin):
    """
    Load the details of a particular image ID. Image details include:
    - All fields in the database
    - The number of views

    Also increments the view count of the image.
    """
    serializer_class = ImageDetailSerializer
    queryset = Image.objects.all()
    lookup_field = 'id'

    @swagger_auto_schema(operation_id="image_detail",
                         responses={
                             200: ImageDetailSerializer,
                             404: 'Not Found'
                         })
    @track_model_views(Image)
    def get(self, request, id, format=None):
        """ Get the details of a single list. """
        return self.retrieve(request, id)
