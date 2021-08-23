import logging

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from catalog.api.controllers import search_controller
from catalog.api.examples import (
    audio_search_curl,
    audio_search_200_example,
    audio_search_400_example,
    recommendations_audio_read_curl,
    recommendations_audio_read_200_example,
    recommendations_audio_read_404_example,
    audio_detail_curl,
    audio_detail_200_example,
    audio_detail_404_example,
    audio_stats_curl,
    audio_stats_200_example,
)
from catalog.api.models import Audio, AudioReport
from catalog.api.serializers.media_serializers import ProxiedImageSerializer
from catalog.api.serializers.audio_serializers import (
    AudioSearchQueryStringSerializer,
    AudioSearchResultsSerializer,
    AudioSerializer,
    ReportAudioSerializer,
    AboutAudioSerializer,
)
from catalog.api.serializers.error_serializers import (
    InputErrorSerializer,
    NotFoundErrorSerializer,
)
from catalog.api.views.media_views import (
    RESULTS,
    RESULT_COUNT,
    PAGE_COUNT,
    fields_to_md,
    SearchMedia,
    RelatedMedia,
    MediaDetail,
    MediaStats,
    ImageProxy,
)
from catalog.custom_auto_schema import CustomAutoSchema

log = logging.getLogger(__name__)


class SearchAudio(SearchMedia):
    audio_search_description = f"""
audio_search is an API endpoint to search audio files using a query string.

By using this endpoint, you can obtain search results based on specified 
query and optionally filter results by
{fields_to_md(AudioSearchQueryStringSerializer.fields_names)}.

Results are ranked in order of relevance.

{SearchMedia.search_description}"""  # noqa

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
            'search-qa-audio',
            AudioSearchQueryStringSerializer,
            AudioSerializer,
            AudioSearchResultsSerializer,
        )


class RelatedAudio(RelatedMedia):
    recommendations_audio_read_description = f"""
recommendations_audio_read is an API endpoint to get related audio files 
for a specified audio ID.

By using this endpoint, you can get the details of related audio such as 
{fields_to_md(AudioSerializer.fields_names)}. 

{RelatedMedia.recommendations_read_description}"""  # noqa

    recommendations_audio_read_response = {
        "200": openapi.Response(
            description="OK",
            examples=recommendations_audio_read_200_example,
            schema=AudioSerializer
        ),
        "404": openapi.Response(
            description="Not Found",
            examples=recommendations_audio_read_404_example,
            schema=NotFoundErrorSerializer
        )
    }

    @swagger_auto_schema(operation_id="recommendations_audio_read",
                         operation_description=recommendations_audio_read_description,  # noqa: E501
                         responses=recommendations_audio_read_response,
                         code_examples=[
                             {
                                 'lang': 'Bash',
                                 'source': recommendations_audio_read_curl
                             }
                         ],
                         manual_parameters=[
                             openapi.Parameter(
                                 'identifier', openapi.IN_PATH,
                                 "The unique identifier for the audio.",
                                 type=openapi.TYPE_STRING,
                                 required=True
                             ),
                         ])
    def get(self, request, identifier, format=None):
        related, result_count = search_controller.related_media(
            uuid=identifier,
            index='audio',
            request=request,
            filter_dead=True
        )

        context = {'request': request}
        serialized_related = AudioSerializer(
            related,
            many=True,
            context=context
        ).data
        response_data = {
            RESULT_COUNT: result_count,
            PAGE_COUNT: 0,
            RESULTS: serialized_related
        }
        serialized_response = AudioSearchResultsSerializer(data=response_data)
        return Response(status=200, data=serialized_response.initial_data)


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


class AudioDetail(MediaDetail):
    serializer_class = AudioSerializer
    queryset = Audio.objects.all()
    audio_detail_description = f"""
audio_detail is an API endpoint to get the details of a specified audio ID.

By using this endpoint, you can get audio details such as
{fields_to_md(AudioSerializer.fields_names)}. 

{MediaDetail.detail_description}"""  # noqa

    audio_detail_response = {
        "200": openapi.Response(
            description="OK",
            examples=audio_detail_200_example,
            schema=AudioSerializer),
        "404": openapi.Response(
            description="OK",
            examples=audio_detail_404_example,
            schema=NotFoundErrorSerializer
        )
    }

    @swagger_auto_schema(operation_id='audio_detail',
                         operation_description=audio_detail_description,
                         responses=audio_detail_response,
                         code_examples=[
                             {
                                 'lang': 'Bash',
                                 'source': audio_detail_curl,
                             }
                         ])
    def get(self, request, identifier, format=None):
        """ Get the details of a single audio file. """
        return self.retrieve(request, identifier)


class AudioStats(MediaStats):
    audio_stats_description = f"""
audio_stats is an API endpoint to get a list of all content providers and their
respective number of audio files in the Openverse catalog.

{MediaStats.media_stats_description}"""  # noqa

    audio_stats_response = {
        "200": openapi.Response(
            description="OK",
            examples=audio_stats_200_example,
            schema=AboutAudioSerializer(many=True)
        )
    }

    @swagger_auto_schema(operation_id='audio_stats',
                         operation_description=audio_stats_description,
                         responses=audio_stats_response,
                         code_examples=[
                             {
                                 'lang': 'Bash',
                                 'source': audio_stats_curl,
                             }
                         ])
    def get(self, request, format=None):
        return self._get(request, 'audio')


class AudioArt(ImageProxy):
    """
    Return the thumbnail of the artwork of the audio. This returns the thumbnail
    of the audio, falling back to the thumbnail of the audio set.
    """

    queryset = Audio.objects.all()

    def get(self, request, identifier, format=None):
        serialized = ProxiedImageSerializer(data=request.data)
        serialized.is_valid()
        try:
            audio = Audio.objects.get(identifier=identifier)
            image_url = audio.thumbnail
            if not image_url:
                image_url = audio.audio_set.url
        except Audio.DoesNotExist:
            return Response(status=404, data='Audio not found')
        except AttributeError:
            return Response(status=404, data='Audio set not found')
        if not image_url:
            return Response(status=404, data='Cover art URL not found')

        if serialized.data['full_size']:
            return self._get(image_url, None)
        else:
            return self._get(image_url)
