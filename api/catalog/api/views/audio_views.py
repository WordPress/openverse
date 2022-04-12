import logging

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
    AudioReportSerializer,
    AudioSearchRequestSerializer,
    AudioSerializer,
    AudioWaveformSerializer,
)
from catalog.api.serializers.media_serializers import MediaThumbnailRequestSerializer
from catalog.api.utils.exceptions import get_api_exception
from catalog.api.utils.throttle import OneThousandPerMinute
from catalog.api.views.media_views import MediaViewSet
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response


log = logging.getLogger(__name__)


@method_decorator(swagger_auto_schema(**AudioSearch.swagger_setup), "list")
@method_decorator(swagger_auto_schema(**AudioStats.swagger_setup), "stats")
@method_decorator(swagger_auto_schema(**AudioDetail.swagger_setup), "retrieve")
@method_decorator(swagger_auto_schema(**AudioRelated.swagger_setup), "related")
@method_decorator(swagger_auto_schema(**AudioComplain.swagger_setup), "report")
@method_decorator(swagger_auto_schema(**AudioThumbnail.swagger_setup), "thumbnail")
@method_decorator(swagger_auto_schema(auto_schema=None), "waveform")
class AudioViewSet(MediaViewSet):
    """
    Viewset for all endpoints pertaining to audio.
    """

    model_class = Audio
    query_serializer_class = AudioSearchRequestSerializer
    default_index = "audio"
    qa_index = "search-qa-audio"

    serializer_class = AudioSerializer

    # Extra actions

    @action(
        detail=True,
        url_path="thumb",
        url_name="thumb",
        serializer_class=MediaThumbnailRequestSerializer,
        throttle_classes=[OneThousandPerMinute],
    )
    def thumbnail(self, request, *_, **__):
        audio = self.get_object()

        image_url = None
        if thumbnail := audio.thumbnail:
            image_url = thumbnail
        elif audio.audio_set and (thumbnail := audio.audio_set.thumbnail):
            image_url = thumbnail
        if not image_url:
            raise get_api_exception("Could not find artwork.", 404)

        return super().thumbnail(image_url, request)

    @action(
        detail=True,
        serializer_class=AudioWaveformSerializer,
        throttle_classes=[OneThousandPerMinute],
    )
    def waveform(self, *_, **__):
        audio = self.get_object()

        try:
            obj = {"points": audio.get_or_create_waveform()}
            serializer = self.get_serializer(obj)

            return Response(status=200, data=serializer.data)
        except Exception as e:
            raise get_api_exception(getattr(e, "message", str(e)))

    @action(detail=True, methods=["post"], serializer_class=AudioReportSerializer)
    def report(self, *args, **kwargs):
        return super().report(*args, **kwargs)
