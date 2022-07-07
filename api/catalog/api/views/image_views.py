import io

from django.conf import settings
from django.http.response import FileResponse, Http404, HttpResponse
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.response import Response

import piexif
import requests
from drf_yasg.utils import swagger_auto_schema
from PIL import Image as PILImage

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
from catalog.api.utils.exceptions import get_api_exception
from catalog.api.utils.throttle import OneThousandPerMinute
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
    """
    Viewset for all endpoints pertaining to images.
    """

    model_class = Image
    query_serializer_class = ImageSearchRequestSerializer
    default_index = "image"
    qa_index = "search-qa-image"

    serializer_class = ImageSerializer

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
        identifier = url.rsplit("/", 1)[1]
        try:
            image = self.get_queryset().get(identifier=identifier)
        except Image.DoesNotExist:
            return get_api_exception("Could not find image.", 404)
        if not (image.height and image.width):
            image_file = requests.get(image.url)
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
        throttle_classes=[OneThousandPerMinute],
    )
    def thumbnail(self, request, *_, **__):
        image = self.get_object()

        image_url = image.url
        if not image_url:
            raise get_api_exception("Could not find image.", 404)

        return super().thumbnail(image_url, request)

    @action(detail=True, url_path="watermark", url_name="watermark")
    def watermark(self, request, *_, **__):
        if not settings.WATERMARK_ENABLED:
            raise Http404  # watermark feature is disabled

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
            exif_bytes = piexif.dump(exif)
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
        """
        PIL crashes if exif_bytes=None, so we have to wrap it to avoid littering
        the code with branches.
        """
        if exif_bytes:
            pil_img.save(destination, "jpeg", exif=exif_bytes)
        else:
            pil_img.save(destination, "jpeg")
