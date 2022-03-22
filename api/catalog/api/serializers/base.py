import re

from django.conf import settings
from rest_framework import serializers


class SchemableHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    """
    This field returns the link but allows the option to replace the URL scheme.
    """

    def __init__(self, scheme=settings.API_LINK_SCHEME, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scheme = scheme

    def get_url(self, *args, **kwargs):
        url = super().get_url(*args, **kwargs)
        return re.sub(r"^\w+://", f"{self.scheme}://", url, 1)
