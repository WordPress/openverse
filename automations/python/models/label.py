from shared.data import get_data

from models.label_group import LabelGroup


class Label:

    """
    Represents a single label.

    A label is defined by four parameters:
    - name, which appears on the label
    - description, which describes it in a little more detail
    - emoji, which is a pictorial representation of the purpose of the label
    - color, which is used as a background on the label element
    A ``Label`` instance is associated to a ``Group`` instance by a many to one
    relationship.
    """

    def __init__(
        self,
        group: LabelGroup = None,
        color: str = None,
        has_emoji_name: bool = True,
        **kwargs,
    ):
        self.group = group
        self.name = kwargs["name"]
        self.description = kwargs["description"]
        self.emoji = kwargs.get("emoji")
        self.own_color = color
        self.has_emoji_name = has_emoji_name

        if group:
            if self not in group.labels:
                group.labels.append(self)
            if self.emoji is None:
                self.emoji = group.emoji

    @property
    def color(self) -> str:
        """
        Get the hex code (sans '#') to use on the emoji label.

        Labels can have their color specified as a constant and if
        missing inherit color from the parent group. If not resolved,
        the color defaults to pure black.

        :return: the 6-digit hexadecimal code of the background color
        """

        colors = get_data("labels.yml")["colors"]

        color = self.own_color
        if color is None and self.group is not None:
            color = self.group.color
        if color is None:
            color = colors["BLACK"]
        elif color in colors:
            color = colors[color]
        return color

    @property
    def qualified_name(self) -> str:
        """
        Get the fully qualified name of the label.

        Most label groups prefix the group name to the name
        of the label, separated by a colon, as indicated by the
        ``is_prefixed`` attribute on the associated ``Group`` instance.

        :return: the fully qualified name of the label
        """

        name = self.name
        if self.group and self.group.is_prefixed:
            name = f"{self.group}: {name}"
        if self.has_emoji_name:
            name = f"{self.emoji} {name}"
        return name

    @property
    def emojified_description(self) -> str:
        """
        Get the label description with emoji prefix.

        TODO: Use this when GitHub supports Unicode in label descriptions
        Get the description of the label prefixed with the emoji.

        :return: the emoji-prefixed description
        """

        return f"{self.emoji} {self.description}"

    @property
    def api_arguments(self) -> dict[str, str]:
        """
        Get label creation API parameters.

        The API only accepts ``name``, ``color`` and ``description``.

        :return: the API arguments as a dictionary
        """

        return {
            "name": self.qualified_name,
            "color": self.color,
            "description": self.description,
        }

    def __eq__(self, remote: "Label") -> bool:
        """
        Compare ``self`` with PyGithub label object.

        :param remote: the PyGithub label instance to compare itself against
        :return: whether the instance is equal to its remote counterpart
        """

        return all(
            [
                self.qualified_name == remote.name,
                self.color == remote.color,
                self.description == remote.description,
            ]
        )

    def __ne__(self, remote: "Label") -> bool:
        """
        Compare ``self`` with PyGithub label object.

        :param remote: the PyGithub label instance to compare itself against
        :return: whether the instance is unequal to its remote counterpart
        """

        return any(
            [
                self.qualified_name != remote.name,
                self.color != remote.color,
                self.description != remote.description,
            ]
        )

    def __str__(self) -> str:
        return self.qualified_name

    def __repr__(self) -> str:
        return f"<Label '{self}'>"
