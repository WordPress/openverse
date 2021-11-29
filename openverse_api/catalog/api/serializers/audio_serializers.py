from catalog.api.controllers.search_controller import get_sources
from catalog.api.docs.media_docs import fields_to_md
from catalog.api.models import AudioReport
from catalog.api.serializers.media_serializers import (
    MediaSearchRequestSerializer,
    MediaSearchSerializer,
    MediaSerializer,
    _validate_enum,
)
from rest_framework import serializers


class AudioSetSerializer(serializers.Serializer):
    """An audio set, rendered as a part of the ``AudioSerializer`` output."""

    title = serializers.CharField(help_text="The name of the media.", required=False)
    foreign_landing_url = serializers.URLField(
        required=False, help_text="A foreign landing link for the image."
    )

    creator = serializers.CharField(
        help_text="The name of the media creator.", required=False, allow_blank=True
    )
    creator_url = serializers.URLField(
        required=False, help_text="A direct link to the media creator."
    )

    url = serializers.URLField(help_text="The actual URL to the media file.")
    filesize = serializers.CharField(
        required=False, help_text="Number in bytes, e.g. 1024."
    )
    filetype = serializers.CharField(
        required=False,
        help_text="The type of the file, related to the file extension.",
    )


class AudioSearchRequestSerializer(MediaSearchRequestSerializer):
    """Parse and validate search query string parameters."""

    fields_names = [
        *MediaSearchRequestSerializer.fields_names,
        "source",
        "categories",
        "duration",
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
        required=False,
    )
    categories = serializers.CharField(
        label="categories",
        help_text="A comma separated list of categories; available categories "
        "include `music`, `sound_effect`, `podcast`, `audiobook`, "
        "and `news`.",
        required=False,
    )
    duration = serializers.CharField(
        label="duration",
        help_text="A comma separated list of audio lengths; available lengths "
        "include `short`, and `long`.",
        required=False,
    )

    @staticmethod
    def validate_source(input_sources):
        allowed_sources = list(get_sources("audio").keys())
        input_sources = input_sources.split(",")
        input_sources = [x for x in input_sources if x in allowed_sources]
        input_sources = ",".join(input_sources)
        return input_sources.lower()

    @staticmethod
    def validate_categories(value):
        valid_categories = {
            "music",
            "sound_effect",
            "podcast",
            "news",
            "audiobook",
        }
        _validate_enum("category", valid_categories, value)
        return value.lower()

    @staticmethod
    def validate_duration(value):
        valid_durations = {"short", "long"}  # TODO: Finalise duration filters
        _validate_enum("duration", valid_durations, value)
        return value.lower()


class AudioSerializer(MediaSerializer):
    """A single audio file. Used in search results."""

    fields_names = [
        *MediaSerializer.fields_names,
        "audio_set",
        "genre",
        "duration",
        "bit_rate",
        "sample_rate",
        "alt_files",
        "detail_url",
        "related_url",
        "category",
    ]
    """
    Keep the fields names in sync with the actual fields below as this list is
    used to generate Swagger documentation.
    """

    audio_set = AudioSetSerializer(
        required=False,
        help_text="Reference to set of which this track is a part.",
        read_only=True,
    )

    genres = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="An array of audio genres such as "
        "`rock`, `electronic` for `music` category, or "
        "`politics`, `sport`, `education` for `podcast` category",
    )

    duration = serializers.IntegerField(
        required=False, help_text="The time length of the audio file in milliseconds."
    )
    bit_rate = serializers.IntegerField(
        required=False, help_text="Number in bits per second, eg. 128000."
    )
    sample_rate = serializers.IntegerField(
        required=False, help_text="Number in hertz, eg. 44100."
    )

    alt_files = serializers.JSONField(
        required=False, help_text="JSON describing alternative files for this audio."
    )

    # Hyperlinks
    thumbnail = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="audio-thumb",
        lookup_field="identifier",
        help_text="A direct link to the miniature artwork.",
    )
    waveform = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="audio-waveform",
        lookup_field="identifier",
        help_text="A direct link to the waveform peaks.",
    )
    detail_url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="audio-detail",
        lookup_field="identifier",
        help_text="A direct link to the detail view of this audio file.",
    )
    related_url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name="audio-related",
        lookup_field="identifier",
        help_text="A link to an endpoint that provides similar audio files.",
    )


class AudioSearchSerializer(MediaSearchSerializer):
    """
    The full audio search response.
    This serializer is purely representational and not actually used to
    serialize the response.
    """

    results = AudioSerializer(
        many=True,
        help_text=(
            "An array of audios and their details such as "
            f"{fields_to_md(AudioSerializer.fields_names)}."
        ),
    )


class AudioReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioReport
        fields = ("identifier", "reason", "description")
        read_only_fields = ("identifier",)

    def create(self, validated_data):
        if (
            validated_data["reason"] == "other"
            and (
                "description" not in validated_data
                or len(validated_data["description"])
            )
            < 20
        ):
            raise serializers.ValidationError(
                "Description must be at least be 20 characters long"
            )
        return AudioReport.objects.create(**validated_data)


class AudioWaveformSerializer(serializers.Serializer):
    len = serializers.SerializerMethodField()
    points = serializers.ListField(serializers.FloatField(min_value=0, max_value=1))

    @staticmethod
    def get_len(obj) -> int:
        return len(obj.get("points", []))
