from django.urls import reverse
from rest_framework import serializers

from catalog.api.controllers.search_controller import get_sources
from catalog.api.models import AudioReport
from catalog.api.serializers.media_serializers import (
    _validate_enum,
    MediaSearchQueryStringSerializer,
    MediaSearchResultsSerializer,
    MediaSerializer,
)


class AudioSearchQueryStringSerializer(MediaSearchQueryStringSerializer):
    """ Parse and validate search query string parameters. """

    fields_names = [
        *MediaSearchQueryStringSerializer.fields_names,
        'source',
        'categories',
        'duration',
    ]
    """
    Keep the fields names in sync with the actual fields below as this list is
    used to generate Swagger documentation.
    """

    source = serializers.CharField(
        label="provider",
        help_text="A comma separated list of data sources to search. Valid "
                  "inputs: "
                  f"`{list(get_sources('audio').keys())}`",
        required=False
    )
    categories = serializers.CharField(
        label="categories",
        help_text="A comma separated list of categories; available categories "
                  "include `music`, `sound_effect`, `podcast`, `audiobook`, "
                  "and `news`.",
        required=False
    )
    duration = serializers.CharField(
        label='duration',
        help_text="A comma separated list of audio lengths; available lengths "
                  "include `short`, and `long`.",
        required=False
    )

    @staticmethod
    def validate_source(input_sources):
        allowed_sources = list(get_sources('audio').keys())
        input_sources = input_sources.split(',')
        input_sources = [x for x in input_sources if x in allowed_sources]
        input_sources = ','.join(input_sources)
        return input_sources.lower()

    @staticmethod
    def validate_categories(value):
        valid_categories = {
            'music',
            'sound_effect',
            'podcast',
            'news',
            'audiobook',
        }
        _validate_enum('category', valid_categories, value)
        return value.lower()

    @staticmethod
    def validate_duration(value):
        valid_durations = {  # TODO: Finalise duration filters
            'short',
            'long'
        }
        _validate_enum('duration', valid_durations, value)
        return value.lower()


class AudioSerializer(MediaSerializer):
    """ A single audio file. Used in search results."""

    fields_names = [
        *MediaSerializer.fields_names,
        'audio_set',
        'genre',
        'duration',
        'bit_rate',
        'sample_rate',
        'alt_files',
        'detail_url',
        'related_url',
    ]
    """
    Keep the fields names in sync with the actual fields below as this list is
    used to generate Swagger documentation.
    """

    thumbnail = serializers.SerializerMethodField(
        help_text="A direct link to the miniature artwork."
    )
    waveform = serializers.SerializerMethodField(
        help_text='A direct link to the waveform peaks.'
    )
    audio_set = serializers.PrimaryKeyRelatedField(
        required=False,
        help_text='Reference to set of which this track is a part.',
        read_only=True
    )

    genres = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='An array of audio genres such as '
                  '`rock`, `electronic` for `music` category, or '
                  '`politics`, `sport`, `education` for `podcast` category'
    )

    duration = serializers.IntegerField(
        required=False,
        help_text='The time length of the audio file in milliseconds.'
    )
    bit_rate = serializers.IntegerField(
        required=False,
        help_text='Number in bits per second, eg. 128000.'
    )
    sample_rate = serializers.IntegerField(
        required=False,
        help_text='Number in hertz, eg. 44100.'
    )

    alt_files = serializers.JSONField(
        required=False,
        help_text='JSON describing alternative files for this audio.'
    )

    # Hyperlinks
    detail_url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='audio-detail',
        lookup_field='identifier',
        help_text="A direct link to the detail view of this audio file."
    )
    related_url = serializers.HyperlinkedIdentityField(
        view_name='audio-related',
        lookup_field='identifier',
        read_only=True,
        help_text="A link to an endpoint that provides similar audio files."
    )

    def get_thumbnail(self, obj):
        request = self.context['request']
        host = request.get_host()
        path = reverse('audio-thumb', kwargs={'identifier': obj.identifier})
        return f'https://{host}{path}'

    def get_waveform(self, obj):
        request = self.context['request']
        host = request.get_host()
        path = reverse('audio-waveform', kwargs={'identifier': obj.identifier})
        return f'https://{host}{path}'


class AudioSearchResultsSerializer(MediaSearchResultsSerializer):
    """
    The full audio search response.
    This serializer is purely representational and not actually used to
    serialize the response.
    """
    results = AudioSerializer(
        many=True,
        help_text="An array of audios and their details such as `title`, `id`, "
                  "`creator`, `creator_url`, `url`, `provider`, `source`, "
                  "`license`, `license_version`, `license_url`, "
                  "`foreign_landing_url`, `detail_url`, `related_url`, "
                  "and `fields_matched `."
    )


class ReportAudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioReport
        fields = ('id', 'identifier', 'reason', 'description')
        read_only_fields = ('id', 'identifier',)

    def create(self, validated_data):
        if validated_data['reason'] == "other" and \
            ('description' not in validated_data or len(
                validated_data['description'])) < 20:
            raise serializers.ValidationError(
                "Description must be at least be 20 characters long"
            )
        return AudioReport.objects.create(**validated_data)


class AudioWaveformSerializer(serializers.Serializer):
    len = serializers.SerializerMethodField()
    points = serializers.ListField(
        serializers.FloatField(min_value=0, max_value=1)
    )

    @staticmethod
    def get_len(obj):
        return len(obj.get('points', []))
