from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from cccatalog.api.models import Image, ContentProvider
from cccatalog.api.utils.validate_images import validate_images
from cccatalog.api.utils.view_count import track_model_views
from cccatalog.api.utils import ccrel
from rest_framework.reverse import reverse
from cccatalog.api.serializers.search_serializers import\
    ImageSearchResultsSerializer, ImageSerializer,\
    ValidationErrorSerializer, ImageSearchQueryStringSerializer
from cccatalog.api.serializers.image_serializers import ImageDetailSerializer,\
    WatermarkQueryStringSerializer
from cccatalog.settings import THUMBNAIL_PROXY_URL, PROXY_THUMBS, PROXY_ALL
from cccatalog.api.utils.view_count import _get_user_ip
from urllib.parse import urlparse
from cccatalog.api.utils.watermark import watermark
from django.http.response import HttpResponse, FileResponse
import cccatalog.api.controllers.search_controller as search_controller
import logging
import piexif
import io
import libxmp

log = logging.getLogger(__name__)

FOREIGN_LANDING_URL = 'foreign_landing_url'
CREATOR_URL = 'creator_url'
RESULTS = 'results'
PAGE = 'page'
PAGESIZE = 'pagesize'
VALIDATION_ERROR = 'validation_error'
FILTER_DEAD = 'filter_dead'
THUMBNAIL = 'thumbnail'
URL = 'url'
THUMBNAIL_WIDTH_PX = 600
PROVIDER = 'provider'
QA = 'qa'


def _add_protocol(url: str):
    """
    Some fields in the database contain incomplete URLs, leading to unexpected
    behavior in downstream consumers. This helper verifies that we always return
    fully formed URLs in such situations.
    """
    parsed = urlparse(url)
    if parsed.scheme == '':
        return 'https://' + url
    else:
        return url


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

        hashed_ip = hash(_get_user_ip(request))
        page_param = params.data[PAGE]
        page_size = params.data[PAGESIZE]
        qa = params.data[QA]
        search_index = 'search-qa' if qa else 'image'
        try:
            search_results = search_controller.search(params,
                                                      index=search_index,
                                                      page_size=page_size,
                                                      ip=hashed_ip,
                                                      page=page_param)
        except ValueError:
            return Response(
                status=400,
                data={
                    VALIDATION_ERROR: 'Deep pagination is not allowed.'
                }
            )

        # Fetch each result from Elasticsearch. Resolve links to detail views.
        results = []
        to_validate = []
        for result in search_results:
            url = request.build_absolute_uri(
                reverse('image-detail', [result.identifier])
            )
            result.detail = url
            to_validate.append(result.url)
            results.append(result)
        if params.data[FILTER_DEAD]:
            validate_images(results, to_validate)
        serialized_results =\
            ImageSerializer(results, many=True).data
        # Elasticsearch does not allow deep pagination of ranked queries.
        # Adjust returned page count to reflect this.
        natural_page_count = int(search_results.hits.total / page_size)
        last_allowed_page = int((5000 + page_size / 2) / page_size)
        page_count = min(natural_page_count, last_allowed_page)

        result_count = search_results.hits.total
        if len(results) < page_size and page_count == 0:
            result_count = len(results)
        response_data = {
            'result_count': result_count,
            'page_count': page_count,
            RESULTS: serialized_results
        }
        # Post-process the search results to fix malformed URLs and insecure
        # HTTP thumbnails.
        for idx, res in enumerate(serialized_results):
            if PROXY_THUMBS:
                provider = res[PROVIDER]
                # Proxy either the thumbnail or URL, depending on whether
                # a thumbnail was provided.
                if THUMBNAIL in res and provider not in PROXY_ALL:
                    to_proxy = THUMBNAIL
                else:
                    to_proxy = URL
                if 'http://' in res[to_proxy] or provider in PROXY_ALL:
                    original = res[to_proxy]
                    secure = '{proxy_url}/{width}/{original}'.format(
                        proxy_url=THUMBNAIL_PROXY_URL,
                        width=THUMBNAIL_WIDTH_PX,
                        original=original
                    )
                    response_data[RESULTS][idx][THUMBNAIL] = secure
            if FOREIGN_LANDING_URL in res:
                foreign = _add_protocol(res[FOREIGN_LANDING_URL])
                response_data[RESULTS][idx][FOREIGN_LANDING_URL] = foreign
            if CREATOR_URL in res:
                creator_url = _add_protocol(res[CREATOR_URL])
                response_data[RESULTS][idx][CREATOR_URL] = creator_url
        serialized_response = ImageSearchResultsSerializer(data=response_data)

        return Response(status=200, data=serialized_response.initial_data)


class ImageDetail(GenericAPIView, RetrieveModelMixin):
    serializer_class = ImageDetailSerializer
    queryset = Image.objects.all()
    lookup_field = 'identifier'

    @swagger_auto_schema(operation_id="image_detail",
                         operation_description="Load the details of a"
                                               " particular image ID.",
                         responses={
                             200: ImageDetailSerializer,
                             404: 'Not Found'
                         })
    def get(self, request, identifier, format=None, view_count=0):
        """ Get the details of a single list. """
        resp = self.retrieve(request, identifier)
        # Get pretty display name for a provider
        provider = resp.data[PROVIDER]
        try:
            provider_data = ContentProvider \
                .objects \
                .get(provider_identifier=provider)
            resp.data['provider'] = provider_data.provider_name
            resp.data['provider_url'] = provider_data.domain_name
        except ContentProvider.DoesNotExist:
            resp.data['provider'] = provider
            resp.data['provider_url'] = 'Unknown'
        # Add page views to the response.
        resp.data['view_count'] = view_count
        # Fix links to creator and foreign landing URLs.
        if CREATOR_URL in resp.data:
            creator_url = _add_protocol(resp.data[CREATOR_URL])
            resp.data[CREATOR_URL] = creator_url
        if FOREIGN_LANDING_URL in resp.data:
            foreign_landing_url = \
                _add_protocol(resp.data[FOREIGN_LANDING_URL])
            resp.data[FOREIGN_LANDING_URL] = foreign_landing_url
        # Proxy insecure HTTP images at full resolution.
        if 'http://' in resp.data[URL]:
            original = resp.data[URL]
            secure = '{proxy_url}/{original}'.format(
                proxy_url=THUMBNAIL_PROXY_URL,
                original=original
            )
            resp.data[URL] = secure

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
            return Response(
                status=400,
                data={
                    "validation_error": params.errors
                }
            )
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
