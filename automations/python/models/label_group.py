class LabelGroup:
    """
    Represents a group of labels.

    A group has some fixed parameters:
    - name, which may be prefixed to all child label names
    - color, which acts as a fallback for child labels that do not specify one
    - emoji, which acts as a fallback for child labels that do not specify one
    - is_prefixed, which determines if group name is prefixed on child labels
    - is_required, which determines if >=1 sub-label must be applied on issues
    """

    def __init__(
        self,
        color=None,
        emoji=None,
        is_prefixed=True,
        is_required=False,
        **kwargs,
    ):
        self.name = kwargs["name"]
        self.color = color
        self.emoji = emoji
        self.is_prefixed = is_prefixed
        self.is_required = is_required

        self.labels = []  # This may or may not be populated, do not rely

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Group '{self}'>"
