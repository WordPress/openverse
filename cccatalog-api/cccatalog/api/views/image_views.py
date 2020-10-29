from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_yasg.utils import swagger_auto_schema
from cccatalog.api.models import Image, ContentProvider, DeletedImage, \
    ImageReport
from cccatalog.api.utils import ccrel
from cccatalog.api.serializers.image_serializers import\
    ImageSearchResultsSerializer, ImageSerializer,\
    InputErrorSerializer, ImageSearchQueryStringSerializer,\
    WatermarkQueryStringSerializer, ReportImageSerializer,\
    OembedSerializer, NotFoundErrorSerializer, OembedResponseSerializer
from rest_framework.reverse import reverse
from cccatalog.api.utils.watermark import watermark
from django.http.response import HttpResponse, FileResponse
import cccatalog.api.controllers.search_controller as search_controller
from cccatalog.api.utils.exceptions import input_error_response
import logging
import piexif
import io
import libxmp
import requests
from PIL import Image as img
from drf_yasg import openapi
from cccatalog.example_responses import (
    image_search_200_example, image_search_400_example,
    image_detail_200_example, image_detail_404_example, oembed_list_200_example,
    oembed_list_404_example, recommendations_images_read_200_example,
    recommendations_images_read_404_example
)
from cccatalog.custom_auto_schema import CustomAutoSchema

log = logging.getLogger(__name__)

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


class SearchImages(APIView):
    swagger_schema = CustomAutoSchema
    image_search_description = \
        """
        image_search is an API endpoint to search images using a query string.

        By using this endpoint, you can obtain search results based on specified 
        query and optionally filter results by `license`, `license_type`, 
        `page`, `page_size`, `creator`, `tags`, `title`, `filter_dead`, 
        `source`, `extension`, `categories`, `aspect_ratio`, `size`, `mature`, 
        and `qa`. Results are ranked in order of relevance.
        
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

        You can refer to Bash's Request Samples for examples on how to use
        this endpoint.
        """  # noqa
    image_search_response = {
        "200": openapi.Response(
            description="OK",
            examples=image_search_200_example,
            schema=ImageSearchResultsSerializer(many=True)
        ),
        "400": openapi.Response(
            description="Bad Request",
            examples=image_search_400_example,
            schema=InputErrorSerializer
        )
    }

    image_search_bash = \
        """
        # Example 1: Search for an exact match of Claude Monet
        curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" https://api.creativecommons.engineering/v1/images?q="Claude Monet"
        
        # Example 2: Search for images related to both dog and cat
        curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" https://api.creativecommons.engineering/v1/images?q=dog+cat
        
        # Example 3: Search for images related to dog or cat, but not necessarily both
        curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" https://api.creativecommons.engineering/v1/images?q=dog|cat

        # Example 4: Search for images related to dog but won't include results related to 'pug'
        curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" https://api.creativecommons.engineering/v1/images?q=dog -pug
        
        # Example 5: Search for images matching anything with the prefix ‘net’
        curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" https://api.creativecommons.engineering/v1/images?q=net*
        
        # Example 6: Search for images that match dogs that are either corgis or labrador
        curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" https://api.creativecommons.engineering/v1/images?q=dogs + (corgis | labrador)
        
        # Example 7: Search for images that match strings close to the term theater with a difference of one character
        curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" https://api.creativecommons.engineering/v1/images?q=theatre~1
        
        # Example 8: Search for images using single query parameter
        curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" https://api.creativecommons.engineering/v1/images?q=test
        
        # Example 9: Search for images using multiple query parameters
        curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" https://api.creativecommons.engineering/v1/images?q=test&license=pdm,by&categories=illustration&page_size=1&page=1   
        """  # noqa

    @swagger_auto_schema(operation_id='image_search',
                         operation_description=image_search_description,
                         query_serializer=ImageSearchQueryStringSerializer,
                         responses=image_search_response,
                         code_examples=[
                             {
                                 'lang': 'Bash',
                                 'source': image_search_bash
                             }
                         ])
    def get(self, request, format=None):
        # Parse and validate query parameters
        params = ImageSearchQueryStringSerializer(data=request.query_params)
        if not params.is_valid():
            return input_error_response(params.errors)

        hashed_ip = hash(_get_user_ip(request))
        page_param = params.data[PAGE]
        page_size = params.data[PAGESIZE]
        qa = params.data[QA]
        filter_dead = params.data[FILTER_DEAD]

        search_index = 'search-qa' if qa else 'image'
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
        serialized_results = ImageSerializer(
            results, many=True, context=context
        ).data

        if len(results) < page_size and num_pages == 0:
            num_results = len(results)
        response_data = {
            RESULT_COUNT: num_results,
            PAGE_COUNT: num_pages,
            PAGE_SIZE: len(results),
            RESULTS: serialized_results
        }
        serialized_response = ImageSearchResultsSerializer(data=response_data)
        return Response(status=200, data=serialized_response.initial_data)


