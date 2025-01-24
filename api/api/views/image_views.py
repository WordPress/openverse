import io

from django.conf import settings
from django.shortcuts import aget_object_or_404
from rest_framework.decorators import action
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
from api.models import Image
from api.serializers.image_serializers import (
    ImageReportRequestSerializer,
    ImageSearchRequestSerializer,
    ImageSerializer,
    OembedRequestSerializer,
    OembedSerializer,
)
from api.utils import image_proxy
from api.utils.aiohttp import get_aiohttp_session
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
        return super().get_queryset().select_related("sensitive_image")

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

            async with session.get(
                image.url, headers=self.OEMBED_HEADERS
            ) as image_file:
                image_content = await image_file.content.read()

            with PILImage.open(io.BytesIO(image_content)) as image_file:
                width, height = image_file.size

            context |= {
                "width": width,
                "height": height,
            }

        serializer = self.get_serializer(image, context=context)
        return Response(data=await serializer.adata)

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
            width=image.width,
        )

    @thumbnail_docs
    @MediaViewSet.thumbnail_action
    async def thumbnail(self, request, identifier):
        """Retrieve the scaled down and compressed thumbnail of the image."""
        return await super().thumbnail(request)

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
