from django.contrib import admin

from api.admin.media_report import register as register_media_report
from api.admin.oauth import register as register_oauth
from api.admin.site import openverse_admin
from api.admin.user import register as register_user
from api.models.models import ContentSource


admin.site = openverse_admin
admin.sites.site = openverse_admin

for register in [register_media_report, register_oauth, register_user]:
    register(admin.site)


@admin.register(ContentSource)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("source_name", "source_identifier", "media_type")
    search_fields = ("source_name", "source_identifier")
    ordering = ("media_type", "source_name")
