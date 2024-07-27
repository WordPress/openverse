from unittest.mock import patch

from django.test import RequestFactory

import pytest

from api.constants.moderation import DecisionAction
from api.models.media import AbstractDeletedMedia, AbstractSensitiveMedia
from api.utils.moderation import perform_moderation
from test.factory.models.oauth2 import UserFactory


pytestmark = pytest.mark.django_db


@pytest.fixture
def mod_request():
    notes = "bulk moderation"

    request = RequestFactory().post("/", {"notes": notes})

    moderator = UserFactory.create(is_moderator=True)
    request.user = moderator

    return moderator, request, notes


@pytest.mark.parametrize(
    "prefix, action",
    [
        ("sensitive", DecisionAction.MARKED_SENSITIVE),
        ("deleted", DecisionAction.DEINDEXED_SENSITIVE),
        ("deleted", DecisionAction.DEINDEXED_COPYRIGHT),
    ],
)
def test_perform_moderation_creates_decision_and_through_models_for_forward_actions(
    prefix,
    action,
    media_type_config,
    mod_request,
):
    media_count = 2
    uuids = [
        media_type_config.model_factory.create().identifier for _ in range(media_count)
    ]
    # ``QuerySet`` of ``AbstractMedia`` subclass
    qs = media_type_config.model_class.objects.filter(identifier__in=uuids)

    moderator, request, notes = mod_request
    dec = perform_moderation(request, media_type_config.media_type, qs, action)

    # Verify that the sensitive/deleted models were created.
    assert (
        getattr(media_type_config, f"{prefix}_class")
        .objects.filter(media_obj_id__in=uuids)
        .count()
        == media_count
    )

    # Verify decision attributes.
    assert dec.moderator == moderator
    assert dec.notes == notes
    assert dec.action == action

    # Verify that number of through models equals number of media items.
    assert (
        getattr(dec, f"{media_type_config.media_type}decisionthrough_set").count()
        == media_count
    )


@patch.object(AbstractSensitiveMedia, "_bulk_update_es")
def test_perform_moderation_handles_marked_sensitive(
    mock,
    media_type_config,
    mod_request,
):
    media_count = 2
    uuids = [
        media_type_config.model_factory.create().identifier for _ in range(media_count)
    ]
    # ``QuerySet`` of ``AbstractMedia`` subclass
    qs = media_type_config.model_class.objects.filter(identifier__in=uuids)

    request = mod_request[1]
    action = DecisionAction.MARKED_SENSITIVE
    perform_moderation(request, media_type_config.media_type, qs, action)

    # Verify that media items are now marked sensitive.
    for uuid in uuids:
        assert media_type_config.model_class.objects.get(identifier=uuid).sensitive
    # Verify that documents have been updated in ES.
    assert mock.called


@patch.object(AbstractDeletedMedia, "_bulk_update_es")
@pytest.mark.parametrize(
    "action",
    [DecisionAction.DEINDEXED_SENSITIVE, DecisionAction.DEINDEXED_COPYRIGHT],
)
def test_perform_moderation_handles_deindexed(
    mock,
    action,
    media_type_config,
    mod_request,
):
    media_count = 2
    uuids = [
        media_type_config.model_factory.create().identifier for _ in range(media_count)
    ]
    # ``QuerySet`` of ``AbstractMedia`` subclass
    qs = media_type_config.model_class.objects.filter(identifier__in=uuids)

    request = mod_request[1]
    perform_moderation(request, media_type_config.media_type, qs, action)

    # Verify that media items are deleted.
    assert not media_type_config.model_class.objects.filter(
        identifier__in=uuids
    ).exists()
    # Verify that documents have been deleted in ES.
    assert mock.called


@pytest.mark.parametrize(
    "prefix, action",
    [
        ("sensitive", DecisionAction.REVERSED_MARK_SENSITIVE),
        ("deleted", DecisionAction.REVERSED_DEINDEX),
    ],
)
def test_perform_moderation_creates_decision_and_through_models_for_reverse_actions(
    prefix,
    action,
    media_type_config,
    mod_request,
):
    media_count = 2
    uuids = [
        getattr(media_type_config, f"{prefix}_factory").create().media_obj_id
        for _ in range(media_count)
    ]
    # ``QuerySet`` of ``AbstractSensitiveMedia``/``AbstractDeletedMedia`` subclass
    qs = getattr(media_type_config, f"{prefix}_class").objects.filter(
        media_obj_id__in=uuids
    )

    moderator, request, notes = mod_request
    dec = perform_moderation(request, media_type_config.media_type, qs, action)

    # Verify that the sensitive/deleted models were deleted.
    assert (
        not getattr(media_type_config, f"{prefix}_class")
        .objects.filter(media_obj_id__in=uuids)
        .exists()
    )

    # Verify decision attributes.
    assert dec.moderator == moderator
    assert dec.notes == notes
    assert dec.action == action

    # Verify that number of through models equals number of media items.
    assert (
        getattr(dec, f"{media_type_config.media_type}decisionthrough_set").count()
        == media_count
    )


@patch.object(AbstractSensitiveMedia, "_bulk_update_es")
def test_perform_moderation_handles_reversed_mark_sensitive(
    mock,
    media_type_config,
    mod_request,
):
    media_count = 2
    uuids = [
        media_type_config.sensitive_factory.create().media_obj_id
        for _ in range(media_count)
    ]
    # ``QuerySet`` of ``AbstractSensitiveMedia`` subclass
    qs = media_type_config.sensitive_class.objects.filter(media_obj_id__in=uuids)

    request = mod_request[1]
    action = DecisionAction.REVERSED_MARK_SENSITIVE
    perform_moderation(request, media_type_config.media_type, qs, action)

    # Verify that media items are not marked sensitive.
    for uuid in uuids:
        assert not media_type_config.model_class.objects.get(identifier=uuid).sensitive
    # Verify that documents have been updated in ES.
    assert mock.called


@patch.object(AbstractDeletedMedia, "_bulk_update_es")
def test_perform_moderation_handles_reversed_deindex(
    mock,
    media_type_config,
    mod_request,
):
    media_count = 2
    uuids = [
        media_type_config.deleted_factory.create().media_obj_id
        for _ in range(media_count)
    ]
    # ``QuerySet`` of ``AbstractDeletedMedia`` subclass
    qs = media_type_config.deleted_class.objects.filter(media_obj_id__in=uuids)

    request = mod_request[1]
    action = DecisionAction.REVERSED_DEINDEX
    perform_moderation(request, media_type_config.media_type, qs, action)

    # Verify that media items stay deleted and are not restored.
    assert not media_type_config.model_class.objects.filter(
        identifier__in=uuids
    ).exists()
    # Verify that no ES call was made.
    assert not mock.called
