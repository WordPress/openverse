import io
import logging

import libxmp
import piexif
import requests
from PIL import Image as img
from django.conf import settings
from django.http.response import HttpResponse, FileResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from urllib.error import HTTPError
from urllib.request import urlopen

import catalog.api.controllers.search_controller as search_controller
from catalog.api.examples import (
    image_search_curl,
    image_search_200_example,
    image_search_400_example,
    recommendations_images_read_curl,
    recommendations_images_read_200_example,
    recommendations_images_read_404_example,
    image_detail_curl,
    image_detail_200_example,
    image_detail_404_example,
    oembed_list_200_example,
    oembed_list_404_example,
    image_stats_curl,
    image_stats_200_example,
    report_image_curl,
    images_report_create_201_example,
)
from catalog.api.models import Image, ImageReport
from catalog.api.serializers.error_serializers import (
    InputErrorSerializer,
    NotFoundErrorSerializer,
)
from catalog.api.serializers.image_serializers import (
    ImageSearchQueryStringSerializer,
    ImageSearchResultsSerializer,
    ImageSerializer,
    ReportImageSerializer,
    WatermarkQueryStringSerializer,
    OembedSerializer,
    OembedResponseSerializer,
    AboutImageSerializer,
    ProxiedImageSerializer,
)
from catalog.api.utils import ccrel
from catalog.api.utils.throttle import OneThousandPerMinute
from catalog.api.utils.exceptions import input_error_response
from catalog.api.utils.watermark import watermark
from catalog.api.views.media_views import (
    refer_sample,
    RESULTS,
    RESULT_COUNT,
    PAGE_COUNT,
    fields_to_md,
    SearchMedia,
    RelatedMedia,
    MediaDetail,
    MediaStats,
)
from catalog.custom_auto_schema import CustomAutoSchema

log = logging.getLogger(__name__)


class SearchImages(SearchMedia):
    image_search_description = f"""
image_search is an API endpoint to search images using a query string.

By using this endpoint, you can obtain search results based on specified query
and optionally filter results by
{fields_to_md(ImageSearchQueryStringSerializer.fields_names)}. 

Results are ranked in order of relevance.

{SearchMedia.search_description}"""  # noqa

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

    @swagger_auto_schema(operation_id='image_search',
                         operation_description=image_search_description,
                         query_serializer=ImageSearchQueryStringSerializer,
                         responses=image_search_response,
                         code_examples=[
                             {
                                 'lang': 'Bash',
                                 'source': image_search_curl
                             }
                         ])
    def get(self, request, format=None):
        # Parse and validate query parameters
        return self._get(
            request,
            'image',
            'search-qa-image',
            ImageSearchQueryStringSerializer,
            ImageSerializer,
            ImageSearchResultsSerializer,
        )


class RelatedImage(RelatedMedia):
    recommendations_images_read_description = f"""
recommendations_images_read is an API endpoint to get related images 
for a specified image ID.

By using this endpoint, you can get the details of related images such as 
{fields_to_md(ImageSerializer.fields_names)}.

{RelatedMedia.recommendations_read_description}"""  # noqa

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

    @swagger_auto_schema(operation_id="recommendations_images_read",
                         operation_description=recommendations_images_read_description,  # noqa: E501
                         responses=recommendations_images_read_response,
                         code_examples=[
                             {
                                 'lang': 'Bash',
                                 'source': recommendations_images_read_curl
                             }
                         ],
                         manual_parameters=[
                             openapi.Parameter(
                                 'identifier', openapi.IN_PATH,
                                 "The unique identifier for the image.",
                                 type=openapi.TYPE_STRING,
                                 required=True
                             ),
                         ])
    def get(self, request, identifier, format=None):
        related, result_count = search_controller.related_media(
            uuid=identifier,
            index='image',
            request=request,
            filter_dead=True
        )

        context = {'request': request}
        serialized_related = ImageSerializer(
            related,
            many=True,
            context=context
        ).data
        response_data = {
            RESULT_COUNT: result_count,
            PAGE_COUNT: 0,
            RESULTS: serialized_related
        }
        serialized_response = ImageSearchResultsSerializer(data=response_data)
        return Response(status=200, data=serialized_response.initial_data)


