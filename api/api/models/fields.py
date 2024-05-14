from django import forms
from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _


class URLTextField(models.TextField):
    """URL field which uses the underlying Postgres TEXT column type."""

    default_validators = [validators.URLValidator()]
    description = _("URL")

    def formfield(self, **kwargs):
        # As with CharField, this will cause URL validation to be performed
        # twice.
        return super().formfield(
            **{
                "form_class": forms.URLField,
                **kwargs,
            }
        )
