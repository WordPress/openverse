from django.conf import settings
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, NotFound
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from catalog.api.constants.media_types import AUDIO_TYPE
from catalog.api.docs.audio_docs import (
    AudioComplain,
    AudioDetail,
    AudioRelated,
    AudioSearch,
    AudioStats,
    AudioThumbnail,
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


@method_decorator(swagger_auto_schema(**AudioSearch.swagger_setup), "list")
@method_decorator(swagger_auto_schema(**AudioStats.swagger_setup), "stats")
@method_decorator(swagger_auto_schema(**AudioDetail.swagger_setup), "retrieve")
@method_decorator(swagger_auto_schema(**AudioRelated.swagger_setup), "related")
@method_decorator(swagger_auto_schema(**AudioComplain.swagger_setup), "report")
@method_decorator(swagger_auto_schema(**AudioThumbnail.swagger_setup), "thumbnail")
@method_decorator(swagger_auto_schema(auto_schema=None), "waveform")
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

    @action(
        detail=True,
        url_path="thumb",
        url_name="thumb",
        serializer_class=MediaThumbnailRequestSerializer,
        throttle_classes=[AnonThumbnailRateThrottle, OAuth2IdThumbnailRateThrottle],
    )
    def thumbnail(self, request, *_, **__):
        audio = self.get_object()

        image_url = None
        if thumbnail := audio.thumbnail:
            image_url = thumbnail
        elif audio.audio_set and (thumbnail := audio.audio_set.thumbnail):
            image_url = thumbnail
        if not image_url:
            raise NotFound("Could not find artwork.")

        return super().thumbnail(image_url, request)

    @action(
        detail=True,
        serializer_class=AudioWaveformSerializer,
        throttle_classes=[AnonThumbnailRateThrottle, OAuth2IdThumbnailRateThrottle],
    )
    def waveform(self, *_, **__):
        audio = self.get_object()

        try:
            obj = {"points": audio.get_or_create_waveform()}
            serializer = self.get_serializer(obj)

            return Response(status=200, data=serializer.data)
        except Exception as e:
            raise APIException(getattr(e, "message", str(e)))

    @action(
        detail=True,
        methods=["post"],
        serializer_class=AudioReportRequestSerializer,
    )
    def report(self, request, identifier):
        return super().report(request, identifier)
