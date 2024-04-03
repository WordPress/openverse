from django.conf import settings
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, NotFound
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, extend_schema_view

from api.constants.media_types import AUDIO_TYPE
from api.docs.audio_docs import (
    detail,
    related,
    report,
    search,
    stats,
    waveform,
)
from api.docs.audio_docs import thumbnail as thumbnail_docs
from api.models import Audio
from api.serializers.audio_serializers import (
    AudioReportRequestSerializer,
    AudioSearchRequestSerializer,
    AudioSerializer,
    AudioWaveformSerializer,
)
from api.utils import image_proxy
from api.utils.cache_control import cache_control
from api.utils.ttl import ttl
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

    def get_queryset(self):
        return super().get_queryset().select_related("sensitive_audio", "audioset")

    # Extra actions

    async def get_image_proxy_media_info(self) -> image_proxy.MediaInfo:
        audio = await self.aget_object()

        image_url = None
        if audio_thumbnail := audio.thumbnail:
            image_url = audio_thumbnail
        elif audio.audio_set and (audio_thumbnail := audio.audio_set.thumbnail):
            image_url = audio_thumbnail
        if not image_url:
            raise NotFound("Could not find artwork.")

        return image_proxy.MediaInfo(
            media_identifier=audio.identifier,
            media_provider=audio.provider,
            image_url=image_url,
        )

    @thumbnail_docs
    @MediaViewSet.thumbnail_action
    async def thumbnail(self, *args, **kwargs):
        """
        Retrieve the scaled down and compressed thumbnail of the artwork of an
        audio track or its audio set.
        """
        return await super().thumbnail(*args, **kwargs)

    @waveform
    @action(
        detail=True,
        serializer_class=AudioWaveformSerializer,
        throttle_classes=[AnonThumbnailRateThrottle, OAuth2IdThumbnailRateThrottle],
    )
    @method_decorator(cache_control(max_age=ttl(weeks=52), public=True))
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
