from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    """Extends model serializer to use docstring of properties as help text."""

    def build_property_field(self, field_name, model_class):
        """
        Use docstrings as the Swagger help text for fields.

        This is accomplished by overriding the built-in property field builder.

        :param field_name: the name of the property for which the field is being built
        :param model_class: the ``class`` instance for the Django model
        :return: the Field subclass to use and the keyword arguments to pass to it
        """

        klass, kwargs = super().build_property_field(field_name, model_class)
        if doc := getattr(model_class, field_name).__doc__:
            kwargs.setdefault("help_text", doc)
        return klass, kwargs
