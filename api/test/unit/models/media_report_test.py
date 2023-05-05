import uuid
from test.factory.models.audio import AudioFactory
from test.factory.models.image import ImageFactory
from typing import Literal, Union
from unittest.mock import MagicMock, call, patch

from django.core.exceptions import ObjectDoesNotExist

import pytest
from elasticsearch import TransportError

from api.models import (
    Audio,
    AudioReport,
    DeletedAudio,
    DeletedImage,
    Image,
    ImageReport,
    MatureAudio,
    MatureImage,
)
from api.models.media import (
    DEINDEXED,
    DMCA,
    MATURE,
    MATURE_FILTERED,
    OTHER,
    PENDING,
    AbstractDeletedMedia,
    AbstractMatureMedia,
)


pytestmark = pytest.mark.django_db

MediaType = Union[Literal["audio"], Literal["image"]]

reason_params = pytest.mark.parametrize("reason", [DMCA, MATURE, OTHER])


@pytest.mark.parametrize(
    "media_type, report_class", [("image", ImageReport), ("audio", AudioReport)]
)
@reason_params
def test_cannot_report_invalid_identifier(media_type, report_class, reason):
    with pytest.raises(ObjectDoesNotExist):
        report_class.objects.create(
            media_obj_id=uuid.uuid4(),
            reason=reason,
        )


@pytest.mark.parametrize(
    "media_type, report_class, mature_class, deleted_class, model_factory",
    [
        ("image", ImageReport, MatureImage, DeletedImage, ImageFactory),
        ("audio", AudioReport, MatureAudio, DeletedAudio, AudioFactory),
    ],
)
@reason_params
def test_pending_reports_have_no_subreport_models(
    media_type: MediaType,
    report_class,
    mature_class,
    deleted_class,
    reason,
    model_factory,
):
    media = model_factory.create()
    report = report_class.objects.create(media_obj=media, reason=reason)

    assert report.status == PENDING
    assert not mature_class.objects.filter(media_obj=media).exists()
    assert not deleted_class.objects.filter(media_obj=media).exists()


@pytest.mark.parametrize(
    "media_type, report_class, mature_class, model_factory",
    [
        ("image", ImageReport, MatureImage, ImageFactory),
        ("audio", AudioReport, MatureAudio, AudioFactory),
    ],
)
def test_mature_filtering_creates_mature_image_instance(
    media_type: MediaType, report_class, mature_class, model_factory
):
    media = model_factory.create()
    mock_es = MagicMock()
    with patch("django.conf.settings.ES", mock_es):
        report_class.objects.create(
            media_obj=media, reason=MATURE, status=MATURE_FILTERED
        )

    assert mature_class.objects.filter(media_obj=media).exists()
    mock_es.update.assert_has_calls(
        [
            call(
                id=media.id,
                index=media_type,
                body={"doc": {"mature": True}},
                refresh=True,
            ),
            call(
                id=media.id,
                index=f"{media_type}-filtered",
                body={"doc": {"mature": True}},
                refresh=True,
            ),
        ]
    )
    assert media.mature


@pytest.mark.parametrize(
    "media_type, report_class, mature_class, model_factory",
    [
        ("image", ImageReport, MatureImage, ImageFactory),
        ("audio", AudioReport, MatureAudio, AudioFactory),
    ],
)
def test_deleting_mature_image_instance_resets_mature_flag(
    media_type: MediaType, report_class, mature_class, model_factory
):
    media = model_factory.create()
    mock_es = MagicMock()
    with patch("django.conf.settings.ES", mock_es):
        # Mark as mature.
        report_class.objects.create(
            media_obj=media, reason=MATURE, status=MATURE_FILTERED
        )
        # Delete mature instance.
        mature_class.objects.get(media_obj=media).delete()

    mock_es.update.assert_has_calls(
        [
            call(
                id=media.pk,
                refresh=True,
                index=media_type,
                body={"doc": {"mature": True}},
            ),
            call(
                id=media.pk,
                refresh=True,
                index=f"{media_type}-filtered",
                body={"doc": {"mature": True}},
            ),
            call(
                id=media.pk,
                refresh=True,
                index=media_type,
                body={"doc": {"mature": False}},
            ),
            call(
                id=media.pk,
                refresh=True,
                index=f"{media_type}-filtered",
                body={"doc": {"mature": False}},
            ),
        ],
    )
    media.refresh_from_db()
    assert not media.mature


@pytest.mark.parametrize(
    "media_type, media_class, report_class, deleted_class, model_factory",
    [
        ("image", Image, ImageReport, DeletedImage, ImageFactory),
        ("audio", Audio, AudioReport, DeletedAudio, AudioFactory),
    ],
)
def test_deindexing_creates_deleted_image_instance(
    media_type: MediaType, media_class, report_class, deleted_class, model_factory
):
    media = model_factory.create()
    # Extracting field values because ``media`` will be deleted.
    image_id = media.id
    identifier = media.identifier

    mock_es = MagicMock()
    with patch("django.conf.settings.ES", mock_es):
        report_class.objects.create(media_obj=media, reason=DMCA, status=DEINDEXED)

    assert deleted_class.objects.filter(media_obj=media).exists()
    assert not media_class.objects.filter(identifier=identifier).exists()
    assert mock_es.delete.called_with(id=image_id)


def test_all_deleted_media_covered():
    """
    Imperfect test to ensure all subclasses are covered by the tests
    in this module. Relies on all models being present in
    ``catalog.api.models`` (i.e., exported from `__init__`).
    """
    assert set(AbstractDeletedMedia.__subclasses__()) == {DeletedAudio, DeletedImage}


