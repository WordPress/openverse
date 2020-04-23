from django.contrib import admin
from cccatalog.api.models import ImageReport

@admin.register(ImageReport)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('reason', 'identifier', 'description')
