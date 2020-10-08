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
    OembedSerializer
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
    image_search_description = \
    """
    Search for images by a query string. Optionally, filter results by specific
    licenses, or license "types" (commercial use allowed, modification allowed,
    etc). Results are ranked in order of relevance.

    Refer to the Lucene syntax guide for information on structuring advanced
    searches. https://lucene.apache.org/core/2_9_4/queryparsersyntax.html

    Although there may be millions of relevant records, only the most relevant
    several thousand records can be viewed. This is by design: the search
    endpoint should be used to find the top N most relevant results, not for
    exhaustive search or bulk download of every barely relevant result.
    As such, the caller should not try to access pages beyond `page_count`,
    or else the server will reject the query.

    Example using single query parameter:
 
    ```
    $ curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" https://api.creativecommons.engineering/v1/images?q=test
    ```


    Example using multiple query parameters:

    ```
    $ curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" https://api.creativecommons.engineering/v1/images?q=test&license=pdm,by&categories=illustration&page_size=1&page=1
    ```

    """
    image_search_response = {
        "200": openapi.Response(
            description="OK",
            examples={
                "application/json": {
                    "result_count": 77,
                    "page_count": 77,
                    "page_size": 1,
                    "results": [
                        {
                            "title": "File:Well test separator.svg",
                            "id": "36537842-b067-4ca0-ad67-e00ff2e06b2d",
                            "creator": "en:User:Oil&GasIndustry",
                            "creator_url": "https://en.wikipedia.org/wiki/User:Oil%26GasIndustry",
                            "url": "https://upload.wikimedia.org/wikipedia/commons/3/3a/Well_test_separator.svg",
                            "thumbnail": "https://api.creativecommons.engineering/v1/thumbs/36537842-b067-4ca0-ad67-e00ff2e06b2d",
                            "provider": "wikimedia",
                            "source": "wikimedia",
                            "license": "by",
                            "license_version": "3.0",
                            "license_url": "https://creativecommons.org/licenses/by/3.0",
                            "foreign_landing_url": "https://commons.wikimedia.org/w/index.php?curid=26229990",
                            "detail_url": "http://api.creativecommons.engineering/v1/images/36537842-b067-4ca0-ad67-e00ff2e06b2d",
                            "related_url": "http://api.creativecommons.engineering/v1/recommendations/images/36537842-b067-4ca0-ad67-e00ff2e06b2d",
                            "fields_matched": [
                                "description",
                                "title"
                            ]
                        }
                    ]
                },
            },
            schema=ImageSearchResultsSerializer(many=True)
        ),
        "400": openapi.Response(
            description="Bad Request",
            examples={
                "application/json": {
                    "error": "InputError",
                    "detail": "Invalid input given for fields. 'license' -> License 'PDMNBCG' does not exist.",
                    "fields": [
                        "license"
                    ]
                }
            },
            schema=InputErrorSerializer
        )
    }
    @swagger_auto_schema(operation_id='image_search',
                         operation_description=image_search_description,
                         query_serializer=ImageSearchQueryStringSerializer,
                         responses=image_search_response)
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
    recommendations_images_read_description = \
    """
    Given an image ID, return images related to the result.

    Example using image ID `7c829a03-fb24-4b57-9b03-65f43ed19395`:

    ```
    $ curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" http://api.creativecommons.engineering/v1/recommendations/images/7c829a03-fb24-4b57-9b03-65f43ed19395
    ```
    """
    recommendations_images_read_response = {
        "200": openapi.Response(
            description="OK",
            examples={
                "application/json": {
                    "result_count": 10000,
                    "page_count": 0,
                    "results": [
                        {
                            "title": "exam tactics",
                            "id": "610756ec-ae31-4d5e-8f03-8cc52f31b71d",
                            "creator": "Sean MacEntee",
                            "creator_url": "https://www.flickr.com/photos/18090920@N07",
                            "tags": [
                                {
                                    "name": "exam"
                                },
                                {
                                    "name": "tactics"
                                }
                            ],
                            "url": "https://live.staticflickr.com/4065/4459771899_07595dc42e.jpg",
                            "thumbnail": "https://api.creativecommons.engineering/v1/thumbs/610756ec-ae31-4d5e-8f03-8cc52f31b71d",
                            "provider": "flickr",
                            "source": "flickr",
                            "license": "by",
                            "license_version": "2.0",
                            "license_url": "https://creativecommons.org/licenses/by/2.0/",
                            "foreign_landing_url": "https://www.flickr.com/photos/18090920@N07/4459771899",
                            "detail_url": "http://api.creativecommons.engineering/v1/images/610756ec-ae31-4d5e-8f03-8cc52f31b71d",
                            "related_url": "http://api.creativecommons.engineering/v1/recommendations/images/610756ec-ae31-4d5e-8f03-8cc52f31b71d"
                        }
                    ]
                }
            },
            schema=ImageSerializer
        ),
        "404": openapi.Response(
            description="Not Found",
            examples={
                "application/json": {
                    "detail": "An internal server error occurred."
                }
            }
        )
    }
    @swagger_auto_schema(operation_id="recommendations_images_read",
                         operation_description=recommendations_images_read_description,
                         responses=recommendations_images_read_response)
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
    serializer_class = ImageSerializer
    queryset = Image.objects.all()
    lookup_field = 'identifier'
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    image_detail_description = \
    """
    Load the details of a particular image ID.

    Example using image ID `7c829a03-fb24-4b57-9b03-65f43ed19395`:

    ```
    $ curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" http://api.creativecommons.engineering/v1/images/7c829a03-fb24-4b57-9b03-65f43ed19395
    ```
    """
    image_detail_response = {
        "200": openapi.Response(
            description="OK",
            examples={
                "application/json": {
                    "title": "exam test",
                    "id": "7c829a03-fb24-4b57-9b03-65f43ed19395",
                    "creator": "Sean MacEntee",
                    "creator_url": "https://www.flickr.com/photos/18090920@N07",
                    "tags": [
                        {
                            "name": "exam"
                        },
                        {
                            "name": "test"
                        }
                    ],
                    "url": "https://live.staticflickr.com/5122/5264886972_3234d62748.jpg",
                    "thumbnail": "https://api.creativecommons.engineering/v1/thumbs/7c829a03-fb24-4b57-9b03-65f43ed19395",
                    "provider": "flickr",
                    "source": "flickr",
                    "license": "by",
                    "license_version": "2.0",
                    "license_url": "https://creativecommons.org/licenses/by/2.0/",
                    "foreign_landing_url": "https://www.flickr.com/photos/18090920@N07/5264886972",
                    "detail_url": "http://api.creativecommons.engineering/v1/images/7c829a03-fb24-4b57-9b03-65f43ed19395",
                    "related_url": "http://api.creativecommons.engineering/v1/recommendations/images/7c829a03-fb24-4b57-9b03-65f43ed19395",
                    "height": 167,
                    "width": 500,
                    "attribution": "\"exam test\" by Sean MacEntee is licensed under CC-BY 2.0. To view a copy of this license, visit https://creativecommons.org/licenses/by/2.0/."
                }
            },
            schema=ImageSerializer
        ),
        "404": openapi.Response(
            description='Not Found',
            examples={
                "application/json": {
                    "detail": "Not found."
                }
            }
        )
    }

    @swagger_auto_schema(operation_id="image_detail",
                         operation_description=image_detail_description,
                         responses=image_detail_response)
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
    oembed_list_description = \
    """
    Retrieve embedded content from a specified URL

    Example using URL `https://ccsearch.creativecommons.org/photos/7c829a03-fb24-4b57-9b03-65f43ed19395`:

    ```
    $ curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" http://api.creativecommons.engineering/v1/oembed?url=https://ccsearch.creativecommons.org/photos/7c829a03-fb24-4b57-9b03-65f43ed19395
    ```
    """
    oembed_list_response = {
        "200": openapi.Response(
            description="OK",
            examples={
                "application/json": {
                    "version": 1,
                    "type": "photo",
                    "width": 500,
                    "height": 167,
                    "title": "exam test",
                    "author_name": "Sean MacEntee",
                    "author_url": "https://www.flickr.com/photos/18090920@N07",
                    "license_url": "https://creativecommons.org/licenses/by/2.0/"
                }
            }
        ),
        "404": openapi.Response(
            description="Not Found",
            examples={
                "application/json": {
                    "detail": "An internal server error occurred."
                }
            }
        )
    }
    @swagger_auto_schema(operation_id="oembed_list",
                         operation_description=oembed_list_description,
                         query_serializer=OembedSerializer,
                         responses=oembed_list_response)
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

    Report issue about a particular image ID.

    Example using image ID `7c829a03-fb24-4b57-9b03-65f43ed19395`:

    ```
    $ curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" -d '{"reason": "mature", "identifier": "7c829a03-fb24-4b57-9b03-65f43ed19395", "description": "string"}' https://api.creativecommons.engineering/v1/images/7c829a03-fb24-4b57-9b03-65f43ed19395/report
    ```
    """
    queryset = ImageReport.objects.all()
    serializer_class = ReportImageSerializer
