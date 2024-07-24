import io

from django.conf import settings
from django.http.response import FileResponse, HttpResponse
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, extend_schema_view
from PIL import Image as PILImage

from api.constants.media_types import IMAGE_TYPE
from api.docs.image_docs import (
    detail,
    oembed,
    related,
    report,
    search,
    stats,
)
from api.docs.image_docs import thumbnail as thumbnail_docs
from api.docs.image_docs import watermark as watermark_doc
from api.models import Image
from api.serializers.image_serializers import (
    ImageReportRequestSerializer,
    ImageSearchRequestSerializer,
    ImageSerializer,
    OembedRequestSerializer,
    OembedSerializer,
    WatermarkRequestSerializer,
)
from api.utils import image_proxy
from api.utils.aiohttp import get_aiohttp_session
from api.utils.asyncio import aget_object_or_404
from api.utils.watermark import UpstreamWatermarkException, watermark
from api.views.media_views import MediaViewSet


@extend_schema(tags=["images"])
@extend_schema_view(
    list=search,
    stats=stats,
    retrieve=detail,
    related=related,
)
class ImageViewSet(MediaViewSet):
    """Viewset for all endpoints pertaining to images."""

    model_class = Image
    media_type = IMAGE_TYPE
    query_serializer_class = ImageSearchRequestSerializer
    default_index = settings.MEDIA_INDEX_MAPPING[IMAGE_TYPE]

    serializer_class = ImageSerializer

    OEMBED_HEADERS = {
        "User-Agent": settings.OUTBOUND_USER_AGENT_TEMPLATE.format(purpose="OEmbed"),
    }

    def get_queryset(self):
        return super().get_queryset().select_related("sensitive_media")

    # Extra actions

    @oembed
    @action(
        detail=False,
        url_path="oembed",
        url_name="oembed",
        serializer_class=OembedSerializer,
    )
    async def oembed(self, request, *_, **__):
        """
        Retrieve the structured data for a specified image URL as per the
        [oEmbed spec](https://oembed.com/).

        This info can be used to embed the image on the consumer's website. Only
        JSON format is supported.
        """

        params = OembedRequestSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        identifier = params.validated_data["identifier"]
        context = self.get_serializer_context()

        image = await aget_object_or_404(Image, identifier=identifier)

        if not (image.height and image.width):
            session = await get_aiohttp_session()
            image_file = await session.get(image.url, headers=self.OEMBED_HEADERS)
            image_content = await image_file.content.read()
            width, height = PILImage.open(io.BytesIO(image_content)).size
            context |= {
                "width": width,
                "height": height,
            }

        serializer = self.get_serializer(image, context=context)
        return Response(data=serializer.data)

    async def get_image_proxy_media_info(self) -> image_proxy.MediaInfo:
        image = await self.aget_object()
        image_url = image.url
        # Hotfix to use thumbnails for SMK images
        # TODO: Remove when small thumbnail issues are resolved
        if "iip.smk.dk" in image_url and image.thumbnail:
            image_url = image.thumbnail

        return image_proxy.MediaInfo(
            media_identifier=image.identifier,
            media_provider=image.provider,
            image_url=image_url,
        )

    @thumbnail_docs
    @MediaViewSet.thumbnail_action
    async def thumbnail(self, *args, **kwargs):
        """Retrieve the scaled down and compressed thumbnail of the image."""
        return await super().thumbnail(*args, **kwargs)

    @watermark_doc
    @action(detail=True, url_path="watermark", url_name="watermark")
    def watermark(self, request, *_, **__):  # noqa: D401
        """
        Note that this endpoint is deprecated.

        ---

        🚧 **TODO:** Document this.
        """

        if not settings.WATERMARK_ENABLED:
            raise NotFound("The watermark feature is currently disabled.")

        params = WatermarkRequestSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)

        image = self.get_object()
        image_url = image.url

        if image_url.endswith(".svg") or getattr(image, "filetype") == "svg":
            raise UpstreamWatermarkException(
                "Unsupported media type: SVG images are not supported for watermarking."
            )

        image_info = {
            attr: getattr(image, attr)
            for attr in ["title", "creator", "license", "license_version"]
        }

        # Create the actual watermarked image.
        watermarked, exif = watermark(image_url, image_info, params.data["watermark"])
        img_bytes = io.BytesIO()
        self._save_wrapper(watermarked, exif, img_bytes)

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

            from api.utils import ccrel

            try:
                with_xmp = ccrel.embed_xmp_bytes(img_bytes, work_properties)
                return FileResponse(with_xmp, content_type="image/jpeg")
            except (libxmp.XMPError, AttributeError):
                # Just send the EXIF-ified file if libxmp fails to add metadata
                response = HttpResponse(content_type="image/jpeg")
                self._save_wrapper(watermarked, exif, response)
                return response
        else:
            response = HttpResponse(img_bytes, content_type="image/jpeg")
            self._save_wrapper(watermarked, exif, response)
            return response

    @report
    @action(
        detail=True,
        methods=["post"],
        serializer_class=ImageReportRequestSerializer,
    )
    def report(self, request, identifier):
        """
        Report an issue about a specified image to Openverse.

        By using this endpoint, you can report an image if it infringes
        copyright, contains mature or sensitive content or some other reason.
        """

        return super().report(request, identifier)

    # Helper functions

    @staticmethod
    def _save_wrapper(pil_img, exif_bytes, destination):
        """Prevent PIL from crashing if ``exif_bytes`` is ``None``."""

        if exif_bytes:
            # Re-insert EXIF metadata
            pil_img.save(destination, "jpeg", exif=exif_bytes)
        else:
            pil_img.save(destination, "jpeg")
