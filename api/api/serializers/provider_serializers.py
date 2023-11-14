from rest_framework import serializers

from drf_spectacular.utils import extend_schema_serializer

from api.models import ContentProvider


@extend_schema_serializer(
    deprecate_fields=["logo_url"],
)
class ProviderSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(
        source="provider_identifier",
        help_text="The source of the media, e.g. flickr",
    )
    display_name = serializers.CharField(
        source="provider_name",
        help_text="The name of content provider, e.g. Flickr",
    )
    source_url = serializers.URLField(
        source="domain_name",
        help_text="The URL of the source, e.g. https://www.flickr.com",
    )
    logo_url = serializers.SerializerMethodField(
        help_text="The URL to a logo for the source.",
    )
    media_count = serializers.SerializerMethodField(
        help_text="The number of media items indexed from the source.",
    )

    @staticmethod
    def get_logo_url(*_) -> str | None:
        return None

    class Meta:
        model = ContentProvider
        fields = [
            "source_name",
            "display_name",
            "source_url",
            "logo_url",
            "media_count",
        ]

    def get_media_count(self, obj) -> int:
        source_counts = self.context.get("source_counts")
        return source_counts.get(obj.provider_identifier)
