import pytest

from api.models import Audio, Image


media_type_params = pytest.mark.parametrize(
    "media_type, media_model",
    [
        ("image", Image),
        ("audio", Audio),
    ],
)


@media_type_params
@pytest.mark.parametrize(
    "fields, attribution",
    [
        (
            ["title", "creator"],
            '"A foo walks into a bar" by John Doe is licensed under CC BY 3.0.',
        ),
        (["title"], '"A foo walks into a bar" is licensed under CC BY 3.0.'),
        (["creator"], "This work by John Doe is licensed under CC BY 3.0."),
        ([], "This work is licensed under CC BY 3.0."),
    ],
)
def test_attribution_handles_missing_title_or_creator(
    media_type, media_model, fields, attribution
):
    field_values = {
        "title": "A foo walks into a bar",
        "creator": "John Doe",
    }

    obj = media_model(
        license="by",
        license_version="3.0",
    )
    for field in fields:
        setattr(obj, field, field_values[field])

    assert attribution in obj.attribution
    assert (
        "To view a copy of this license, "
        "visit https://creativecommons.org/licenses/by/3.0/."
    ) in obj.attribution


@media_type_params
def test_license_url_is_generated_if_missing(media_type, media_model):
    obj = media_model(
        license="by",
        license_version="3.0",
    )
    assert obj.license_url is not None
