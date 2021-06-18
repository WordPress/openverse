import logging

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView

from catalog.api.examples import (
    audio_search_curl,
    audio_search_200_example,
    audio_search_400_example,
)
from catalog.api.models import AudioReport
from catalog.api.serializers.audio_serializers import (
    AudioSearchQueryStringSerializer,
    AudioSearchResultsSerializer,
    AudioSerializer,
    ReportAudioSerializer,
)
from catalog.api.serializers.error_serializers import InputErrorSerializer
from catalog.api.views.media_views import (
    SearchMedia,
)
from catalog.custom_auto_schema import CustomAutoSchema

log = logging.getLogger(__name__)


class SearchAudio(SearchMedia):
    swagger_schema = CustomAutoSchema
    audio_search_description = """
audio_search is an API endpoint to search audio files using a query 
string.

By using this endpoint, you can obtain search results based on specified 
query and optionally filter results by `license`, `license_type`, 
`page`, `page_size`, `creator`, `tags`, `title`, `filter_dead`, 
`source`, `extension`, `categories`, `aspect_ratio`, `size`, `mature`, 
and `qa`. Results are ranked in order of relevance.
""" \
                               f'{SearchMedia.search_description}'  # noqa

    audio_search_response = {
        "200": openapi.Response(
            description="OK",
            examples=audio_search_200_example,
            schema=AudioSearchResultsSerializer(many=True)
        ),
        "400": openapi.Response(
            description="Bad Request",
            examples=audio_search_400_example,
            schema=InputErrorSerializer
        ),
    }

    @swagger_auto_schema(operation_id='audio_search',
                         operation_description=audio_search_description,
                         query_serializer=AudioSearchQueryStringSerializer,
                         responses=audio_search_response,
                         code_examples=[
                             {
                                 'lang': 'Bash',
                                 'source': audio_search_curl
                             }
                         ])
    def get(self, request, fmt=None):
        # Parse and validate query parameters
        return self._get(
            request,
            'audio',
            'search-audio-qa',
            AudioSearchQueryStringSerializer,
            AudioSerializer,
            AudioSearchResultsSerializer,
        )


class ReportAudioView(CreateAPIView):
    """
    audio_report_create

    audio_report_create is an API endpoint to report an issue about a 
    specified audio ID to Creative Commons.

    By using this endpoint, you can report an audio file if it infringes 
    copyright, contains mature or sensitive content and others.

    You can refer to Bash's Request Samples for example on how to use
    this endpoint.
    """  # noqa
    swagger_schema = CustomAutoSchema
    queryset = AudioReport.objects.all()
    serializer_class = ReportAudioSerializer
