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
from cccatalog.api.utils.view_count import track_model_views
from cccatalog.api.serializers.image_serializers import\
    ImageSearchResultsSerializer, ImageSerializer,\
    InputErrorSerializer, ImageSearchQueryStringSerializer,\
    WatermarkQueryStringSerializer, ReportImageSerializer,\
    OembedSerializer
from cccatalog.settings import THUMBNAIL_PROXY_URL
from cccatalog.api.utils.view_count import _get_user_ip
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


class SearchImages(APIView):
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
    """

    @swagger_auto_schema(operation_id='image_search',
                         query_serializer=ImageSearchQueryStringSerializer,
                         responses={
                             200: ImageSearchResultsSerializer(many=True),
                             400: InputErrorSerializer,
                         })
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
    """
    Given a UUID, return images related to the result.
    """
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

    @swagger_auto_schema(operation_id="image_detail",
                         operation_description="Load the details of a"
                                               " particular image ID.",
                         responses={
                             200: ImageSerializer,
                             404: 'Not Found'
                         })
    @track_model_views(Image)
    def get(self, request, identifier, format=None, view_count=0):
        """ Get the details of a single list. """
        resp = self.retrieve(request, identifier)
        # Fix links to creator and foreign landing URLs.
        # Proxy insecure HTTP images at full resolution.
        if 'http://' in resp.data[search_controller.URL]:
            original = resp.data[search_controller.URL]
            secure = '{proxy_url}/{original}'.format(
                proxy_url=THUMBNAIL_PROXY_URL,
                original=original
            )
            resp.data[search_controller.URL] = secure

        return resp

    @swagger_auto_schema(operation_id="image_delete",
                         operation_description="Delete image of given ID.",
                         responses={
                             204: '',
                             404: 'Not Found'
                         })
    def delete(self, request, identifier, format=None):
        try:
            image = Image.objects.get(identifier=identifier)
            es = search_controller.es
            es.delete(index='image', id=image.id)
            delete_log = DeletedImage(
                identifier=image.identifier
            )
            image.delete()
            delete_log.save()
        except Image.DoesNotExist:
            return Response(status=404, data='Not Found')
        # Mark as removed in upstream database
        image = Image.objects.using('upstream').get(identifier=identifier)
        image.removed_from_source = True
        image.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


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

    @swagger_auto_schema(operation_id="oembed_list",
                         query_serializer=OembedSerializer,
                         responses={
                             200: '',
                             404: 'Not Found'
                         })
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
    queryset = ImageReport.objects.all()
    serializer_class = ReportImageSerializer
