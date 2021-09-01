import logging

from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from catalog.api.docs.audio_docs import (
    AudioSearch,
    AudioStats,
    AudioDetail,
    AudioRelated,
    AudioComplain,
)
from catalog.api.models import Audio
from catalog.api.serializers.audio_serializers import (
    AudioSearchRequestSerializer,
    AudioSerializer,
    AudioReportSerializer,
    AudioWaveformSerializer,
)
from catalog.api.utils.exceptions import get_api_exception
from catalog.api.utils.throttle import OneThousandPerMinute
from catalog.api.utils.waveform import (
    download_audio,
    generate_waveform,
    process_waveform_output,
    cleanup,
)
from catalog.api.views.media_views import MediaViewSet

log = logging.getLogger(__name__)


@method_decorator(swagger_auto_schema(**AudioSearch.swagger_setup), 'list')
@method_decorator(swagger_auto_schema(**AudioStats.swagger_setup), 'stats')
@method_decorator(swagger_auto_schema(**AudioDetail.swagger_setup), 'retrieve')
@method_decorator(swagger_auto_schema(**AudioRelated.swagger_setup), 'related')
@method_decorator(swagger_auto_schema(**AudioComplain.swagger_setup), 'report')
@method_decorator(swagger_auto_schema(auto_schema=None), 'thumbnail')
@method_decorator(swagger_auto_schema(auto_schema=None), 'waveform')
class AudioViewSet(MediaViewSet):
    """
    Viewset for all endpoints pertaining to audio.
    """

    model_class = Audio
    query_serializer_class = AudioSearchRequestSerializer
    default_index = 'audio'
    qa_index = 'search-qa-audio'

    serializer_class = AudioSerializer

    # Extra actions

    @action(detail=True,
            url_path='thumb',
            url_name='thumb',
            throttle_classes=[OneThousandPerMinute])
    def thumbnail(self, request, *_, **__):
        audio = self.get_object()

        image_url = None
        if thumbnail := audio.thumbnail:
            image_url = thumbnail
        elif audio.audio_set and (thumbnail := audio.audio_set.url):
            image_url = thumbnail
        if not image_url:
            raise get_api_exception('Could not find artwork.', 404)

        is_full_size = request.query_params.get('full_size', False)
        if is_full_size:
            return self._get_proxied_image(image_url, None)
        else:
            return self._get_proxied_image(image_url)

    @action(detail=True,
            serializer_class=AudioWaveformSerializer,
            throttle_classes=[OneThousandPerMinute])
    def waveform(self, *_, **__):
        audio = self.get_object()

        file_name = None
        try:
            file_name = download_audio(audio.url, audio.identifier)
            awf_out = generate_waveform(file_name, audio.duration)
            data = process_waveform_output(awf_out)

            obj = {'points': data}
            serializer = self.get_serializer(obj)

            return Response(status=200, data=serializer.data)
        except Exception as e:
            raise get_api_exception(getattr(e, 'message', str(e)))
        finally:
            if file_name is not None:
                cleanup(file_name)

    @action(detail=True,
            methods=['post'],
            serializer_class=AudioReportSerializer)
    def report(self, *args, **kwargs):
        return super().report(*args, **kwargs)
