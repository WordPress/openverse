import uuid

from django.core.exceptions import ValidationError

import pook
import pytest
from elasticsearch import BadRequestError, NotFoundError

from api.models import DeletedAudio, DeletedImage, SensitiveAudio, SensitiveImage
from api.models.media import (
    DEINDEXED,
    DMCA,
    MATURE,
    MATURE_FILTERED,
    OTHER,
    PENDING,
    AbstractDeletedMedia,
    AbstractSensitiveMedia,
)


pytestmark = pytest.mark.django_db

reason_params = pytest.mark.parametrize("reason", [DMCA, MATURE, OTHER])


@reason_params
def test_cannot_report_invalid_identifier(media_type_config, reason):
    with pytest.raises(ValidationError):
        media_type_config.report_factory.create(
            media_obj_id=uuid.uuid4(),
            reason=reason,
        )


@reason_params
def test_pending_reports_have_no_subreport_models(
    media_type_config,
    reason,
):
    media = media_type_config.model_factory.create()
    report = media_type_config.report_factory.create(media_obj=media, reason=reason)

    assert report.status == PENDING
    assert not media_type_config.sensitive_class.objects.filter(
        media_obj=media
    ).exists()
    assert not media_type_config.deleted_class.objects.filter(media_obj=media).exists()


@pytest.mark.skip("This needs to be updated based on new moderation flow")
def test_mature_filtering_creates_sensitive_media_instance(media_type_config, settings):
    media = media_type_config.model_factory.create()

    media_type_config.report_factory.create(
        media_obj=media, reason=MATURE, status=MATURE_FILTERED
    )

    assert media_type_config.sensitive_class.objects.filter(media_obj=media).exists()

    for index in media_type_config.indexes:
        doc = settings.ES.get(
            index=index,
            id=media.pk,
            # get defaults to "realtime", meaning it ignores refreshes
            # disable it here to implicitly test that the index was refreshed
            # when the document was updated
            realtime=False,
        )
        assert doc["found"]
        assert doc["_source"]["mature"]

    assert media.sensitive


@pytest.mark.skip("This needs to be updated based on new moderation flow")
def test_deleting_sensitive_media_instance_resets_mature_flag(
    media_type_config, settings
):
    media = media_type_config.model_factory.create()
    # Mark as mature.
    media_type_config.report_factory.create(
        media_obj=media, reason=MATURE, status=MATURE_FILTERED
    )
    # Delete sensitive instance.
    media_type_config.sensitive_class.objects.get(media_obj=media).delete()

    # Assert the media are back to mature=False
    # The previous test asserts they get set to mature=True
    # in the first place, so it's not necessary to add those
    # assertions here
    for index in media_type_config.indexes:
        doc = settings.ES.get(
            index=index,
            id=media.pk,
            # get defaults to "realtime", meaning it ignores refreshes
            # disable it here to implicitly test that the index was refreshed
            # when the document was updated
            realtime=False,
        )
        assert doc["found"]
        assert not doc["_source"]["mature"]

    media.refresh_from_db()
    assert not media.sensitive


@pytest.mark.skip("This needs to be updated based on new moderation flow")
def test_deindexing_creates_deleted_media_instance(media_type_config, settings):
    media = media_type_config.model_factory.create()
    # Extracting field values because ``media`` will be deleted.
    image_id = media.id
    identifier = media.identifier

    media_type_config.report_factory.create(
        media_obj=media, reason=DMCA, status=DEINDEXED
    )

    assert media_type_config.deleted_class.objects.filter(media_obj=media).exists()
    assert not media_type_config.model_class.objects.filter(
        identifier=identifier
    ).exists()

    for index in media_type_config.indexes:
        with pytest.raises(NotFoundError):
            settings.ES.get(
                index=index,
                id=image_id,
                # get defaults to "realtime", meaning it ignores refreshes
                # disable it here to implicitly test that the index was refreshed
                # when the document was updated
                realtime=False,
            )


def test_all_deleted_media_covered():
    """
    Imperfect test to ensure all subclasses are covered by the tests
    in this module. Relies on all models being present in
    ``catalog.api.models`` (i.e., exported from `__init__`).
    """
    assert set(AbstractDeletedMedia.__subclasses__()) == {DeletedAudio, DeletedImage}


