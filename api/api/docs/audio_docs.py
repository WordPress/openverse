from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    NotFound,
    ValidationError,
)

from drf_spectacular.utils import OpenApiResponse, extend_schema

from api.constants.parameters import COLLECTION, TAG
from api.docs.base_docs import (
    NON_FILTER_FIELDS,
    SEARCH_DESCRIPTION,
    custom_extend_schema,
    fields_to_md,
)
from api.examples import (
    audio_complain_201_example,
    audio_complain_curl,
    audio_detail_200_example,
    audio_detail_404_example,
    audio_detail_curl,
    audio_related_200_example,
    audio_related_404_example,
    audio_related_curl,
    audio_search_200_example,
    audio_search_400_example,
    audio_search_list_curl,
    audio_stats_200_example,
    audio_stats_curl,
    audio_waveform_200_example,
    audio_waveform_404_example,
    audio_waveform_curl,
)
from api.serializers.audio_serializers import (
    AudioReportRequestSerializer,
    AudioSearchRequestSerializer,
    AudioSerializer,
    AudioWaveformSerializer,
)
from api.serializers.media_serializers import MediaThumbnailRequestSerializer
from api.serializers.provider_serializers import ProviderSerializer


serializer = AudioSearchRequestSerializer(context={"media_type": "audio"})
audio_filter_fields = fields_to_md(
    [f for f in serializer.field_names if f not in NON_FILTER_FIELDS]
)

audio_search_description = SEARCH_DESCRIPTION.format(
    filter_fields=audio_filter_fields,
    media_type="audio files",
    collection_param=COLLECTION,
    tag_param=TAG,
)

search = custom_extend_schema(
    desc=audio_search_description,
    params=serializer,
    res={
        200: (AudioSerializer, audio_search_200_example),
        400: (ValidationError, audio_search_400_example),
        401: (NotAuthenticated, None),
    },
    eg=[audio_search_list_curl],
    external_docs={
        "description": "Openverse Syntax Guide",
        "url": "https://openverse.org/search-help",
    },
)

stats = custom_extend_schema(
    desc=f"""
        Get a list of all content providers and their respective number of
        audio files in the Openverse catalog.

        By using this endpoint, you can obtain info about content providers such
        as {fields_to_md(ProviderSerializer.Meta.fields)}.""",
    res={
        200: (ProviderSerializer(many=True), audio_stats_200_example),
        401: (AuthenticationFailed, None),
    },
    eg=[audio_stats_curl],
)

detail = custom_extend_schema(
    desc=f"""
        Get the details of a specified audio track.

        By using this endpoint, you can obtain info about audio files such as
        {fields_to_md(AudioSerializer.Meta.fields)}""",
    res={
        200: (AudioSerializer, audio_detail_200_example),
        401: (AuthenticationFailed, None),
        404: (NotFound, audio_detail_404_example),
    },
    eg=[audio_detail_curl],
)

related = custom_extend_schema(
    desc=f"""
        Get related audio files for a specified audio track.

        By using this endpoint, you can get the details of related audio such as
        {fields_to_md(AudioSerializer.Meta.fields)}.""",
    res={
        200: (AudioSerializer(many=True), audio_related_200_example),
        401: (AuthenticationFailed, None),
        404: (NotFound, audio_related_404_example),
    },
    eg=[audio_related_curl],
)

report = custom_extend_schema(
    res={
        201: (AudioReportRequestSerializer, audio_complain_201_example),
        400: (ValidationError, None),
        401: (AuthenticationFailed, None),
    },
    eg=[audio_complain_curl],
)

thumbnail = extend_schema(
    parameters=[MediaThumbnailRequestSerializer],
    responses={
        200: OpenApiResponse(description="Thumbnail image"),
        401: AuthenticationFailed,
    },
)

waveform = custom_extend_schema(
    res={
        200: (AudioWaveformSerializer, audio_waveform_200_example),
        401: (AuthenticationFailed, None),
        404: (NotFound, audio_waveform_404_example),
    },
    eg=[audio_waveform_curl],
)
