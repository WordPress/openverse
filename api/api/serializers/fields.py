import re

from django.conf import settings
from rest_framework import serializers

from api.utils.help_text import make_comma_separated_help_text


class SchemableHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    """
    This field returns the link but allows the option to replace the URL scheme.

    This is useful when the API runs on ``http`` behind a proxy that serves ``https``.
    In these cases, the scheme in hyperlinks must be forced to ``https``.
    """

    def __init__(self, scheme=settings.API_LINK_SCHEME, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scheme = scheme

    def get_url(self, *args, **kwargs):
        url = super().get_url(*args, **kwargs)

        # Only rewrite URLs if a fixed scheme is provided
        if self.scheme is not None:
            url = re.sub(r"^\w+://", f"{self.scheme}://", url, 1)

        return url


class EnumCharField(serializers.CharField):
    """This field extends the ``CharField`` to add enum validation."""

    default_error_messages = serializers.CharField.default_error_messages | {
        "outside_enum": "Invalid value: {given}. Allowed values: {allowed}"
    }

    def __init__(self, plural: str, enum_class: set[str], **kwargs):
        kwargs["help_text"] = make_comma_separated_help_text(enum_class, plural)
        super().__init__(**kwargs)

        self.enum_class = enum_class

    def _validate_enum(self, given_value: str):
        """
        Validate whether the given values are all members of the given enum.

        :param given_value: the comma separated list received in the input
        :return: the lower cased form of the input, if the input is valid
        :raise: ``ValidationError``, if the input is invalid
        """

        lower = given_value.lower()
        input_values = lower.split(",")
        for value in input_values:
            if value not in self.enum_class:
                self.fail("outside_enum", given=value, allowed=self.enum_class)
        return lower

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        self._validate_enum(data)
        return data
