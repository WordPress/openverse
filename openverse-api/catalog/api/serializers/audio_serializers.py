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

    source = serializers.CharField(
        label="provider",
        help_text="A comma separated list of data sources to search. Valid "
                  "inputs:"
                  " `{}`".format(list(get_sources('audio').keys())),
        required=False
    )
    categories = serializers.CharField(
        label="categories",
        help_text="A comma separated list of categories; available categories "
                  "include `music`, `podcast`, `audiobook`, and `news`.",
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
            'podcast',
            'news',
            'audiobook',
        }
        _validate_enum('category', valid_categories, value)
        return value.lower()

    @staticmethod
    def validate_duration(value):
        valid_ratios = {  # TODO: Finalise duration filters
            'short',
            'long'
        }
        _validate_enum('aspect ratio', valid_ratios, value)
        return value.lower()


class AudioSerializer(MediaSerializer):
    """ A single audio file. Used in search results."""

    set = serializers.PrimaryKeyRelatedField(
        required=False,
        help_text='Reference to set of which this track is a part.'
    )

    genre = serializers.CharField(
        required=False,
        help_text=''
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


class AudioSearchResultsSerializer(MediaSearchResultsSerializer):
    """ The full audio search response. """
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
        fields = ('reason', 'identifier', 'description')

    def create(self, validated_data):
        if validated_data['reason'] == "other" and \
            ('description' not in validated_data or len(
                validated_data['description'])) < 20:
            raise serializers.ValidationError(
                "Description must be at least be 20 characters long"
            )
        return AudioReport.objects.create(**validated_data)
