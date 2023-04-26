from test.factory.models.audio import AudioFactory
from test.factory.models.image import ImageFactory
from unittest import mock

import pytest
from elasticsearch import TransportError

from catalog.api.models import DeletedAudio, DeletedImage, MatureAudio, MatureImage
from catalog.api.models.media import AbstractDeletedMedia, AbstractMatureMedia


pytestmark = pytest.mark.django_db


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
    ("media_factory", "deleted_media_class", "indexes"),
    (
        (ImageFactory, DeletedImage, ("image", "image-filtered")),
        (AudioFactory, DeletedAudio, ("audio", "audio-filtered")),
    ),
)
def test_deleted_media_deletes_from_all_indexes(
    settings, media_factory, deleted_media_class, indexes
):
    settings.ES = mock.MagicMock()
    media = media_factory.create()

    instance = deleted_media_class(
        media_obj=media,
    )

    instance.save()

    settings.ES.delete.assert_has_calls(
        (
            mock.call(index=index, id=media.identifier, refresh=True)
            for index in indexes
        ),
        # The order does not matter
        any_order=True,
    )


@pytest.mark.parametrize(
    ("media_factory", "deleted_media_class", "indexes"),
    (
        (ImageFactory, DeletedImage, ("image", "image-filtered")),
        (AudioFactory, DeletedAudio, ("audio", "audio-filtered")),
    ),
)
def test_deleted_media_ignores_elasticsearch_404_errors(
    settings, media_factory, deleted_media_class, indexes
):
    settings.ES = mock.MagicMock()
    error = TransportError(404, "Whoops, no document!", {})
    settings.ES.delete.side_effect = [None, error]
    media = media_factory.create()

    instance = deleted_media_class(
        media_obj=media,
    )

    instance.save()

    settings.ES.delete.assert_has_calls(
        (
            mock.call(index=index, id=media.identifier, refresh=True)
            for index in indexes
        ),
        # The order does not matter
        any_order=True,
    )


@pytest.mark.parametrize(
    ("media_factory", "deleted_media_class", "indexes"),
    (
        (ImageFactory, DeletedImage, ("image", "image-filtered")),
        (AudioFactory, DeletedAudio, ("audio", "audio-filtered")),
    ),
)
def test_deleted_media_raises_elasticsearch_400_errors(
    settings, media_factory, deleted_media_class, indexes
):
    settings.ES = mock.MagicMock()
    error = TransportError(400, "Terrible request, no thanks", {})
    settings.ES.delete.side_effect = [None, error]
    media = media_factory.create()

    instance = deleted_media_class(
        media_obj=media,
    )

    with pytest.raises(TransportError):
        instance.save()

    settings.ES.delete.assert_has_calls(
        (
            mock.call(index=index, id=media.identifier, refresh=True)
            for index in indexes
        ),
        # The order does not matter
        any_order=True,
    )


@pytest.mark.parametrize(
    ("media_factory", "mature_media_class", "indexes"),
    (
        (ImageFactory, MatureImage, ("image", "image-filtered")),
        (AudioFactory, MatureAudio, ("audio", "audio-filtered")),
    ),
)
def test_mature_media_updates_all_indexes(
    settings, media_factory, mature_media_class, indexes
):
    settings.ES = mock.MagicMock()
    media = media_factory.create()

    instance = mature_media_class(
        media_obj=media,
    )

    instance.save()

    settings.ES.update.assert_has_calls(
        (
            mock.call(
                index=index,
                id=media.identifier,
                body={"doc": {"mature": True}},
                refresh=True,
            )
            for index in indexes
        ),
        # The order does not matter
        any_order=True,
    )


@pytest.mark.parametrize(
    ("media_factory", "mature_media_class", "indexes"),
    (
        (ImageFactory, MatureImage, ("image", "image-filtered")),
        (AudioFactory, MatureAudio, ("audio", "audio-filtered")),
    ),
)
def test_mature_media_ignores_elasticsearch_404_errors(
    settings, media_factory, mature_media_class, indexes
):
    settings.ES = mock.MagicMock()
    error = TransportError(404, "Whoops, no document!", {})
    settings.ES.update.side_effect = [None, error]
    media = media_factory.create()

    instance = mature_media_class(
        media_obj=media,
    )

    instance.save()

    settings.ES.update.assert_has_calls(
        (
            mock.call(
                index=index,
                id=media.identifier,
                body={"doc": {"mature": True}},
                refresh=True,
            )
            for index in indexes
        ),
        # The order does not matter
        any_order=True,
    )


@pytest.mark.parametrize(
    ("media_factory", "mature_media_class", "indexes"),
    (
        (ImageFactory, MatureImage, ("image", "image-filtered")),
        (AudioFactory, MatureAudio, ("audio", "audio-filtered")),
    ),
)
def test_mature_media_reraises_elasticsearch_400_errors(
    settings, media_factory, mature_media_class, indexes
):
    settings.ES = mock.MagicMock()
    error = TransportError(400, "Terrible request, no thanks.", {})
    settings.ES.update.side_effect = [None, error]
    media = media_factory.create()

    instance = mature_media_class(
        media_obj=media,
    )

    with pytest.raises(TransportError):
        instance.save()

    settings.ES.update.assert_has_calls(
        (
            mock.call(
                index=index,
                id=media.identifier,
                body={"doc": {"mature": True}},
                refresh=True,
            )
            for index in indexes
        ),
        # The order does not matter
        any_order=True,
    )