def test_all_sensitive_media_covered():
    """
    Imperfect test to ensure all subclasses are covered by the tests
    in this module. Relies on all models being present in
    ``catalog.api.models`` (i.e., exported from `__init__`).
    """
    assert set(AbstractSensitiveMedia.__subclasses__()) == {
        SensitiveAudio,
        SensitiveImage,
    }


def test_deleted_media_deletes_from_all_indexes(
    media_type_config,
    settings,
):
    media = media_type_config.model_factory.create()
    # Need to retrieve this here because the creation of the
    # deleted media class below will delete this object, rendering
    # the pk empty by the time we assert the calls
    media_id = media.pk

    instance = media_type_config.deleted_class(
        media_obj=media,
    )

    instance.save()

    for index in media_type_config.indexes:
        with pytest.raises(NotFoundError):
            settings.ES.get(
                index=index,
                id=media_id,
                realtime=False,
            )


@pook.on
def test_deleted_media_ignores_elasticsearch_404_errors(settings, media_type_config):
    media = media_type_config.model_factory.create()

    es_mocks = []
    for index in media_type_config.indexes:
        es_mocks.append(
            pook.delete(settings.ES_ENDPOINT)
            .path(f"/{index}/_doc/{media.pk}")
            .param("refresh", "true")
            .reply(404)
            .mock
        )

    # This should succeed despite the 404s forced above
    media_type_config.deleted_class.objects.create(
        media_obj=media,
    )

    for mock in es_mocks:
        assert mock.matched, f"{repr(mock.matchers)} did not match!"


@pook.on
def test_deleted_media_raises_elasticsearch_400_errors(settings, media_type_config):
    media = media_type_config.model_factory.create()

    es_mocks: list[pook.Mock] = []
    for index in media_type_config.indexes:
        es_mocks.append(
            pook.delete(settings.ES_ENDPOINT)
            .path(f"/{index}/_doc/{media.pk}")
            .param("refresh", "true")
            .reply(400)
            .mock
        )

    with pytest.raises(BadRequestError):
        media_type_config.deleted_class.objects.create(
            media_obj=media,
        )

    # Because we're causing a 400, and because that re-raises
    # in the update, only one of the requests ever gets sent
    # Therefore, one should remain pending and at least one
    # should have matched
    # Take this approach to avoid being concerned with the
    # order of the requests, which doesn't matter
    assert len([m for m in es_mocks if m.matched]) == 1


@pook.on
def test_sensitive_media_ignores_elasticsearch_404_errors(
    settings,
    media_type_config,
):
    media = media_type_config.model_factory.create()

    es_mocks = []
    for index in media_type_config.indexes:
        es_mocks.append(
            pook.post(settings.ES_ENDPOINT)
            .path(f"/{index}/_update/{media.pk}")
            .param("refresh", "true")
            .reply(404)
            .mock
        )

    # This should pass despite the 404 enforced above
    media_type_config.sensitive_factory.create(
        media_obj=media,
    )

    for mock in es_mocks:
        assert mock.matched, f"{repr(mock.matchers)} did not match!"


@pook.on
def test_sensitive_media_reraises_elasticsearch_400_errors(settings, media_type_config):
    media = media_type_config.model_factory.create()

    es_mocks = []
    for index in media_type_config.indexes:
        es_mocks.append(
            pook.post(settings.ES_ENDPOINT)
            .path(f"/{index}/_update/{media.pk}")
            .param("refresh", "true")
            .reply(400)
            .mock
        )

    # This should fail due to the 400 enforced above
    with pytest.raises(BadRequestError):
        media_type_config.sensitive_factory.create(
            media_obj=media,
        )

    # Because we're causing a 400, and because that re-raises
    # in the update, only one of the requests ever gets sent
    # Therefore, one should remain pending and at least one
    # should have matched
    # Take this approach to avoid being concerned with the
    # order of the requests, which doesn't matter
    assert len([m for m in es_mocks if m.matched]) == 1