class RelatedImage(APIView):
    swagger_schema = CustomAutoSchema
    recommendations_images_read_description = \
        """
        recommendations_images_read is an API endpoint to get related images 
        for a specified image ID.

        By using this endpoint, you can get the details of related images such as 
        `title`, `id`, `creator`, `creator_url`, `tags`, `url`, `thumbnail`, 
        `provider`, `source`, `license`, `license_version`, `license_url`, 
        `foreign_landing_url`, `detail_url`, `related_url`, `height`, `weight`, 
        and `attribution`.
        
        You can refer to Bash's Request Samples for example on how to use
        this endpoint.
        """  # noqa
    recommendations_images_read_response = {
        "200": openapi.Response(
            description="OK",
            examples=recommendations_images_read_200_example,
            schema=ImageSerializer
        ),
        "404": openapi.Response(
            description="Not Found",
            examples=recommendations_images_read_404_example,
            schema=NotFoundErrorSerializer
        )
    }

    recommendations_images_read_bash = \
        """
        # Get related images for image ID (7c829a03-fb24-4b57-9b03-65f43ed19395)
        curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" http://api.creativecommons.engineering/v1/recommendations/images/7c829a03-fb24-4b57-9b03-65f43ed19395
        """  # noqa

    @swagger_auto_schema(operation_id="recommendations_images_read",
                         operation_description=recommendations_images_read_description,  # noqa: E501
                         responses=recommendations_images_read_response,
                         code_examples=[
                             {
                                 'lang': 'Bash',
                                 'source': recommendations_images_read_bash
                             }
                         ],
                         manual_parameters=[
                             openapi.Parameter('identifier', openapi.IN_PATH,
                                               "The unique identifier for "
                                               "the image.",
                                               type=openapi.TYPE_STRING,
                                               required=True),
                         ]
                         )
    def get(self, request, identifier, format=None):
        related, result_count = search_controller.related_images(
            uuid=identifier,
            index='image',
            request=request,
            filter_dead=True
        )

        context = {'request': request}
        serialized_related = ImageSerializer(
            related, many=True, context=context
        ).data
        response_data = {
            RESULT_COUNT: result_count,
            PAGE_COUNT: 0,
            RESULTS: serialized_related
        }
        serialized_response = ImageSearchResultsSerializer(data=response_data)
        return Response(status=200, data=serialized_response.initial_data)


class ImageDetail(GenericAPIView, RetrieveModelMixin):
    swagger_schema = CustomAutoSchema
    serializer_class = ImageSerializer
    queryset = Image.objects.all()
    lookup_field = 'identifier'
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    image_detail_description = \
        """
        image_detail is an API endpoint to get the details of a specified 
        image ID.

        By using this endpoint, you can get image details such as `title`, `id`, 
        `creator`, `creator_url`, `tags`, `url`, `thumbnail`, `provider`, 
        `source`, `license`, `license_version`, `license_url`, 
        `foreign_landing_url`, `detail_url`, `related_url`, `height`, `weight`, 
        and `attribution`.

        You can refer to Bash's Request Samples for example on how to use
        this endpoint.
        """  # noqa
    image_detail_response = {
        "200": openapi.Response(
            description="OK",
            examples=image_detail_200_example,
            schema=ImageSerializer
        ),
        "404": openapi.Response(
            description='Not Found',
            examples=image_detail_404_example,
            schema=NotFoundErrorSerializer
        )
    }

    image_detail_bash = \
        """
        # Get the details of image ID (7c829a03-fb24-4b57-9b03-65f43ed19395)
        curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" http://api.creativecommons.engineering/v1/images/7c829a03-fb24-4b57-9b03-65f43ed19395
        """  # noqa

    @swagger_auto_schema(operation_id="image_detail",
                         operation_description=image_detail_description,
                         responses=image_detail_response,
                         code_examples=[
                             {
                                 'lang': 'Bash',
                                 'source': image_detail_bash
                             }
                         ])
    def get(self, request, identifier, format=None):
        """ Get the details of a single list. """
        resp = self.retrieve(request, identifier)
        # Proxy insecure HTTP images at full resolution.
        if 'http://' in resp.data[search_controller.URL]:
            secure = request.build_absolute_uri(
                reverse('thumbs', [identifier])
            )
            secure += '?full_size=True'
            resp.data[search_controller.URL] = secure

        return resp


def _save_wrapper(pil_img, exif_bytes, destination):
    """
    PIL crashes if exif_bytes=None, so we have to wrap it to avoid littering
    the code with branches.
    """
    if exif_bytes:
        pil_img.save(destination, 'jpeg', exif=exif_bytes)
    else:
        pil_img.save(destination, 'jpeg')


