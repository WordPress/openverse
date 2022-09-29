import uuid
from typing import Literal, Union
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError

import pytest

from catalog.api.models import (
    Audio,
    AudioReport,
    DeletedAudio,
    DeletedImage,
    Image,
    ImageReport,
    MatureAudio,
    MatureImage,
)
from catalog.api.models.media import (
    DEINDEXED,
    DMCA,
    MATURE,
    MATURE_FILTERED,
    OTHER,
    PENDING,
)


pytestmark = pytest.mark.django_db

MediaType = Union[Literal["audio"], Literal["image"]]

reason_params = pytest.mark.parametrize("reason", [DMCA, MATURE, OTHER])


@pytest.fixture
def media_obj():
    def _get_media_obj(type: MediaType):
        klass = {
            "audio": Audio,
            "image": Image,
        }.get(type)
        identifier = uuid.uuid4()
        obj = klass(identifier=identifier)
        obj.save()
        return obj

    return _get_media_obj


@pytest.mark.parametrize(
    "media_type, report_class", [("image", ImageReport), ("audio", AudioReport)]
)
@reason_params
def test_cannot_report_invalid_identifier(media_type, report_class, reason):
    with pytest.raises(ValidationError):
        report_class.objects.create(
            identifier=uuid.uuid4(),
            reason=reason,
        )


@pytest.mark.parametrize(
    "media_type, report_class, mature_class, deleted_class",
    [
        ("image", ImageReport, MatureImage, DeletedImage),
        ("audio", AudioReport, MatureAudio, DeletedAudio),
    ],
)
@reason_params
def test_pending_reports_have_no_subreport_models(
    media_type: MediaType, report_class, mature_class, deleted_class, reason, media_obj
):
    media = media_obj(media_type)
    report = report_class.objects.create(
        identifier=media.identifier,
        reason=reason,
    )

    assert report.status == PENDING
    assert not mature_class.objects.filter(identifier=media.identifier).exists()
    assert not deleted_class.objects.filter(identifier=media.identifier).exists()


@pytest.mark.parametrize(
    "media_type, report_class, mature_class",
    [("image", ImageReport, MatureImage), ("audio", AudioReport, MatureAudio)],
)
def test_mature_filtering_creates_mature_image_instance(
    media_type: MediaType, report_class, mature_class, media_obj
):
    media = media_obj(media_type)
    mock_es = MagicMock()
    with patch("django.conf.settings.ES", mock_es):
        report_class.objects.create(
            identifier=media.identifier, reason=MATURE, status=MATURE_FILTERED
        )

    assert mature_class.objects.filter(identifier=media.identifier).exists()
    assert mock_es.update.called_with(
        index=media_type, id=media.id, body={"doc": {"mature": True}}
    )
    assert media.mature


@pytest.mark.parametrize(
    "media_type, report_class, mature_class",
    [("image", ImageReport, MatureImage), ("audio", AudioReport, MatureAudio)],
)
def test_deleting_mature_image_instance_resets_mature_flag(
    media_type: MediaType, report_class, mature_class, media_obj
):
    media = media_obj(media_type)
    mock_es = MagicMock()
    with patch("django.conf.settings.ES", mock_es):
        # Mark as mature.
        report_class.objects.create(
            identifier=media.identifier, reason=MATURE, status=MATURE_FILTERED
        )
        # Delete ``MatureImage`` instance.
        mature_class.objects.get(identifier=media.identifier).delete()

    assert mock_es.update.call_count == 2
    assert mock_es.update.called_with(id=media.id, body={"doc": {"mature": False}})
    assert not media.mature


@pytest.mark.parametrize(
    "media_type, media_class, report_class, deleted_class",
    [
        ("image", Image, ImageReport, DeletedImage),
        ("audio", Audio, AudioReport, DeletedAudio),
    ],
)
def test_deindexing_creates_deleted_image_instance(
    media_type: MediaType, media_class, report_class, deleted_class, media_obj
):
    media = media_obj(media_type)
    # Extracting field values because ``media`` will be deleted.
    image_id = media.id
    identifier = media.identifier

    mock_es = MagicMock()
    with patch("django.conf.settings.ES", mock_es):
        report_class.objects.create(
            identifier=identifier, reason=DMCA, status=DEINDEXED
        )

    assert deleted_class.objects.filter(identifier=identifier).exists()
    assert not media_class.objects.filter(identifier=identifier).exists()
    assert mock_es.delete.called_with(id=image_id)
