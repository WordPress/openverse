import io
import struct

from django.conf import settings
from django.http.response import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

import piexif
import requests
from drf_yasg.utils import swagger_auto_schema
from PIL import Image as PILImage

from catalog.api.constants.media_types import IMAGE_TYPE
from catalog.api.docs.image_docs import (
    ImageComplain,
    ImageDetail,
    ImageOembed,
    ImageRelated,
    ImageSearch,
    ImageStats,
    ImageThumbnail,
)
from catalog.api.models import Image
from catalog.api.serializers.image_serializers import (
    ImageReportRequestSerializer,
    ImageSearchRequestSerializer,
    ImageSerializer,
    OembedRequestSerializer,
    OembedSerializer,
    WatermarkRequestSerializer,
)
from catalog.api.serializers.media_serializers import MediaThumbnailRequestSerializer
from catalog.api.utils.throttle import (
    AnonThumbnailRateThrottle,
    OAuth2IdThumbnailRateThrottle,
)
from catalog.api.utils.watermark import watermark
from catalog.api.views.media_views import MediaViewSet


@method_decorator(swagger_auto_schema(**ImageSearch.swagger_setup), "list")
@method_decorator(swagger_auto_schema(**ImageStats.swagger_setup), "stats")
@method_decorator(swagger_auto_schema(**ImageDetail.swagger_setup), "retrieve")
@method_decorator(swagger_auto_schema(**ImageRelated.swagger_setup), "related")
@method_decorator(swagger_auto_schema(**ImageComplain.swagger_setup), "report")
@method_decorator(swagger_auto_schema(**ImageOembed.swagger_setup), "oembed")
@method_decorator(swagger_auto_schema(**ImageThumbnail.swagger_setup), "thumbnail")
@method_decorator(swagger_auto_schema(auto_schema=None), "watermark")
class ImageViewSet(MediaViewSet):
    """Viewset for all endpoints pertaining to images."""

    model_class = Image
    query_serializer_class = ImageSearchRequestSerializer
    default_index = settings.MEDIA_INDEX_MAPPING[IMAGE_TYPE]
    qa_index = "search-qa-image"

    serializer_class = ImageSerializer

    OEMBED_HEADERS = {
        "User-Agent": settings.OUTBOUND_USER_AGENT_TEMPLATE.format(purpose="OEmbed"),
    }

    def get_queryset(self):
        return super().get_queryset().select_related("mature_image")

    # Extra actions

    @action(
        detail=False,
        url_path="oembed",
        url_name="oembed",
        serializer_class=OembedSerializer,
    )
    def oembed(self, request, *_, **__):
        params = OembedRequestSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)

        context = self.get_serializer_context()

        url = params.validated_data["url"]
        if url.endswith("/"):
            url = url[:-1]
        identifier = url.rsplit("/", 1)[1]
        image = get_object_or_404(Image, identifier=identifier)
        if not (image.height and image.width):
            image_file = requests.get(image.url, headers=self.OEMBED_HEADERS)
            width, height = PILImage.open(io.BytesIO(image_file.content)).size
            context |= {
                "width": width,
                "height": height,
            }

        serializer = self.get_serializer(image, context=context)
        return Response(data=serializer.data)

    @action(
        detail=True,
        url_path="thumb",
        url_name="thumb",
        serializer_class=MediaThumbnailRequestSerializer,
        throttle_classes=[AnonThumbnailRateThrottle, OAuth2IdThumbnailRateThrottle],
    )
    def thumbnail(self, request, *_, **__):
        image = self.get_object()
        image_url = image.url
        # Hotfix to use thumbnails for SMK images
        # TODO: Remove when small thumbnail issues are resolved
        if "iip.smk.dk" in image_url and image.thumbnail:
            image_url = image.thumbnail

        return super().thumbnail(image_url, request)

    @action(detail=True, url_path="watermark", url_name="watermark")
    def watermark(self, request, *_, **__):
        if not settings.WATERMARK_ENABLED:
            raise NotFound("The watermark feature is currently disabled.")

        params = WatermarkRequestSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)

        image = self.get_object()
        image_url = image.url
        image_info = {
            attr: getattr(image, attr)
            for attr in ["title", "creator", "license", "license_version"]
        }

        # Create the actual watermarked image.
        watermarked, exif = watermark(image_url, image_info, params.data["watermark"])
        # Re-insert EXIF metadata.
        if exif:
            # piexif dump raises InvalidImageDataError which is a child class
            # of ValueError, and a struct error when the value is not
            # between -2147483648 and 2147483647
            # https://github.com/WordPress/openverse-api/issues/849
            try:
                exif_bytes = piexif.dump(exif)
            except (struct.error, ValueError):
                exif_bytes = None
        else:
            exif_bytes = None
        img_bytes = io.BytesIO()
        self._save_wrapper(watermarked, exif_bytes, img_bytes)

        if params.data["embed_metadata"]:
            # Embed ccREL metadata with XMP.
            work_properties = {
                "creator": image.creator,
                "license_url": image.license_url,
                "attribution": image.attribution,
                "work_landing_page": image.foreign_landing_url,
                "identifier": str(image.identifier),
            }

            # Import inside a function to allow server run without Exempi library
            import libxmp

            from catalog.api.utils import ccrel

            try:
                with_xmp = ccrel.embed_xmp_bytes(img_bytes, work_properties)
                return FileResponse(with_xmp, content_type="image/jpeg")
            except (libxmp.XMPError, AttributeError):
                # Just send the EXIF-ified file if libxmp fails to add metadata
                response = HttpResponse(content_type="image/jpeg")
                self._save_wrapper(watermarked, exif_bytes, response)
                return response
        else:
            response = HttpResponse(img_bytes, content_type="image/jpeg")
            self._save_wrapper(watermarked, exif_bytes, response)
            return response

    @action(
        detail=True,
        methods=["post"],
        serializer_class=ImageReportRequestSerializer,
    )
    def report(self, *args, **kwargs):
        return super().report(*args, **kwargs)

    # Helper functions

    @staticmethod
    def _save_wrapper(pil_img, exif_bytes, destination):
        """Prevent PIL from crashing if ``exif_bytes`` is ``None``."""

        if exif_bytes:
            pil_img.save(destination, "jpeg", exif=exif_bytes)
        else:
            pil_img.save(destination, "jpeg")