class Watermark(GenericAPIView):
    """
    Given an image identifier as a URL parameter, produce an attribution
    watermark. This entails drawing a frame around the image and embedding
    ccREL metadata inside of the file.
    """
    lookup_field = 'identifier'
    serializer_class = WatermarkQueryStringSerializer

    @swagger_auto_schema(query_serializer=WatermarkQueryStringSerializer)
    def get(self, request, identifier, format=None):
        params = WatermarkQueryStringSerializer(data=request.query_params)
        if not params.is_valid():
            return input_error_response()
        try:
            image_record = Image.objects.get(identifier=identifier)
        except Image.DoesNotExist:
            return Response(status=404, data='Not Found')
        image_url = str(image_record.url)
        image_info = {
            'title': image_record.title,
            'creator': image_record.creator,
            'license': image_record.license,
            'license_version': image_record.license_version
        }
        # Create the actual watermarked image.
        watermarked, exif = watermark(
            image_url, image_info, params.data['watermark']
        )
        # Re-insert EXIF metadata.
        if exif:
            exif_bytes = piexif.dump(exif)
        else:
            exif_bytes = None
        img_bytes = io.BytesIO()
        _save_wrapper(watermarked, exif_bytes, img_bytes)
        if params.data['embed_metadata']:
            # Embed ccREL metadata with XMP.
            work_properties = {
                'creator': image_record.creator,
                'license_url': image_record.license_url,
                'attribution': image_record.attribution,
                'work_landing_page': image_record.foreign_landing_url,
                'identifier': str(image_record.identifier)
            }
            try:
                with_xmp = ccrel.embed_xmp_bytes(img_bytes, work_properties)
                return FileResponse(with_xmp, content_type='image/jpeg')
            except (libxmp.XMPError, AttributeError) as e:
                # Just send the EXIF-ified file if libxmp fails to add metadata.
                log.error(
                    'Failed to add XMP metadata to {}'
                    .format(image_record.identifier)
                )
                log.error(e)
                response = HttpResponse(content_type='image/jpeg')
                _save_wrapper(watermarked, exif_bytes, response)
                return response
        else:
            response = HttpResponse(img_bytes, content_type='image/jpeg')
            _save_wrapper(watermarked, exif_bytes, response)
            return response


class OembedView(APIView):
    swagger_schema = CustomAutoSchema
    oembed_list_description = \
        """
        oembed_list is an API endpoint to retrieve embedded content from a 
        specified image URL.

        By using this endpoint, you can retrieve embedded content such as 
        `version`, `type`, `width`, `height`, `title`, `author_name`, 
        `author_url`, and `license_url`.

        You can refer to Bash's Request Samples for example on how to use
        this endpoint.
        """  # noqa
    oembed_list_response = {
        "200": openapi.Response(
            description="OK",
            examples=oembed_list_200_example,
            schema=OembedResponseSerializer
        ),
        "404": openapi.Response(
            description="Not Found",
            examples=oembed_list_404_example,
            schema=NotFoundErrorSerializer
        )
    }

    oembed_list_bash = \
        """
        # Retrieve embedded content from image URL (https://ccsearch.creativecommons.org/photos/7c829a03-fb24-4b57-9b03-65f43ed19395)
        curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" http://api.creativecommons.engineering/v1/oembed?url=https://ccsearch.creativecommons.org/photos/7c829a03-fb24-4b57-9b03-65f43ed19395
        """  # noqa

    @swagger_auto_schema(operation_id="oembed_list",
                         operation_description=oembed_list_description,
                         query_serializer=OembedSerializer,
                         responses=oembed_list_response,
                         code_examples=[
                             {
                                 'lang': 'Bash',
                                 'source': oembed_list_bash
                             }
                         ])
    def get(self, request):
        url = request.query_params.get('url', '')

        if not url:
            return Response(status=404, data='Not Found')
        try:
            identifier = url.rsplit('/', 1)[1]
            image_record = Image.objects.get(identifier=identifier)
        except Image.DoesNotExist:
            return Response(status=404, data='Not Found')
        if not image_record.height or image_record.width:
            image = requests.get(image_record.url)
            width, height = img.open(io.BytesIO(image.content)).size
        else:
            width, height = image_record.width, image_record.height
        resp = {
            'version': 1.0,
            'type': 'photo',
            'width': width,
            'height': height,
            'title': image_record.title,
            'author_name': image_record.creator,
            'author_url': image_record.creator_url,
            'license_url': image_record.license_url
        }

        return Response(data=resp, status=status.HTTP_200_OK)


class ReportImageView(CreateAPIView):
    """
    images_report_create
    
    images_report_create is an API endpoint to report an issue about a 
    specified image ID to Creative Commons.

    By using this endpoint, you can report an image if it infringes copyright, 
    contains mature or sensitive content and others.

    You can refer to Bash's Request Samples for example on how to use
    this endpoint.
    """  # noqa
    swagger_schema = CustomAutoSchema
    queryset = ImageReport.objects.all()
    serializer_class = ReportImageSerializer
