from django.conf import settings
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, NotFound
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, extend_schema_view

from api.constants.media_types import AUDIO_TYPE
from api.docs.audio_docs import (
    creator_collection,
    detail,
    related,
    report,
    search,
    source_collection,
    stats,
    tag_collection,
    thumbnail as thumbnail_docs,
    waveform,
)
from api.models import Audio
from api.serializers.audio_serializers import (
    AudioCollectionRequestSerializer,
    AudioReportRequestSerializer,
    AudioSearchRequestSerializer,
    AudioSerializer,
    AudioWaveformSerializer,
)
from api.utils.image_proxy import ImageProxyMediaInfo
from api.utils.throttle import AnonThumbnailRateThrottle, OAuth2IdThumbnailRateThrottle
from api.views.media_views import MediaViewSet


@extend_schema(tags=["audio"])
@extend_schema_view(
    list=search,
    stats=stats,
    retrieve=detail,
    related=related,
)
class AudioViewSet(MediaViewSet):
    """Viewset for all endpoints pertaining to audio."""

    model_class = Audio
    media_type = AUDIO_TYPE
    query_serializer_class = AudioSearchRequestSerializer
    default_index = settings.MEDIA_INDEX_MAPPING[AUDIO_TYPE]

    serializer_class = AudioSerializer
    collection_serializer_class = AudioCollectionRequestSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("mature_audio", "audioset")

    # Extra actions
    @creator_collection
    @action(
        detail=False,
        methods=["get"],
        url_path="source/(?P<source>[^/.]+)/creator/(?P<creator>.+)",
    )
    def creator_collection(self, request, source, creator):
        return super().creator_collection(request, source, creator)

    @source_collection
    @action(
        detail=False,
        methods=["get"],
        url_path="source/(?P<source>[^/.]+)",
    )
    def source_collection(self, request, source):
        return super().source_collection(request, source)

    @tag_collection
    @action(
        detail=False,
        methods=["get"],
        url_path="tag/(?P<tag>[^/.]+)",
    )
    def tag_collection(self, request, tag, *_, **__):
        return super().tag_collection(request, tag, *_, **__)

    async def get_image_proxy_media_info(self) -> ImageProxyMediaInfo:
        audio = await self.aget_object()

        image_url = None
        if audio_thumbnail := audio.thumbnail:
            image_url = audio_thumbnail
        elif audio.audio_set and (audio_thumbnail := audio.audio_set.thumbnail):
            image_url = audio_thumbnail
        if not image_url:
            raise NotFound("Could not find artwork.")

        return ImageProxyMediaInfo(
            media_identifier=audio.identifier,
            media_provider=audio.provider,
            image_url=image_url,
        )

    thumbnail = thumbnail_docs(MediaViewSet.thumbnail)

    @waveform
    @action(
        detail=True,
        serializer_class=AudioWaveformSerializer,
        throttle_classes=[AnonThumbnailRateThrottle, OAuth2IdThumbnailRateThrottle],
    )
    def waveform(self, *_, **__):
        """
        Get the waveform peaks for an audio track.

        The peaks are provided as a list of numbers, each of these numbers being
        a fraction between 0 and 1. The list contains approximately 1000 numbers,
        although it can be slightly higher or lower, depending on the track's length.
        """

        audio = self.get_object()

        try:
            obj = {"points": audio.get_or_create_waveform()}
            serializer = self.get_serializer(obj)

            return Response(status=200, data=serializer.data)
        except Exception as e:
            raise APIException(getattr(e, "message", str(e)))

    @report
    @action(
        detail=True,
        methods=["post"],
        serializer_class=AudioReportRequestSerializer,
    )
    def report(self, request, identifier):
        """
        Report an issue about a specified audio track to Openverse.

        By using this endpoint, you can report an audio track if it infringes
        copyright, contains mature or sensitive content or some other reason.
        """

        return super().report(request, identifier)
