from rest_framework import serializers

from elasticsearch_dsl.response import Hit

from api.constants.field_order import field_position_map
from api.constants.field_values import AUDIO_CATEGORIES, LENGTHS
from api.models import Audio, AudioReport, AudioSet
from api.serializers.fields import EnumCharField, SchemableHyperlinkedIdentityField
from api.serializers.media_serializers import (
    MediaReportRequestSerializer,
    MediaSearchRequestSerializer,
    MediaSerializer,
    get_hyperlinks_serializer,
)


#######################
# Request serializers #
#######################


class AudioSearchRequestSerializer(MediaSearchRequestSerializer):
    """Parse and validate search query string parameters."""

    field_names = [
        *MediaSearchRequestSerializer.field_names,
        "category",
        "length",
    ]
    """
    Keep the fields names in sync with the actual fields below as this list is
    used to generate Swagger documentation.
    """

    category = EnumCharField(
        plural="categories",
        enum_class=AUDIO_CATEGORIES,
        required=False,
    )
    length = EnumCharField(
        plural="lengths",
        enum_class=LENGTHS,
        required=False,
    )
    peaks = serializers.BooleanField(
        help_text="Whether to include the waveform peaks or not",
        required=False,
        default=False,
    )


class AudioReportRequestSerializer(MediaReportRequestSerializer):
    identifier = serializers.SlugRelatedField(
        slug_field="identifier",
        queryset=Audio.objects.all(),
        source="media_obj",
    )

    class Meta(MediaReportRequestSerializer.Meta):
        model = AudioReport


########################
# Response serializers #
########################


class AudioSetSerializer(serializers.ModelSerializer):
    """An audio set, rendered as a part of the ``AudioSerializer`` output."""

    class Meta:
        model = AudioSet
        fields = [
            "title",
            "foreign_landing_url",
            "creator",
            "creator_url",
            "url",
            "filesize",
            "filetype",
        ]


AudioHyperlinksSerializer = get_hyperlinks_serializer("audio")


class AudioAltFileSerializer(serializers.Serializer):
    """
    A set of alternative files for a single audio object,
    rendered as a part of the ``AudioSerializer`` output.
    """

    class Meta:
        fields = [
            "url",
            "bit_rate",
            "filesize",
            "filetype",
            "sample_rate",
        ]

    url = serializers.URLField(
        help_text="URL of the alternative file.",
    )
    bit_rate = serializers.IntegerField(
        help_text="Bit rate of the alternative file.",
        min_value=0,
        required=False,
    )
    filesize = serializers.IntegerField(
        help_text="Size of the alternative file in bytes.",
        min_value=0,
        required=False,
    )
    filetype = serializers.CharField(
        help_text="File type of the alternative file.",
    )
    sample_rate = serializers.IntegerField(
        help_text="Sample rate of the alternative file.",
        required=False,
        min_value=0,
    )


class AudioSerializer(AudioHyperlinksSerializer, MediaSerializer):
    """A single audio file. Used in search results."""

    class Meta:
        model = Audio
        fields = sorted(  # keep this list ordered logically
            [
                *MediaSerializer.Meta.fields,
                *AudioHyperlinksSerializer.field_names,
                "genres",
                "alt_files",
                "audio_set",
                "duration",
                "bit_rate",
                "sample_rate",
                "waveform",  # hyperlink to the endpoint that generates the waveform
                "peaks",  # waveform peaks, if they have already been generated
            ],
            key=lambda val: field_position_map.get(val, 999),
        )
        """
        Keep the fields names in sync with the actual fields below as this list is
        used to generate Swagger documentation.
        """

    audio_set = AudioSetSerializer(
        allow_null=True,
        help_text="Reference to set of which this track is a part.",
        read_only=True,
    )

    alt_files = AudioAltFileSerializer(
        allow_null=True,
        help_text="JSON describing alternative files for this audio.",
        read_only=True,
        many=True,
    )

    waveform = SchemableHyperlinkedIdentityField(
        read_only=True,
        view_name="audio-waveform",
        lookup_field="identifier",
        help_text="A direct link to the waveform peaks.",
    )

    # Add-on data
    peaks = serializers.SerializerMethodField(
        help_text="The list of peaks used to generate the waveform for the audio."
    )

    def __init__(self, *args, **kwargs):
        # Includes the peaks only if requested via the `peaks` query param
        if not kwargs.get("context", {}).get("validated_data", {}).get("peaks"):
            del self.fields["peaks"]
        super().__init__(*args, **kwargs)

    def get_peaks(self, obj) -> list[int]:
        if isinstance(obj, Hit):
            obj = Audio.objects.get(identifier=obj.identifier)
        return obj.get_waveform()

    def to_representation(self, instance):
        # Get the original representation
        output = super().to_representation(instance)
        audio = instance

        if isinstance(instance, Hit):
            # TODO: Remove this DB query when updating ES index
            audio = Audio.objects.get(identifier=instance.identifier)

        if isinstance(audio, Audio) and not audio.thumbnail:
            output["thumbnail"] = None

        return output


##########################
# Additional serializers #
##########################


class AudioWaveformSerializer(serializers.Serializer):
    len = serializers.SerializerMethodField()
    points = serializers.ListField(
        child=serializers.FloatField(min_value=0, max_value=1)
    )

    @staticmethod
    def get_len(obj) -> int:
        return len(obj.get("points", []))
