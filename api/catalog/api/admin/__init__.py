from django.contrib import admin

from catalog.api.admin.site import openverse_admin
from catalog.api.models import PENDING, AudioReport, ContentProvider, ImageReport
from catalog.api.models.media import AbstractDeletedMedia, AbstractMatureMedia


admin.site = openverse_admin
admin.sites.site = openverse_admin


class MediaReportAdmin(admin.ModelAdmin):
    list_display = ("reason", "status", "description", "created_at")
    media_specific_list_display = ()
    list_filter = ("status", "reason")
    list_display_links = ("status",)
    search_fields = ("description", "identifier")
    actions = None

    def get_list_display(self, request):
        return self.list_display + self.media_specific_list_display

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return []
        always_readonly = [
            "reason",
            "description",
            "identifier",
            "created_at",
        ]
        if obj.status == PENDING:
            return always_readonly
        else:
            status_readonly = ["status"]
            status_readonly.extend(always_readonly)
            return status_readonly


@admin.register(ImageReport)
class ImageReportAdmin(MediaReportAdmin):
    media_specific_list_display = ("image_url",)


@admin.register(AudioReport)
class AudioReportAdmin(MediaReportAdmin):
    media_specific_list_display = ("audio_url",)


class MediaSubreportAdmin(admin.ModelAdmin):
    search_fields = [
        "identifier",
    ]
    readonly_fields = [
        "identifier",
    ]

    def has_add_permission(self, *args, **kwargs):
        """Create ``_Report`` instances instead."""
        return False


for klass in [
    *AbstractMatureMedia.__subclasses__(),
    *AbstractDeletedMedia.__subclasses__(),
]:
    admin.site.register(klass, MediaSubreportAdmin)


@admin.register(ContentProvider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("provider_name", "provider_identifier", "media_type")
    search_fields = ("provider_name", "provider_identifier")
    exclude = ("notes",)
