from django.conf import settings
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, NotFound
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, extend_schema_view

from catalog.api.constants.media_types import AUDIO_TYPE
from catalog.api.docs.audio_docs import (
    detail,
    related,
    report,
    search,
    stats,
    thumbnail,
    waveform,
)
from catalog.api.models import Audio
from catalog.api.serializers.audio_serializers import (
    AudioReportRequestSerializer,
    AudioSearchRequestSerializer,
    AudioSerializer,
    AudioWaveformSerializer,
)
from catalog.api.serializers.media_serializers import MediaThumbnailRequestSerializer
from catalog.api.utils.throttle import (
    AnonThumbnailRateThrottle,
    OAuth2IdThumbnailRateThrottle,
)
from catalog.api.views.media_views import MediaViewSet


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
    query_serializer_class = AudioSearchRequestSerializer
    default_index = settings.MEDIA_INDEX_MAPPING[AUDIO_TYPE]
    qa_index = "search-qa-audio"

    serializer_class = AudioSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("mature_audio", "audioset")

    # Extra actions

    @thumbnail
    @action(
        detail=True,
        url_path="thumb",
        url_name="thumb",
        serializer_class=MediaThumbnailRequestSerializer,
        throttle_classes=[AnonThumbnailRateThrottle, OAuth2IdThumbnailRateThrottle],
    )
    def thumbnail(self, request, *_, **__):
        """
        Retrieve the scaled down and compressed thumbnail of the artwork of an
        audio track or its audio set.
        """

        audio = self.get_object()

        image_url = None
        if thumbnail := audio.thumbnail:
            image_url = thumbnail
        elif audio.audio_set and (thumbnail := audio.audio_set.thumbnail):
            image_url = thumbnail
        if not image_url:
            raise NotFound("Could not find artwork.")

        return super().thumbnail(image_url, request)

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
