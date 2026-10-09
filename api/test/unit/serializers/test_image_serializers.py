from api.models import Image
from api.serializers.image_serializers import OembedSerializer


# Entity-encoded markup must be stripped the same way as literal markup.
ENCODED_MARKUP = "&lt;iframe&gt;X&lt;/iframe&gt;"


def _oembed_output(**fields):
    image = Image(
        license="by",
        license_version="4.0",
        width=640,
        height=480,
        **fields,
    )
    return OembedSerializer(image, context={}).data


def test_oembed_serializer_strips_markup_from_title_and_author_name():
    output = _oembed_output(title=ENCODED_MARKUP, creator=ENCODED_MARKUP)

    assert output["title"] == "X"
    assert output["author_name"] == "X"


def test_oembed_serializer_drops_author_url_with_unsafe_scheme():
    output = _oembed_output(creator="Jane Doe", creator_url="javascript:void(0)")

    assert output["author_url"] is None