class ImageDetail(MediaDetail):
    serializer_class = ImageSerializer
    queryset = Image.objects.all()
    image_detail_description = f"""
image_detail is an API endpoint to get the details of a specified image ID.

By using this endpoint, you can image details such as
{fields_to_md(ImageSerializer.fields_names)}.

{MediaDetail.detail_description}"""  # noqa

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

    @swagger_auto_schema(operation_id="image_detail",
                         operation_description=image_detail_description,
                         responses=image_detail_response,
                         code_examples=[
                             {
                                 'lang': 'Bash',
                                 'source': image_detail_curl
                             }
                         ])
    def get(self, request, identifier, format=None):
        """ Get the details of a single image. """
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
                    f'Failed to add XMP metadata to {image_record.identifier}'
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
        curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" http://api.openverse.engineering/v1/oembed?url=https://ccsearch.creativecommons.org/photos/7c829a03-fb24-4b57-9b03-65f43ed19395
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
    report_image_description = f"""
images_report_create is an API endpoint to report an issue about a specified 
image ID to Openverse.

By using this endpoint, you can report an image if it infringes copyright, 
contains mature or sensitive content and others.

{refer_sample}"""  # noqa

    swagger_schema = CustomAutoSchema
    queryset = ImageReport.objects.all()
    serializer_class = ReportImageSerializer

    @swagger_auto_schema(operation_id='images_report_create',
                         operation_description=report_image_description,
                         query_serializer=ReportImageSerializer,
                         responses={
                             "201": openapi.Response(
                                 description="OK",
                                 examples=images_report_create_201_example,
                                 schema=ReportImageSerializer
                             )
                         },
                         code_examples=[
                             {
                                 'lang': 'Bash',
                                 'source': report_image_curl,
                             }
                         ])
    def post(self, request, *args, **kwargs):
        return super(ReportImageView, self).post(request, *args, **kwargs)


class ImageStats(MediaStats):
    image_stats_description = f"""
image_stats is an API endpoint to get a list of all content providers and their
respective number of images in the Openverse catalog.

{MediaStats.media_stats_description}"""  # noqa

    image_stats_response = {
        "200": openapi.Response(
            description="OK",
            examples=image_stats_200_example,
            schema=AboutImageSerializer(many=True)
        )
    }

    @swagger_auto_schema(operation_id='image_stats',
                         operation_description=image_stats_description,
                         responses=image_stats_response,
                         code_examples=[
                             {
                                 'lang': 'Bash',
                                 'source': image_stats_curl,
                             }
                         ])
    def get(self, request, format=None):
        return self._get(request, 'image')


class ProxiedImage(APIView):
    """
    Return the thumb of an image.
    """

    lookup_field = 'identifier'
    queryset = Image.objects.all()
    throttle_classes = [OneThousandPerMinute]
    swagger_schema = None

    def get(self, request, identifier, format=None):
        serialized = ProxiedImageSerializer(data=request.data)
        serialized.is_valid()
        try:
            image = Image.objects.get(identifier=identifier)
        except Image.DoesNotExist:
            return Response(status=404, data='Not Found')

        if serialized.data['full_size']:
            proxy_upstream = f'{settings.THUMBNAIL_PROXY_URL}/{image.url}'
        else:
            proxy_upstream = f'{settings.THUMBNAIL_PROXY_URL}/{settings.THUMBNAIL_WIDTH_PX}' \
                             f',fit/{image.url}'
        try:
            upstream_response = urlopen(proxy_upstream)
            status = upstream_response.status
            content_type = upstream_response.headers.get('Content-Type')
        except HTTPError:
            log.info('Failed to render thumbnail: ', exc_info=True)
            return HttpResponse(status=500)

        response = HttpResponse(
            upstream_response.read(),
            status=status,
            content_type=content_type
        )

        return response
