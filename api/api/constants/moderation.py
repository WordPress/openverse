from django.db import models


class DecisionAction(models.TextChoices):
    """
    This enumeration represents the actions that can be taken by a moderator as
    a part of a moderation decision.
    """

    MARKED_SENSITIVE = "mark", "Marked sensitive"

    DEINDEXED_COPYRIGHT = "deidx_copyright", "Deindexed (copyright)"
    DEINDEXED_SENSITIVE = "deidx_sensitive", "Deindexed (sensitive)"

    REJECTED_REPORTS = "rej", "Rejected"
    DEDUPLICATED_REPORTS = "dedup", "De-duplicated"

    REVERSED_MARK_SENSITIVE = "rev_mark", "Reversed deindex"
    REVERSED_DEINDEX = "rev_deidx", "Reversed mark sensitive"

    @property
    def is_reversal(self):
        return self in [self.REVERSED_DEINDEX, self.REVERSED_MARK_SENSITIVE]
