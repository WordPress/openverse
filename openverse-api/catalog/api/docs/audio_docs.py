from drf_yasg import openapi

from catalog.api.docs.media_docs import (
    fields_to_md,
    MediaSearch,
    MediaStats,
    MediaDetail,
    MediaRelated,
    MediaComplain,
)
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
    report_audio_curl,
    audio_report_create_201_example,
)
from catalog.api.serializers.audio_serializers import (
    AudioSearchQueryStringSerializer,
    AudioSearchResultsSerializer,
    AudioSerializer,
    ReportAudioSerializer,
)
from catalog.api.serializers.error_serializers import (
    InputErrorSerializer,
    NotFoundErrorSerializer,
)
from catalog.api.serializers.provider_serializers import ProviderSerializer


class AudioSearch(MediaSearch):
    desc = f"""
audio_search is an API endpoint to search audio files using a query string.

By using this endpoint, you can obtain search results based on specified 
query and optionally filter results by
{fields_to_md(AudioSearchQueryStringSerializer.fields_names)}.

{MediaSearch.desc}"""  # noqa

    responses = {
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

    code_examples = [
        {
            'lang': 'Bash',
            'source': audio_search_curl,
        },
    ]

    swagger_setup = {
        'operation_id': 'audio_search',
        'operation_description': desc,
        'query_serializer': AudioSearchQueryStringSerializer,
        'responses': responses,
        'code_examples': code_examples
    }


class AudioStats(MediaStats):
    desc = f"""
audio_stats is an API endpoint to get a list of all content providers and their
respective number of audio files in the Openverse catalog.

{MediaStats.desc}"""  # noqa

    responses = {
        "200": openapi.Response(
            description="OK",
            examples=audio_stats_200_example,
            schema=ProviderSerializer(many=True)
        )
    }

    code_examples = [
        {
            'lang': 'Bash',
            'source': audio_stats_curl,
        },
    ]

    swagger_setup = {
        'operation_id': 'audio_stats',
        'operation_description': desc,
        'responses': responses,
        'code_examples': code_examples,
    }


class AudioDetail(MediaDetail):
    desc = f"""
audio_detail is an API endpoint to get the details of a specified audio ID.

By using this endpoint, you can get audio details such as
{fields_to_md(AudioSerializer.fields_names)}. 

{MediaDetail.desc}"""  # noqa

    responses = {
        "200": openapi.Response(
            description="OK",
            examples=audio_detail_200_example,
            schema=AudioSerializer
        ),
        "404": openapi.Response(
            description="OK",
            examples=audio_detail_404_example,
            schema=NotFoundErrorSerializer
        )
    }

    code_examples = [
        {
            'lang': 'Bash',
            'source': audio_detail_curl,
        },
    ]

    swagger_setup = {
        'operation_id': 'audio_detail',
        'operation_description': desc,
        'responses': responses,
        'code_examples': code_examples,
    }


class AudioRelated(MediaRelated):
    desc = f"""
recommendations_audio_read is an API endpoint to get related audio files 
for a specified audio ID.

By using this endpoint, you can get the details of related audio such as 
{fields_to_md(AudioSerializer.fields_names)}. 

{MediaRelated.desc}"""  # noqa

    responses = {
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

    code_examples = [
        {
            'lang': 'Bash',
            'source': recommendations_audio_read_curl,
        },
    ]

    swagger_setup = {
        'operation_id': 'audio_related',
        'operation_description': desc,
        'responses': responses,
        'code_examples': code_examples
    }


class AudioComplain(MediaComplain):
    desc = f"""
audio_report_create is an API endpoint to report an issue about a specified
audio ID to Openverse.

By using this endpoint, you can report an audio file if it infringes copyright,
contains mature or sensitive content and others.

{MediaComplain.desc}"""  # noqa

    responses = {
        "201": openapi.Response(
            description="OK",
            examples=audio_report_create_201_example,
            schema=ReportAudioSerializer
        )
    }

    code_examples = [
        {
            'lang': 'Bash',
            'source': report_audio_curl,
        }
    ]

    swagger_setup = {
        'operation_id': 'audio_report',
        'operation_description': desc,
        'query_serializer': ReportAudioSerializer,
        'responses': responses,
        'code_examples': code_examples,
    }
