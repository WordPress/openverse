from django.db import models


class OpenLedgerModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __iter__(self):
        for field_name in self._meta.get_fields():
            value = getattr(self, field_name, None)
            yield field_name, value
