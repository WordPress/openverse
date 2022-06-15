from rest_framework import serializers

from elasticsearch_dsl.response import Hit

from catalog.api.constants.field_order import field_position_map
from catalog.api.constants.field_values import AUDIO_CATEGORIES, LENGTHS
from catalog.api.docs.media_docs import fields_to_md
from catalog.api.models import Audio, AudioReport, AudioSet
from catalog.api.serializers.fields import (
    EnumCharField,
    SchemableHyperlinkedIdentityField,
)
from catalog.api.serializers.media_serializers import (
    MediaReportRequestSerializer,
    MediaSearchRequestSerializer,
    MediaSearchSerializer,
    MediaSerializer,
    get_hyperlinks_serializer,
    get_search_request_source_serializer,
)


#######################
# Request serializers #
#######################


AudioSearchRequestSourceSerializer = get_search_request_source_serializer("audio")


class AudioSearchRequestSerializer(
    AudioSearchRequestSourceSerializer,
    MediaSearchRequestSerializer,
):
    """Parse and validate search query string parameters."""

    fields_names = [
        *MediaSearchRequestSerializer.fields_names,
        *AudioSearchRequestSourceSerializer.field_names,
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


class AudioReportRequestSerializer(MediaReportRequestSerializer):
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

    @staticmethod
    def get_peaks(obj) -> list[int]:
        if isinstance(obj, Hit):
            obj = Audio.objects.get(identifier=obj.identifier)
        return obj.get_waveform()

    def to_representation(self, instance):
        # Get the original representation
        output = super().to_representation(instance)

        if isinstance(instance, Hit):
            # TODO: Remove when updating ES indexes
            audio = Audio.objects.get(identifier=instance.identifier)
            if not audio.thumbnail:
                output["thumbnail"] = None

        return output


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
            f"{fields_to_md(AudioSerializer.Meta.fields)}."
        ),
    )


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
