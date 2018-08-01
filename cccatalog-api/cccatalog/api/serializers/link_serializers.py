from rest_framework.serializers import ModelSerializer, Serializer, URLField
from cccatalog.api.controllers.link_controller import get_next_shortened_path
from cccatalog.api.models import ShortenedLink


class ShortenedLinkResponseSerializer(Serializer):
    shortened_url = URLField(
        help_text="A shortened link on the `shares.cc` domain."
    )


class ShortenedLinkSerializer(ModelSerializer):
    """
    A single shortened URL, mapping a shortened path at shares.cc to a full
    URL elsewhere on the CC Catalog platform.
    """

    class Meta:
        model = ShortenedLink
        fields = ('shortened_path', 'full_url')

    def save(self):
        try:
            last_url = str(
                ShortenedLink
                    .objects
                    .latest(field_name='created_on')
                    .shortened_url
            )
        except ShortenedLink.DoesNotExist:
            # No URLs exist. Create the first one.
            last_url = None

        shortened_path = get_next_shortened_path(last_url)
        full_url = self.validated_data['full_url']
        shortened_link_instance = ShortenedLink(shortened_path, full_url)
        shortened_link_instance.save()
        return shortened_path
