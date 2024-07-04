from typing import Protocol

from django.db import models

from api.constants.media_types import MediaType


class OpenLedgerModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __iter__(self):
        for field_name in self._meta.get_fields():
            value = getattr(self, field_name, None)
            yield field_name, value


class OpenverseMediaModel(Protocol):
    media_type: MediaType


class MediaRelatedBase(models.base.ModelBase):
    """
    Metaclass for models related to any media type, for each each media type has its own subclass.

    The metaclass ensures media types use the same names to refer to related models
    of the same kind. Django will not inherit properties from parent the ``Meta``
    of model base classes. As such, this class implements a "related_name" specific
    inheritance via base classes' ``Meta``.

    Additionally, it ensures base classes define the media class they are related to
    and that the media class has a back reference to the related model. The method
    used ensures all media classes have identical properties with which to reference
    shared related models.
    """

    def _handle_abstract(cls, name, bases, attrs, related_name: str | None, **kwargs):
        if not related_name:
            raise TypeError(
                f"{name} missing 1 required keyword-only argument: 'related_name'"
            )

        setattr(attrs["Meta"], "default_related_name", related_name)

        return super().__new__(cls, name, bases, attrs, **kwargs)

    def _handle_final(cls, name, bases, attrs, **kwargs):
        if "media_class" not in attrs:
            raise TypeError(f"{name} missing required attribute: 'media_class'")

        media_class = attrs["media_class"]

        default_related_name = None
        for base in bases:
            if not hasattr(base, "Meta"):
                continue

            default_related_name = getattr(base.Meta, "default_related_name", None)
            if not default_related_name:
                continue

            if "Meta" not in attrs:
                attrs["Meta"] = type(
                    "Meta", (), {"default_related_name": default_related_name}
                )
            else:
                setattr(attrs["Meta"], "default_related_name", default_related_name)

        if default_related_name is None:
            raise NotImplementedError(
                f"Media-related model {name} is not abstract, but has no base class that "
                "defines 'default_related_name'. Did you mean to mark this model abstract?"
            )

        new_model = super().__new__(cls, name, bases, attrs, **kwargs)

        setattr(media_class, f"{default_related_name}_class", new_model)

        return new_model

    def __new__(cls, name, bases, attrs, *, related_name: str | None = None, **kwargs):
        if "Meta" in attrs and getattr(attrs["Meta"], "abstract", False):
            # Abstract models are models with a ``Meta`` defined with ``abstract = True``
            return cls._handle_abstract(cls, name, bases, attrs, related_name, **kwargs)
        else:
            return cls._handle_final(cls, name, bases, attrs, **kwargs)
