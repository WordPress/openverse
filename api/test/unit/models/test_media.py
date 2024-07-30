from django.conf import settings

import pytest
from elasticsearch_dsl import Document

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


@pytest.mark.django_db
def test_deleted_media_bulk_action(media_type_config):
    """
    Test that ``AbstractDeletedMedia`` performs bulk moderation by
    deleting media items from ES.
    """

    media_ids = [media_type_config.model_factory.create().id for _ in range(2)]

    media_type_config.deleted_class._bulk_update_es(media_ids)

    for index in media_type_config.indexes:
        for media_id in media_ids:
            exists = Document.exists(id=media_id, index=index, using=settings.ES)
            assert not exists


@pytest.mark.django_db
def test_sensitive_media_bulk_action(media_type_config):
    """
    Test that ``AbstractSensitiveMedia`` performs bulk moderation by
    setting ``mature`` field in ES.
    """

    media_ids = [media_type_config.model_factory.create().id for _ in range(2)]

    for mature in [True, False]:
        media_type_config.sensitive_class._bulk_update_es(mature, media_ids)

        for index in media_type_config.indexes:
            for media_id in media_ids:
                doc = Document.get(id=media_id, index=index, using=settings.ES)
                assert doc.mature == mature