def test_all_mature_media_covered():
    """
    Imperfect test to ensure all subclasses are covered by the tests
    in this module. Relies on all models being present in
    ``catalog.api.models`` (i.e., exported from `__init__`).
    """
    assert set(AbstractMatureMedia.__subclasses__()) == {MatureAudio, MatureImage}


@pytest.mark.parametrize(
    ("model_factory", "deleted_media_class", "indexes"),
    (
        (ImageFactory, DeletedImage, ("image", "image-filtered")),
        (AudioFactory, DeletedAudio, ("audio", "audio-filtered")),
    ),
)
def test_deleted_media_deletes_from_all_indexes(
    settings, model_factory, deleted_media_class, indexes
):
    settings.ES = MagicMock()
    media = model_factory.create()
    # Need to retrieve this here because the creation of the
    # deleted media class below will delete this object, rendering
    # the pk empty by the time we assert the calls
    media_id = media.pk

    instance = deleted_media_class(
        media_obj=media,
    )

    instance.save()

    settings.ES.delete.assert_has_calls(
        (call(index=index, id=media_id, refresh=True) for index in indexes),
        # The order does not matter
        any_order=True,
    )


@pytest.mark.parametrize(
    ("model_factory", "deleted_media_class", "indexes"),
    (
        (ImageFactory, DeletedImage, ("image", "image-filtered")),
        (AudioFactory, DeletedAudio, ("audio", "audio-filtered")),
    ),
)
def test_deleted_media_ignores_elasticsearch_404_errors(
    settings, model_factory, deleted_media_class, indexes
):
    settings.ES = MagicMock()
    error = TransportError(404, "Whoops, no document!", {})
    settings.ES.delete.side_effect = [None, error]
    media = model_factory.create()
    # Need to retrieve this here because the creation of the
    # deleted media class below will delete this object, rendering
    # the pk empty by the time we assert the calls
    media_id = media.pk

    instance = deleted_media_class(
        media_obj=media,
    )

    instance.save()

    settings.ES.delete.assert_has_calls(
        (call(index=index, id=media_id, refresh=True) for index in indexes),
        # The order does not matter
        any_order=True,
    )


@pytest.mark.parametrize(
    ("model_factory", "deleted_media_class", "indexes"),
    (
        (ImageFactory, DeletedImage, ("image", "image-filtered")),
        (AudioFactory, DeletedAudio, ("audio", "audio-filtered")),
    ),
)
def test_deleted_media_raises_elasticsearch_400_errors(
    settings, model_factory, deleted_media_class, indexes
):
    settings.ES = MagicMock()
    error = TransportError(400, "Terrible request, no thanks", {})
    settings.ES.delete.side_effect = [None, error]
    media = model_factory.create()
    # Need to retrieve this here because the creation of the
    # deleted media class below will delete this object, rendering
    # the pk empty by the time we assert the calls

    instance = deleted_media_class(
        media_obj=media,
    )

    with pytest.raises(TransportError):
        instance.save()

    settings.ES.delete.assert_has_calls(
        (call(index=index, id=media.pk, refresh=True) for index in indexes),
        # The order does not matter
        any_order=True,
    )


@pytest.mark.parametrize(
    ("model_factory", "mature_media_class", "indexes"),
    (
        (ImageFactory, MatureImage, ("image", "image-filtered")),
        (AudioFactory, MatureAudio, ("audio", "audio-filtered")),
    ),
)
def test_mature_media_updates_all_indexes(
    settings, model_factory, mature_media_class, indexes
):
    settings.ES = MagicMock()
    media = model_factory.create()

    instance = mature_media_class(
        media_obj=media,
    )

    instance.save()

    settings.ES.update.assert_has_calls(
        (
            call(
                index=index,
                id=media.id,
                body={"doc": {"mature": True}},
                refresh=True,
            )
            for index in indexes
        ),
        # The order does not matter
        any_order=True,
    )


@pytest.mark.parametrize(
    ("model_factory", "mature_media_class", "indexes"),
    (
        (ImageFactory, MatureImage, ("image", "image-filtered")),
        (AudioFactory, MatureAudio, ("audio", "audio-filtered")),
    ),
)
def test_mature_media_ignores_elasticsearch_404_errors(
    settings, model_factory, mature_media_class, indexes
):
    settings.ES = MagicMock()
    error = TransportError(404, "Whoops, no document!", {})
    settings.ES.update.side_effect = [None, error]
    media = model_factory.create()

    instance = mature_media_class(
        media_obj=media,
    )

    instance.save()

    settings.ES.update.assert_has_calls(
        (
            call(
                index=index,
                id=media.id,
                body={"doc": {"mature": True}},
                refresh=True,
            )
            for index in indexes
        ),
        # The order does not matter
        any_order=True,
    )


@pytest.mark.parametrize(
    ("model_factory", "mature_media_class", "indexes"),
    (
        (ImageFactory, MatureImage, ("image", "image-filtered")),
        (AudioFactory, MatureAudio, ("audio", "audio-filtered")),
    ),
)
def test_mature_media_reraises_elasticsearch_400_errors(
    settings, model_factory, mature_media_class, indexes
):
    settings.ES = MagicMock()
    error = TransportError(400, "Terrible request, no thanks.", {})
    settings.ES.update.side_effect = [None, error]
    media = model_factory.create()

    instance = mature_media_class(
        media_obj=media,
    )

    with pytest.raises(TransportError):
        instance.save()

    settings.ES.update.assert_has_calls(
        (
            call(
                index=index,
                id=media.id,
                body={"doc": {"mature": True}},
                refresh=True,
            )
            for index in indexes
        ),
        # The order does not matter
        any_order=True,
    )
