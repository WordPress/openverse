from typing import Literal

import structlog

from api.constants.moderation import DecisionAction
from api.models.audio import (
    Audio,
    AudioDecision,
    AudioDecisionThrough,
    DeletedAudio,
    SensitiveAudio,
)
from api.models.image import (
    DeletedImage,
    Image,
    ImageDecision,
    ImageDecisionThrough,
    SensitiveImage,
)
from api.models.media import AbstractDeletedMedia, AbstractMedia, AbstractSensitiveMedia


logger = structlog.get_logger(__name__)


def perform_moderation(
    request,
    media_type: Literal["audio", "image"],
    mod_objects: list[
        type[AbstractSensitiveMedia] | type[AbstractDeletedMedia] | type[AbstractMedia]
    ],
    action: DecisionAction,
):
    """
    Perform bulk moderation on the given models.

    If the decision action is forward, ``mod_objects`` is a queryset of
    ``Media`` items. We can get the UUIDs from the ``identifier`` field.

    If the decision action is reverse, ``mod_objects`` is a queryset of
    ``SensitiveMedia`` or ``DeletedMedia`` items. We can get the UUIDs
    from the ``media_obj_id`` field.

    Note that bulk moderation will not resolve any open reports. It is
    up to the moderator to manually link open reports with the
    appropriate decisions and resolve them.

    :param request: the request used to determine the moderator
    :param media_type: the type of media being bulk-moderated
    :param mod_objects: a ``QuerySet`` of media items to bulk-moderate
    :para action: the action of the bulk moderation decision
    """

    match media_type:
        case "audio":
            Media = Audio
            SensitiveMedia = SensitiveAudio
            DeletedMedia = DeletedAudio
            MediaDecision = AudioDecision
            MediaDecisionThrough = AudioDecisionThrough
        case "image":
            Media = Image
            SensitiveMedia = SensitiveImage
            DeletedMedia = DeletedImage
            MediaDecision = ImageDecision
            MediaDecisionThrough = ImageDecisionThrough

    # The following block uses ``list`` to force evaluation of the
    # queryset and store the values because calling ``delete`` below
    # will otherwise make the querysets evaluate differently.
    if action.is_reverse:
        identifiers = list(mod_objects.values_list("media_obj_id", flat=True))
    else:
        identifiers = list(mod_objects.values_list("identifier", flat=True))

    logger.info(
        "Performing bulk moderation action.",
        action=action,
        model=mod_objects.model._meta.label,
        identifiers=identifiers,
    )

    match action:
        case DecisionAction.MARKED_SENSITIVE:
            created = SensitiveMedia.objects.bulk_create(
                [SensitiveMedia(media_obj_id=identifier) for identifier in identifiers]
            )
            logger.debug(f"Created sensitive-{media_type} items.", count=len(created))
            SensitiveMedia.bulk_perform_action(True, mod_objects)

        case DecisionAction.DEINDEXED_COPYRIGHT | DecisionAction.DEINDEXED_SENSITIVE:
            created = DeletedMedia.objects.bulk_create(
                [DeletedMedia(media_obj_id=identifier) for identifier in identifiers]
            )
            logger.debug(f"Created deleted-{media_type} items.", count=len(created))
            DeletedMedia.bulk_perform_action(mod_objects)

        case DecisionAction.REVERSED_MARK_SENSITIVE:
            media_items = Media.objects.filter(identifier__in=identifiers)
            SensitiveMedia.bulk_perform_action(False, media_items)
            logger.debug(
                f"Unmarked {media_type} items as sensitive.",
                identifier_count=len(identifiers),
                media_item_count=len(media_items),
            )

            count, _ = mod_objects.delete()
            logger.debug(f"Deleted sensitive-{media_type} items.", count=count)

        case DecisionAction.REVERSED_DEINDEX:
            # There is no bulk action for reversed-deindex. The media
            # item will eventually be reindexed through data refresh.
            count, _ = mod_objects.delete()
            logger.debug(f"Deleted deleted-{media_type} items.", count=count)

    media_decision = MediaDecision.objects.create(
        action=action,
        moderator=request.user,
        notes=request.POST.get("notes"),
    )
    logger.debug(
        "Decision created",
        decision=media_decision.id,
        action=media_decision.action,
        notes=media_decision.notes,
        moderator=media_decision.moderator.get_username(),
    )

    created = MediaDecisionThrough.objects.bulk_create(
        [
            MediaDecisionThrough(decision_id=media_decision.id, media_obj_id=identifier)
            for identifier in identifiers
        ]
    )
    logger.debug(f"Created {media_type}-decision-through items.", count=len(created))

    return media_decision
